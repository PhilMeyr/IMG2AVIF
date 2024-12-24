# IMG2AVIF

A simple script to convert images to AVIF format in batches.

## Features

- Image conversion to AVIF format
- Support for input formats: JPG, JPEG, PNG, GIF, BMP, TIFF
- Support for RAW files (DNG, NEF)
- Preservation of EXIF data (when possible)
- Batch processing with multi-threading
- Retention of non-image files in the output directory

## Prerequisites

- Python 3.11

## Installation

1. Clone the repository:

```bash
git clone [repo-url]
cd IMG2AVIF
```

2. Install the dependencies:

```bash
pipenv install
```

## Usage

1. Create an `input` directory in the project folder
2. Place your images to convert in the `input` directory
3. Run the script:

```bash
pipenv run python img2avif.py
```

The converted images will be saved in the `output` directory.

## Notes

- EXIF data is preserved when possible, but support is limited for RAW files
- The script uses 5 workers in parallel to optimize conversion speed
- Non-image files are copied as is to the output directory

## Folder structure

```bash
IMG2AVIF/
├── input/          # Source images folder
├── output/         # Converted images folder
├── main.py         # Main script
├── Pipfile         # pipenv configuration
└── README.md       # Documentation
```
