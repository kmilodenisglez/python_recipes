#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Thumbnail Generator

Generates thumbnails for all images in a specified directory.
"""

# =======================
# MODULES IMPORTS
# =======================

import os
import imghdr
import logging
import argparse
from PIL import Image

# =======================
# CONFIGURATION
# =======================

# Default configuration
DEFAULT_CONFIG = {
    'images_folder': '/home/un2x3c5/public_html/webimages/upload/MenuItem',
    'logs_folder': '/home/un2x3c5/logs/cronjob',
    'sizes': {
        'small': (100, 100),
        'standard': (600, 600)
    }
}

# =======================
# LOGGING SETUP
# =======================

def setup_logging(logs_folder):
    """
    Configure logging with proper format and file location.
    
    Args:
        logs_folder (str): Directory for log files
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    log_file = os.path.join(logs_folder, "generate_thumbnails.log")
    
    # Configure logging
    logging.basicConfig(
        filename=log_file,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
        datefmt='%d/%m/%Y %I:%M:%S %p',
        level=logging.INFO
    )
    
    # Add console handler for debugging
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

# =======================
# THUMBNAIL FUNCTIONS
# =======================

def generate_thumbnail(im, dirpath, filename, format_im='jpeg', sizes=None):
    """
    Generate thumbnail from image.
    
    Args:
        im (PIL.Image): PIL Image object
        dirpath (str): Directory path for saving thumbnail
        filename (str): Original filename
        format_im (str): Image format (jpeg, png, etc.)
        sizes (dict): Dictionary of thumbnail sizes
        
    Returns:
        bool: True if successful, False otherwise
    """
    if sizes is None:
        sizes = DEFAULT_CONFIG['sizes']
        
    try:
        width_to_apply, height_to_apply = sizes.get('small', (100, 100))
        # Create a copy to avoid modifying the original
        thumb_im = im.copy()
        thumb_im.thumbnail((width_to_apply, height_to_apply))
        
        # Save each image with appropriate filename
        new_filename = '{0}x{1}_resized_{2}'.format(
            width_to_apply, height_to_apply, filename)
        infile = os.path.join(dirpath, new_filename)
        
        thumb_im.save(infile, format=format_im, optimize=True, progressive=True)
        logging.info("Generated thumbnail: %s", new_filename)
        return True
    except Exception as error:
        logging.exception("Failed to generate thumbnail for %s: %s", filename, error)
        return False


def process_image(filepath, filename, dirpath):
    """
    Process a single image file.
    
    Args:
        filepath (str): Full path to image file
        filename (str): Filename of image
        dirpath (str): Directory path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if file is an image
        image_header = imghdr.what(filepath)
        if not image_header:
            logging.debug("Not an image file: %s", filepath)
            return False
            
        # Open and process image
        with Image.open(filepath) as img:
            return generate_thumbnail(img, dirpath, filename, image_header)
            
    except Exception as error:
        logging.exception("Error processing %s: %s", filepath, error)
        return False


def main(path_src=None):
    """
    Main function to process all images in directory.
    
    Args:
        path_src (str): Source directory for images
    """
    if path_src is None:
        path_src = DEFAULT_CONFIG['images_folder']
        
    logging.info("Starting thumbnail generation in %s", path_src)
    
    # Track statistics
    total_files = 0
    successful = 0
    failed = 0
    
    # Loop through all the folder
    for dirpath, _, filenames in os.walk(path_src, topdown=False):
        for filename in filenames:
            total_files += 1
            infile = os.path.join(dirpath, filename)
            
            if process_image(infile, filename, dirpath):
                successful += 1
            else:
                failed += 1
                
    logging.info("Thumbnail generation complete. Total: %d, Success: %d, Failed: %d", 
                 total_files, successful, failed)


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate thumbnails for images')
    parser.add_argument('-src', '--source', help='Source directory for images')
    parser.add_argument('-log', '--log-folder', help='Folder for log files')
    args = parser.parse_args()
    
    # Setup logging
    log_folder = args.log_folder if args.log_folder else DEFAULT_CONFIG['logs_folder']
    setup_logging(log_folder)
    
    # Run main function
    main(args.source)