#!/usr/bin/env python

# =======================
# MODULES IMPORTS
# =======================

import os
import imghdr
from csv import reader

# =======================
# VARIABLES
# =======================

# csv con imagenes a eliminar
csvfile = "libro_imagenes.csv"

# Location of files to compress/delete
folder = "/public_html/webimages/upload/MenuItem"


def purge_imgs():
    # read csv file as a list of lists
    with open(csvfile, 'rt') as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)
        # Pass reader object to list() to get a list of lists
        # list_of_rows = list(csv_reader)
        for row in csv_reader:
            if len(row):
                file = row[0]
                name, ext = os.path.splitext(file)
                file_fullpath = os.path.join(folder, file)
                try:
                    if os.path.isfile(file_fullpath) and imghdr.what(file_fullpath):
                        print('eliminada ', name, ext,
                              imghdr.what(file_fullpath))
                        # remove file
                        os.remove(file_fullpath)
                    else:
                        print('No eliminada', file_fullpath)
                except BaseException as e:
                    print('Error: ', e)


if __name__ == "__main__":
    if os.path.isdir(folder):
        purge_imgs()
    else:
        print('No es un directorio')
