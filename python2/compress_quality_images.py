#!/usr/bin/env python

# =======================
# MODULES IMPORTS
# =======================

import os
import sys
import time
import imghdr
import shutil
import logging
import argparse
import subprocess
from PIL import Image
from zipfile import ZipFile

# =======================
# LOGGING
# =======================
logs_folder = r"/home/userfolder/logs/cronjob"
# create a directory if it does not exist
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)

log_file = os.path.join(logs_folder, "compress_quality_images.log")
logging.basicConfig(filename=log_file,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO)

# =======================
# VARIABLES
# =======================

# variable to name the compressed .zip
script_name = "-restaurant"

# Location of files to compress/delete
images_folder = r"/home/userfolder/public_html/webimages/upload/MenuItem"
# images_folder = r"C:\Users\userfolder\Downloads\home"
backup_folder = r"/home/userfolder/backup/"
# backup_folder = r"C:\Users\userfolder\Downloads\backup"

tmp_linux_folder = r"/home/un2x3c5/tmp"
# tmp_linux_folder = r"C:\Users\userfolder\Downloads\tmp"

# check if tmp folder exists
try:
    os.stat(tmp_linux_folder)
except os.error as e:
    logging.exception(e)
    sys.exit()

# Image files older than specified
image_older_days = 1
image_older_hours = 23

# minimum size allowed in Bytes
minimum_size_allowed = 89000  # ~90KB

if minimum_size_allowed < 88000:
    sys.exit()

# dictionary for image sizes
sizes = {'small': (100, 100), 'standard': (600, 600)}

# Current time
now = time.time()


def from_ago(_file, fmt_hours=False):
    # return file time in hour
    if fmt_hours:
        return (now - os.stat(_file).st_mtime) / 3600 < image_older_hours
    # return file time in day
    return (now - os.stat(_file).st_mtime) / (3600 * 24) < image_older_days


def size_greater_than(_file):
    return os.path.getsize(_file) > minimum_size_allowed


def remove_empty_zips():
    for root, _, files in os.walk(backup_folder, topdown=False):
        for _file in files:
            infile = os.path.join(root, _file)
            # remove .zip with 1K or 22 byte
            if _file.lower().endswith(".zip") and os.stat(infile).st_size < 24:
                os.remove(infile)


def select_quality(_file):
    try:
        image_filesize = os.path.getsize(_file)

        if image_filesize > 6000000:
            return 10
        elif image_filesize > 1900000:
            return 40
        elif image_filesize > 1000000:
            return 42
        elif image_filesize > 350000:
            return 65
        elif image_filesize > 90000:
            return 55
        else:
            return 60
    except os.error:
        return 65


def always_jpg(image_header):
    if image_header and image_header.lower() == "png":
        return "jpeg"
    return image_header


def is_transparent(image):
    """
    Check to see if an image is transparent.
    """
    if not isinstance(image, Image.Image):
        # Can only deal with PIL images, fall back to the assumption that that
        # it's not transparent.
        return False
    return (image.mode in ('RGBA', 'LA') or
            (image.mode == 'P' and 'transparency' in image.info))


def resize_with_aspect_ratio(im, infile, format_im='jpeg'):
    """
    maintain its aspect ratio
    """
    try:
        width, height = im.size
        width_to_apply, height_to_apply = sizes.get('standard', (600, 600))
        # applied (width_to_apply, height_to_apply) only if it is less than original image size
        if (width_to_apply, height_to_apply) < (width, height):
            # maintain ratio to width
            height_to_apply = width_to_apply * height / width
            im = im.resize((width_to_apply, height_to_apply), Image.ANTIALIAS)
        else:
            im = im.resize((width, height), Image.ANTIALIAS)
        im.save(infile, format=format_im, optimize=True, progressive=True)
    except BaseException as error:
        logging.exception(error)
        return im, False
    return im, True


def generate_thumbnail(im, dirpath, filename, format_im='jpeg'):
    try:
        width_to_apply, height_to_apply = sizes.get('small', (100, 100))
        im.thumbnail((width_to_apply, height_to_apply))
        #  save each image into separate folders according to dimensions in dictionary
        new_filename = '{0}x{1}_resized_{2}'.format(width_to_apply,
                                                    height_to_apply, filename)
        infile = os.path.join(dirpath, new_filename)
        im.save(infile, format=format_im, optimize=True, progressive=True)
    except BaseException as error:
        logging.exception(error)


def colorspace(im, no_rgba=True, bw=False, replace_alpha=False, **kwargs):
    """
    Convert images to the correct color space.
    A passive option (i.e. always processed) of this method is that all images
    (unless grayscale) are converted to RGB colorspace.
    This processor should be listed before :func:`scale_and_crop` so palette is
    changed before the image is resized.
    no_rgba
        Si la imagen es transparent (RGBA, LA, etc) la convierte a RGB
    bw
        Make the thumbnail grayscale (not really just black & white).
    replace_alpha
        Replace any transparency layer with a solid color. For example,
        ``replace_alpha='#fff'`` would replace the transparency layer with
        white.
    """
    # if im.mode == 'I':
    #    PIL (and pillow) have can't convert 16 bit grayscale images to lower
    #    modes, so manually convert them to an 8 bit grayscale.
    #    im = im.point(list(_points_table()), 'L')

    is_transp = is_transparent(im)
    is_grayscale = im.mode in ('L', 'LA')
    new_mode = im.mode
    if is_grayscale or bw:
        new_mode = 'L'
    else:
        new_mode = 'RGB'

    if no_rgba and is_transp:
        new_mode = 'RGB'
    elif is_transp:
        if replace_alpha:
            if im.mode != 'RGBA':
                im = im.convert('RGBA')
            base = Image.new('RGBA', im.size, replace_alpha)
            base.paste(im, mask=im)
            im = base
        else:
            new_mode = new_mode + 'A'

    if im.mode != new_mode:
        im = im.convert(new_mode)

    return im


def optimize(infile, _format="jpg", filesize="290k"):
    runstring = {
        "jpeg": u"jpegoptim -P -p -q --strip-all --all-progressive --size=%(fsize)s %(file)s",
        "jpg": u"jpegoptim -P -p -q --strip-all --all-progressive --size=%(fsize)s %(file)s",
        "jfif": u"jpegoptim -P -p -q --strip-all --all-progressive --size=%(fsize)s %(file)s",
    }
    if _format in runstring:
        sp = subprocess.Popen(runstring[_format] %
                              {'file': infile, 'fsize': filesize}, shell=True)
        sp.wait()


def compress_quality_images(path_src=images_folder, _resize_img="y", _optimize_jpeg="y", _generate_thumbnail="y"):
    gzip_name = "{}{}{}".format(now, script_name, '.zip')
    gzip_file = os.path.join(backup_folder, gzip_name)
    infile_tmp = ""

    # create a directory if it does not exist
    try:
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
    except OSError as error:
        logging.exception(error)
        sys.exit()

    # Create a ZipFile Object
    with ZipFile(gzip_file, 'w') as zipObj:
        # Loop through all the folder
        for dirpath, _, filenames in os.walk(path_src, topdown=False):
            for filename in filenames:
                try:
                    saved = False
                    infile = os.path.join(dirpath, filename)
                    image_header = imghdr.what(infile)

                    if from_ago(infile, True) and size_greater_than(infile) and image_header:
                        # for PNG compress
                        formatpim = always_jpg(image_header)
                        file_tmp = "tmp_{}".format(filename)
                        infile_tmp = os.path.join(tmp_linux_folder, file_tmp)
                        with Image.open(infile) as pim:
                            pim = colorspace(pim)
                            resized = False
                            # resize image
                            if _resize_img == "y":
                                pim, resized = resize_with_aspect_ratio(
                                    pim, infile_tmp, formatpim)
                            if not resized or size_greater_than(infile_tmp):
                                # check file size and optimize
                                _quality = select_quality(infile_tmp)
                                pim.save(infile_tmp, format=formatpim,
                                         optimize=True, progressive=True, quality=_quality)
                            # thumbnail
                            if _generate_thumbnail == "y":
                                generate_thumbnail(pim, dirpath, filename, formatpim)

                            saved = True

                        if _optimize_jpeg == "y" and os.stat(infile_tmp).st_size > 70000:
                            optimize(infile_tmp, image_header, '70k')

                        if saved:
                            # Add file to the zip
                            zipObj.write(infile)

                            # Move src to dst. (mv src dst)
                            shutil.move(infile_tmp, infile)
                except OSError as error:
                    logging.exception('%s raised an os error', error)
                # Problem compress the image
                except IOError as error:
                    logging.exception('%s raised an exception', error)
                    if os.path.exists(infile_tmp):
                        os.remove(infile_tmp)
                except BaseException as error:
                    logging.exception('%s raised an exception--', error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='compress images using PIL library')
    parser.add_argument('-src', nargs='?',
                        type=str, help='an path', default=images_folder)
    parser.add_argument('-resize', nargs='?',
                        type=str, choices=("y", "n"), help='resize maintain ratio, is "y" by default', default="y")
    parser.add_argument('-thumbnail', nargs='?',
                        type=str, choices=("y", "n"), help='make image into a thumbnail', default="y")
    parser.add_argument('-jpegoptim', nargs='?',
                        type=str, choices=("y", "n"), help='run the jpegoptim binary, is "y" by default', default="y")
    args = parser.parse_args()

    if args.src:
        logging.info('run script en %s', args.src)
        # script_name is global variable
        script_name = "-{}".format(os.path.basename(args.src)).lower()
    else:
        logging.info('run script en %s', images_folder)

    compress_quality_images(args.src, _resize_img=args.resize, _optimize_jpeg=args.jpegoptim,
                            _generate_thumbnail=args.thumbnail)
    remove_empty_zips()
