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
logs_folder = r"/home/un2x3c5/logs/cronjob"
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
scriptname = "-restaurant"

# Location of files to compress/delete
images_folder = r"/home/un2x3c5/public_html/webimages/upload/MenuItem"
# images_folder = r"C:\Users\zoro\Downloads\home"
backup_folder = r"/home/un2x3c5/un2x3.com/public_ftp/"
# backup_folder = r"C:\Users\zoro\Downloads\backup"

tmp_linux_folder = r"/home/un2x3c5/tmp"
# tmp_linux_folder = r"C:\Users\zoro\Downloads\tmp"

# Image files older than specified
image_older_days = 1
image_older_hours = 23

# minimum size allowed in Bytes
minimum_size_allowed = 280000  # ~600KB

# en un futuro preparar select_quality() para tamanos mas pequenos
if minimum_size_allowed < 240000:
    sys.exit()

# Current time
now = time.time()


def from_ago(_file, fmt_hours=False):
    # retorna el tiempo de los ficheros en horas
    if fmt_hours:
        return (now - os.stat(_file).st_mtime) / 3600 < image_older_hours
    # retorna el tiempo de los ficheros en dias
    return (now - os.stat(_file).st_mtime) / (3600*24) < image_older_days


def size_greater_than(_file):
    return os.path.getsize(_file) > minimum_size_allowed


def select_quality(_file):
    try:
        image_size = os.path.getsize(_file)

        if image_size > 6000000:
            return 10
        elif image_size > 4000000:
            return 40
        elif image_size > 1900000:
            return 58
        elif image_size > 1000000:
            return 42
        elif image_size > 800000:
            return 65
        elif image_size > 350000:
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


def optimize(infile, _format="jpg"):
    runstring = {
        "jpeg": u"jpegoptim -P -p -q --strip-all --all-progressive --size=290k %(file)s",
        "jpg": u"jpegoptim -P -p -q --strip-all --all-progressive --size=290k %(file)s",
        "jfif": u"jpegoptim -P -p -q --strip-all --all-progressive --size=290k %(file)s",
    }
    if _format in runstring:
        sp = subprocess.Popen(runstring[_format] %
                              {'file': infile}, shell=True)
        sp.wait()


def compress_quality_images(path_src=images_folder):
    gzipname = "{}{}{}".format(now, scriptname, '.zip')
    gzipfile = os.path.join(backup_folder, gzipname)

    # check in tmp folder
    if not os.path.exists(tmp_linux_folder):
        return
    # create a directory if it does not exist
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    # Create a ZipFile Object
    with ZipFile(gzipfile, 'w') as zipObj:
        # Loop through all the folder
        for root, _, files in os.walk(path_src, topdown=False):
            for _file in files:
                try:
                    saved = False
                    infile = os.path.join(root, _file)
                    image_header = imghdr.what(infile)

                    if from_ago(infile, True) and size_greater_than(infile) and image_header:
                        # for PNG compress
                        formatpim = always_jpg(image_header)
                        file_tmp = "tmp_{}".format(_file)
                        infile_tmp = os.path.join(tmp_linux_folder, file_tmp)
                        _quality = select_quality(infile)
                        with Image.open(infile) as pim:
                            pim = colorspace(pim)
                            pim.save(infile_tmp, format=formatpim,
                                     optimize=True, quality=_quality)
                            saved = True

                        if saved:
                            # Add multiple files to the zip
                            zipObj.write(infile)

                            optimize(infile_tmp, image_header)

                            # Move src to dst. (mv src dst)
                            shutil.move(infile_tmp, infile)
                except OSError, e:
                    logging.exception('%s raised an oserror', e)
                # Problem compress the image
                except IOError, e:
                    logging.exception('%s raised an exception', e)
                    if os.path.exists(infile_tmp):
                        os.remove(infile_tmp)
                except BaseException, e:
                    logging.exception('%s raised an exception--', e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='compress images using PIL library')
    parser.add_argument('-src', nargs='?',
                        type=str, help='an path', default=images_folder)
    args = parser.parse_args()

    if args.src:
        logging.info('run script en %s', args.src)
        # scriptname is global variable
        scriptname = "-{}".format(os.path.basename(args.src)).lower()
    else:
        logging.info('run script en %s', images_folder)
    compress_quality_images(args.src)