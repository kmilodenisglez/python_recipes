#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image compression and thumbnail generation utility.

This script processes images by:
1. Compressing them to reduce file size
2. Generating thumbnails
3. Creating backups of original files
"""

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
from ConfigParser import ConfigParser  # Python 2 import

# =======================
# CONFIGURATION
# =======================

# Load configuration from config file if exists
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.ini')
config = ConfigParser()

# Default configuration
DEFAULT_CONFIG = {
    'paths': {
        'images_folder': '/home/userfolder/public_html/webimages/upload/MenuItem',
        'backup_folder': '/home/userfolder/backup/',
        'tmp_folder': '/home/userfolder/tmp',
        'logs_folder': '/home/userfolder/logs/cronjob'
    },
    'settings': {
        'script_name': '-restaurant',
        'image_older_hours': '23',
        'image_older_days': '1',
        'minimum_size_allowed': '89000'
    }
}

# Try to load config file, use defaults if not available
if os.path.exists(CONFIG_FILE):
    config.read(CONFIG_FILE)
else:
    # Create sections
    config.add_section('paths')
    config.add_section('settings')
    
    # Set default values
    for section, options in DEFAULT_CONFIG.items():
        for option, value in options.items():
            config.set(section, option, value)
    
    # Write default config file
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

# Get configuration values
IMAGES_FOLDER = config.get('paths', 'images_folder')
BACKUP_FOLDER = config.get('paths', 'backup_folder')
TMP_FOLDER = config.get('paths', 'tmp_folder')
LOGS_FOLDER = config.get('paths', 'logs_folder')

SCRIPT_NAME = config.get('settings', 'script_name')
IMAGE_OLDER_HOURS = config.getint('settings', 'image_older_hours')
IMAGE_OLDER_DAYS = config.getint('settings', 'image_older_days')
MINIMUM_SIZE_ALLOWED = config.getint('settings', 'minimum_size_allowed')

SIZES = {
    'standard': (600, 600),
    'small': (100, 100)
}

# =======================
# LOGGING SETUP
# =======================

def setup_logging():
    """Configure logging with proper format and file location."""
    # Create logs directory if it doesn't exist
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)

    log_file = os.path.join(LOGS_FOLDER, "compress_quality_images.log")
    
    # Configure logging
    logging.basicConfig(
        filename=log_file,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
        datefmt='%d/%m/%Y %I:%M:%S %p',
        level=logging.INFO
    )
    
    # Add console handler for debugging
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger('').addHandler(console)

setup_logging()

# =======================
# IMAGE PROCESSING FUNCTIONS
# =======================

def from_ago(file_path, fmt_hours=False):
    """
    Check if file was modified within specified time period.
    
    Args:
        file_path (str): Path to the file
        fmt_hours (bool): If True, check hours instead of days
        
    Returns:
        bool: True if file is newer than threshold, False otherwise
    """
    now = time.time()
    if fmt_hours:
        return (now - os.stat(file_path).st_mtime) / 3600 < IMAGE_OLDER_HOURS
    return (now - os.stat(file_path).st_mtime) / (3600 * 24) < IMAGE_OLDER_DAYS


def size_greater_than(file_path):
    """
    Check if file size is greater than minimum allowed.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file is larger than threshold, False otherwise
    """
    return os.path.getsize(file_path) > MINIMUM_SIZE_ALLOWED


def remove_empty_zips():
    for root, _, files in os.walk(BACKUP_FOLDER, topdown=False):
        for _file in files:
            infile = os.path.join(root, _file)
            # remove .zip with 1K or 22 byte
            if _file.lower().endswith(".zip") and os.stat(infile).st_size < 24:
                os.remove(infile)


def select_quality(file_path):
    """
    Select appropriate compression quality based on file size.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        int: Quality value (10-65)
    """
    try:
        image_filesize = os.path.getsize(file_path)

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
        logging.exception("Error determining file size")
        return 65


def always_jpg(image_header):
    """
    Convert PNG to JPEG format identifier.
    
    Args:
        image_header (str): Image format identifier
        
    Returns:
        str: Format to use (always 'jpeg' for PNG)
    """
    if image_header and image_header.lower() == "png":
        return "jpeg"
    return image_header


def is_transparent(image):
    """
    Check if an image has transparency.
    
    Args:
        image (PIL.Image): PIL Image object
        
    Returns:
        bool: True if image has transparency, False otherwise
    """
    if not isinstance(image, Image.Image):
        return False
    return (image.mode in ('RGBA', 'LA') or
            (image.mode == 'P' and 'transparency' in image.info))


def resize_with_aspect_ratio(im, infile, format_im='jpeg'):
    """
    maintain its aspect ratio
    """
    try:
        width, height = im.size
        width_to_apply, height_to_apply = SIZES.get('standard', (600, 600))
        # applied (width_to_apply, height_to_apply) only if it is less than original image size
        if (width_to_apply, height_to_apply) < (width, height):
            # maintain ratio to width
            height_to_apply = int(width_to_apply * height / width)
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
        width_to_apply, height_to_apply = SIZES.get('small', (100, 100))
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
    
    Args:
        im (PIL.Image): PIL Image object
        no_rgba (bool): Convert transparent images to RGB
        bw (bool): Convert to grayscale
        replace_alpha (str): Color to replace transparency with
        
    Returns:
        PIL.Image: Converted image
    """
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


def compress_quality_images(path_src=IMAGES_FOLDER, _resize_img="y", _optimize_jpeg="y", _generate_thumbnail="y"):
    now = time.time()
    gzip_name = "{}{}{}".format(now, SCRIPT_NAME, '.zip')
    gzip_file = os.path.join(BACKUP_FOLDER, gzip_name)
    infile_tmp = ""

    # create a directory if it does not exist
    try:
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)
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
                        infile_tmp = os.path.join(TMP_FOLDER, file_tmp)
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
                        type=str, help='an path', default=IMAGES_FOLDER)
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
        SCRIPT_NAME = "-{}".format(os.path.basename(args.src)).lower()
    else:
        logging.info('run script en %s', IMAGES_FOLDER)

    compress_quality_images(args.src, _resize_img=args.resize, _optimize_jpeg=args.jpegoptim,
                            _generate_thumbnail=args.thumbnail)
    remove_empty_zips()
