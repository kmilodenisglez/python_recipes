# Example using the GetLogicalDrives function of the Windows api to detect adding and removing devices
# tested in Windows 10
import string
import time
from ctypes import windll


def get_drive_status():
    devices = []
    record_device_bit = windll.kernel32.GetLogicalDrives()  # The GetLogicalDrives function retrieves a bitmask
    # representing the currently available disk drives.
    for label in string.ascii_uppercase:  # The uppercase letters 'A-Z'
        if record_device_bit & 1:
            devices.append(label)
        record_device_bit >>= 1
    return devices


def detect_device():
    original = set(get_drive_status())
    print('Detecting...')
    time.sleep(3)
    add_device = set(get_drive_status()) - original
    subt_device = original - set(get_drive_status())

    if len(add_device):
        print("There were %d" % (len(add_device)))
        for drive in add_device:
            print("The drives added: %s." % drive)

    elif len(subt_device):
        print("There were %d" % (len(subt_device)))
        for drive in subt_device:
            print("The drives remove: %s." % drive)


if __name__ == '__main__':
    while True:
        detect_device()
