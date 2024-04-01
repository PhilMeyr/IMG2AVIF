A simple script for batch converting images to AVIF.

The script tries to save EXIF data but it's not really supported by python librairies for RAW files.
The script tells you if EXIF data have ben saved, or not.

HOWTO
------
1. Install dependencies
>`pipenv install`

2. Place all your images to convert into an ./input/ folder

3. Run 
> `pipenv run main.py`