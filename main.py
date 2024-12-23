#!/usr/bin/env python3

import os
import logging
import rawpy
from PIL import Image
import pillow_avif
import exifread
import shutil
import concurrent.futures
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import multiprocessing
from tqdm import tqdm
from colorama import init, Fore, Style

# Initialize colorama
init()

# Configuration
@dataclass
class Config:
    input_directory: Path = Path('input')
    output_directory: Path = Path('output')
    max_workers: int = multiprocessing.cpu_count()
    image_extensions: tuple = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.dng', '.nef')
    quality: int = 80  # AVIF quality (0-100)

config = Config()

# Custom formatter for colored logs
class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors to the logs."""
    
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

# Set up logging with colors
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

class ImageConversionError(Exception):
    """Custom exception for image conversion errors."""
    pass

def extract_exif(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Extract EXIF data from an image file.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Optional[Dict[str, Any]]: EXIF data if available, None otherwise
    """
    try:
        with open(file_path, 'rb') as f:
            return exifread.process_file(f)
    except Exception as e:
        logger.warning(f'Failed to extract EXIF from {file_path}: {str(e)}')
        return None

def convert_image_to_avif(
    image_or_path: Path | Image.Image,
    avif_file_path: Path,
    exif_source: Optional[Path] = None
) -> None:
    """
    Convert an image to AVIF format.
    
    Args:
        image_or_path: Source image or path to source image
        avif_file_path: Output path for AVIF file
        exif_source: Optional path to source of EXIF data
    
    Raises:
        ImageConversionError: If conversion fails
    """
    try:
        if isinstance(image_or_path, Image.Image):
            image = image_or_path
        else:
            image = Image.open(image_or_path)

        # Optimize image size if needed
        if max(image.size) > 4000:
            image.thumbnail((4000, 4000), Image.Resampling.LANCZOS)

        exif_data = extract_exif(exif_source) if exif_source else None
        
        image.save(
            avif_file_path,
            format='AVIF',
            quality=config.quality,
            optimize=True
        )

        status = 'WITH' if exif_data else 'WITHOUT'
        logger.debug(f'Image saved: {avif_file_path} {status} EXIF')
        
    except Exception as e:
        raise ImageConversionError(f'Failed to convert {image_or_path}: {str(e)}')

def process_file(file_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Process a single file for conversion.
    
    Args:
        file_path: Path to the file to process
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (filename, error_message) if error occurred, else (filename, None)
    """
    try:
        filename = file_path.name
        output_path = config.output_directory / (file_path.stem + '.avif')

        if file_path.suffix.lower() in config.image_extensions:
            if file_path.suffix.lower() in ('.dng', '.nef'):
                with rawpy.imread(str(file_path)) as raw:
                    rgb = raw.postprocess()
                    image = Image.fromarray(rgb)
                    convert_image_to_avif(image, output_path, file_path)
            else:
                convert_image_to_avif(file_path, output_path)
        else:
            shutil.copy(file_path, config.output_directory / filename)
            logger.debug(f'Non-image file copied: {filename}')
            
        return filename, None
            
    except Exception as e:
        error_msg = f'Error processing {file_path}: {str(e)}'
        logger.error(error_msg)
        return filename, error_msg

def process_files_with_progress(files: List[Path]) -> List[Tuple[str, str]]:
    """
    Process files with a progress bar.
    
    Args:
        files: List of files to process
        
    Returns:
        List[Tuple[str, str]]: List of (filename, error_message) for failed conversions
    """
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        futures = []
        for file_path in files:
            future = executor.submit(process_file, file_path)
            futures.append(future)
            
        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(futures),
            desc=f"{Fore.CYAN}Converting images{Style.RESET_ALL}",
            unit="file"
        ):
            filename, error = future.result()
            if error:
                errors.append((filename, error))
                
    return errors

def display_error_summary(errors: List[Tuple[str, str]]) -> None:
    """
    Display a summary of all errors that occurred during processing.
    
    Args:
        errors: List of (filename, error_message) tuples
    """
    if not errors:
        logger.info(f"{Fore.GREEN}✓ All files processed successfully!{Style.RESET_ALL}")
        return
        
    logger.error(f"\n{Fore.RED}Error Summary:{Style.RESET_ALL}")
    logger.error(f"{Fore.RED}Found {len(errors)} error(s) during processing:{Style.RESET_ALL}")
    
    for filename, error in errors:
        logger.error(f"\n{Fore.YELLOW}File:{Style.RESET_ALL} {filename}")
        logger.error(f"{Fore.RED}Error:{Style.RESET_ALL} {error}")

def main() -> None:
    """Main function to orchestrate the conversion process."""
    try:
        if not config.input_directory.exists():
            raise FileNotFoundError(f"Directory {config.input_directory} doesn't exist")
        
        config.output_directory.mkdir(exist_ok=True)
        
        files = list(config.input_directory.iterdir())
        logger.info(f"Found {Fore.CYAN}{len(files)}{Style.RESET_ALL} files to process")
        
        errors = process_files_with_progress(files)
        
        logger.info(f"\n{Fore.GREEN}Conversion process completed{Style.RESET_ALL}")
        display_error_summary(errors)
        
    except Exception as e:
        logger.error(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
        raise

if __name__ == '__main__':
    main()
