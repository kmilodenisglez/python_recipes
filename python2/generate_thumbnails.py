#!/usr/bin/env python

# =======================
# MODULES IMPORTS
# =======================

import os
import imghdr
import logging
from PIL import Image

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
script_name = "-restaurant"

# Location of files to compress/delete
images_folder = r"/home/un2x3c5/public_html/webimages/upload/MenuItem"

# dictionary for image sizes
sizes = {'small': (100, 100), 'standard': (600, 600)}


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


def main(path_src=images_folder):
    # Loop through all the folder
    for dirpath, _, filenames in os.walk(path_src, topdown=False):
        for filename in filenames:
            try:
                infile = os.path.join(dirpath, filename)
                image_header = imghdr.what(infile)

                if image_header:
                    with Image.open(infile) as pim:
                        generate_thumbnail(pim, dirpath, filename, image_header)
            except BaseException as error:
                logging.exception('%s raised an exception--', error)


if __name__ == '__main__':
    main()
