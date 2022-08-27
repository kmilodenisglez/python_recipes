#!/usr/bin/env python

# =======================
# MODULES IMPORTS
# =======================

import os
import sys
import time
import gzip
import imghdr
from csv import reader
from zipfile import ZipFile

# =======================
# VARIABLES
# =======================

scriptname = "-restaurant"

# csv con imagenes a eliminar
timestamp_name = "timestamp_rst"

# Location of files to compress/delete
images_folder = "/home/un2x3c5/public_html/webimages/upload/Company"
backup_folder = "/home/un2x3c5/un2x3.com/public_ftp/"

# Image files older than specified
image_older_days = 1

# Compress files older than specified
compress_older_days = 1

# Delete files older than specified
# delete_older_days = 3

# maximum size allowed in Bytes
maximum_size_allowed = 700042  # ~700KB

# 1001000 #(~1MB)

# Current time
now = time.time()

timestamp_file = os.path.join(backup_folder, timestamp_name)


def from_ago(file):
    return (now - os.stat(file).st_mtime) / (3600*24) < compress_older_days


def size_greater_than(file):
    return os.path.getsize(file) > maximum_size_allowed


def make_backup():
    gzipname = "{}{}{}".format(now, scriptname, '.zip')
    gzipfile = os.path.join(backup_folder, gzipname)

    # create a directory if it does not exist
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    # Create a ZipFile Object
    with ZipFile(gzipfile, 'w') as zipObj:
        # Loop through all the folder
        for root, _, files in os.walk(images_folder, topdown=False):
            for file in files:
                # print root, name
                f = os.path.join(root, file)
                if from_ago(f) and size_greater_than(f) and imghdr.what(f):
                    # Add multiple files to the zip
                    zipObj.write(f)
    # actualizamos el timestamp
    write_timestamp()


def get_timestamp():
    with open(timestamp_file, mode="r") as archivo:
        return archivo.readline()


def write_timestamp():
    with open(timestamp_file, 'w') as archivo:
        archivo.write(str(now))

# para nombres de ficheros con codificaciones raras


def decodeName(name):
    if type(name) == str:  # leave unicode ones alone
        try:
            name = name.decode('utf8')
        except:
            name = name.decode('windows-1252')
    return name

# 1611369979.4232066


if __name__ == "__main__":
    if os.path.isfile(timestamp_file):
        # comprobamos si el timestamp fue actualizado recientemente, es decir antes de image_older_days
        if ((now - float(get_timestamp())) / (3600 * 24) < (image_older_days - 0.2)):
            sys.exit()
    else:
        # first time and creamos el timestamp
        write_timestamp()
    make_backup()
    # body del email, el print se envia por el cronjob como el email.
    body = "Ha sido creado el backup {}{}{} con nuevas imagenes de los restaurantes a procesar!!!".format(
        now, scriptname, '.zip')
    print(body)