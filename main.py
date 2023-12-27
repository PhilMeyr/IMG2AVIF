import os
import rawpy
from PIL import Image
import pillow_avif
import exifread
import shutil
import concurrent.futures


# Files & Variables
input_directory_path = os.path.join('input')
output_directory_path = os.path.join('output')
max_workers = 10

def extract_exif(file_path):
    with open(file_path, 'rb') as f:
        exif_data = exifread.process_file(f)
        return exif_data

def convert_image_to_avif(image_or_path, avif_file_path, exif_source=None):
    try:
        if isinstance(image_or_path, Image.Image):
            image = image_or_path
        else:
            image = Image.open(image_or_path)
        
        if exif_source:
            exif_data = extract_exif(exif_source)
        else:
            exif_data = None

        image.save(avif_file_path, format='AVIF')

        if exif_data:
            print(f'Image saved: {avif_file_path} WITH EXIF')
        else:
            print(f'Image saved: {avif_file_path} WITHOUT EXIF')
    except IOError:
        print(f"Erreur lors de la lecture ou de l'enregistrement de l'image : {image_or_path}")


def convert_raw_to_avif(raw_file_path, avif_file_path):
    with rawpy.imread(raw_file_path) as raw:
        rgb = raw.postprocess()
        image = Image.fromarray(rgb)
        convert_image_to_avif(image, avif_file_path, raw_file_path)

def is_image_file(file_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.dng', '.nef']
    return any(file_path.lower().endswith(ext) for ext in image_extensions)

def process_file(file_path, output_directory_path):
    filename = os.path.basename(file_path)
    avif_file_path = os.path.join(output_directory_path, os.path.splitext(filename)[0] + '.avif')

    if is_image_file(filename):
        if filename.lower().endswith(('.dng', '.nef')):
            with rawpy.imread(file_path) as raw:
                rgb = raw.postprocess()
                image = Image.fromarray(rgb)
                convert_image_to_avif(image, avif_file_path, file_path)
        else:
            convert_image_to_avif(file_path, avif_file_path)
    else:
        shutil.copy(file_path, os.path.join(output_directory_path, filename))
        print(f'Non-image file copied: {filename}')

def convert_directory(input_directory_path, output_directory_path):
    if not os.path.exists(input_directory_path):
        print(f"Le répertoire {input_directory_path} n'existe pas.")
        return
    
    if not os.path.exists(output_directory_path):
        os.makedirs(output_directory_path)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        futures = [executor.submit(process_file, os.path.join(input_directory_path, filename), output_directory_path) 
                   for filename in os.listdir(input_directory_path)]
        for future in concurrent.futures.as_completed(futures):
            future.result()

convert_directory(input_directory_path, output_directory_path)
