# Python 2 Scripts

Scripts for automation and image processing:

- **backup_bigger.py**: Backs up old and large images.
- **compress_quality_images.py**: Compresses images, adjusts quality, and generates thumbnails.
- **delete_unused_images.py**: Deletes images listed in a CSV file.
- **generate_thumbnails.py**: Generates thumbnails for images in a directory.

## Usage

Run each script from the terminal. Some scripts require you to modify paths or CSV files according to your environment.

Example:
```bash
python backup_bigger.py
```

## Dependencies

- [Pillow](https://pillow.readthedocs.io/) for image processing.
- `jpegoptim.exe` for JPEG optimization (included).
