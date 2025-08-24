#!/usr/bin/env python3
"""
PictureSort - Image Sorting by Date

A script for automatically sorting and renaming images
based on their capture date.
"""

import os
import sys
import shutil
import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import re

try:
    from PIL import Image, ExifTags
    from tqdm import tqdm
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    print("Please install dependencies with: pip install -r requirements.txt")
    sys.exit(1)


class ImageSorter:
    """Main class for image sorting."""
    
    def __init__(self, source_dir: str, dest_dir: str, include_gps: bool = False, include_dir: bool = False):
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.include_gps = include_gps
        self.include_dir = include_dir
        self.supported_extensions = {'.jpg', '.jpeg', '.png'}
        self.stats = {
            'total_files': 0,
            'exif_files': 0,
            'filesystem_date_files': 0,
            'current_date_files': 0,
            'gps_files': 0,
            'copied_files': 0,
            'error_files': 0
        }
        # List for GPS data for CSV export
        self.gps_data = []
        
    def find_image_files(self) -> List[Path]:
        """Finds all image files in the source directory recursively."""
        image_files = []
        
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory does not exist: {self.source_dir}")
            
        print(f"Searching directory: {self.source_dir}")
        
        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                image_files.append(file_path)
                
        print(f"Found: {len(image_files)} image files")
        self.stats['total_files'] = len(image_files)
        return image_files
    
    def get_gps_coordinates(self, image_path: Path) -> Optional[Tuple[float, float]]:
        """Extracts GPS coordinates from an image."""
        if not self.include_gps:
            return None
            
        try:
            with Image.open(image_path) as img:
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    
                    # Find GPS tags
                    gps_tags = {}
                    for tag_id in exif:
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        if isinstance(tag, str) and tag.startswith('GPS'):
                            gps_tags[tag] = exif[tag_id]
                    
                    # Extract GPS coordinates
                    if 'GPSLatitude' in gps_tags and 'GPSLongitude' in gps_tags:
                        try:
                            lat = self._convert_to_degrees(gps_tags['GPSLatitude'])
                            lon = self._convert_to_degrees(gps_tags['GPSLongitude'])
                            
                            # Consider GPS latitude reference
                            if 'GPSLatitudeRef' in gps_tags and gps_tags['GPSLatitudeRef'] == 'S':
                                lat = -lat
                            
                            # Consider GPS longitude reference
                            if 'GPSLongitudeRef' in gps_tags and gps_tags['GPSLongitudeRef'] == 'W':
                                lon = -lon
                            
                            self.stats['gps_files'] += 1
                            return (lat, lon)
                        except Exception as e:
                            print(f"Error during GPS conversion for {image_path}: {e}")
                    
                    # Alternative: GPSInfo format (as seen in debug outputs)
                    elif 'GPSInfo' in gps_tags:
                        gps_info = gps_tags['GPSInfo']
                        try:
                            # GPSInfo has structure: {1: 'N', 2: (lat_deg, lat_min, lat_sec), 3: 'E', 4: (lon_deg, lon_min, lon_sec)}
                            if 2 in gps_info and 4 in gps_info:
                                lat_dms = gps_info[2]  # (degrees, minutes, seconds)
                                lon_dms = gps_info[4]  # (degrees, minutes, seconds)
                                
                                lat = self._convert_to_degrees(lat_dms)
                                lon = self._convert_to_degrees(lon_dms)
                                
                                # Consider reference
                                if 1 in gps_info and gps_info[1] == 'S':
                                    lat = -lat
                                if 3 in gps_info and gps_info[3] == 'W':
                                    lon = -lon
                                
                                self.stats['gps_files'] += 1
                                return (lat, lon)
                        except Exception as e:
                            print(f"Error during GPSInfo conversion for {image_path}: {e}")
                        
        except Exception as e:
            print(f"Warning: Could not read GPS data for {image_path}: {e}")
        
        return None
    
    def _convert_to_degrees(self, dms) -> float:
        """Converts GPS coordinates from DMS (Degrees, Minutes, Seconds) to decimal degrees."""
        degrees = float(dms[0])
        minutes = float(dms[1])
        seconds = float(dms[2])
        
        return degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    def get_image_date(self, image_path: Path) -> Tuple[datetime, str]:
        """Extracts the capture date from an image and returns date and source."""
        try:
            with Image.open(image_path) as img:
                # Try to read EXIF data
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    
                    # Search for DateTimeOriginal tag
                    for tag_id in exif:
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        if tag == 'DateTimeOriginal':
                            date_str = exif[tag_id]
                            try:
                                # Parse EXIF date (format: YYYY:MM:DD HH:MM:SS)
                                date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                                self.stats['exif_files'] += 1
                                return date, f"EXIF: {date_str}"
                            except ValueError:
                                pass
                                
        except Exception as e:
            print(f"Warning: Could not read EXIF data for {image_path}: {e}")
        
        # Fallback: Use filesystem creation date
        try:
            stat = image_path.stat()
            # Use the earliest available date
            date = datetime.fromtimestamp(min(stat.st_ctime, stat.st_mtime))
            self.stats['filesystem_date_files'] += 1
            return date, f"Filesystem: {date.strftime('%Y-%m-%d %H:%M:%S')}"
        except Exception as e:
            print(f"Warning: Could not read filesystem date for {image_path}: {e}")
            # Last fallback: Current date
            date = datetime.now()
            self.stats['current_date_files'] += 1
            return date, f"Current date: {date.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def get_subfolder_name(self, image_path: Path) -> str:
        """Extracts the name of the subfolder relative to the source directory."""
        if not self.include_dir:
            return ""
            
        try:
            # Relative path from source directory
            relative_path = image_path.relative_to(self.source_dir)
            
            # If image is directly in source directory
            if relative_path.parent == Path('.'):
                return ""
            
            # Extract first subfolder name
            subfolder = relative_path.parts[0]
            return f"_{subfolder}_"
            
        except Exception:
            return ""
    
    def generate_new_filename(self, original_path: Path, date: datetime, gps_coords: Optional[Tuple[float, float]] = None, subfolder: str = "") -> str:
        """Generates a new filename based on date, GPS and subfolder."""
        date_str = date.strftime('%Y%m%d_%H%M%S')
        original_name = original_path.stem
        extension = original_path.suffix.lower()
        
        # Remove invalid characters from filename
        safe_name = re.sub(r'[^\w\-_.]', '_', original_name)
        
        # Build filename - GPS goes at the end
        filename_parts = [date_str]
        
        if subfolder:
            filename_parts.append(subfolder)
        
        filename_parts.append(safe_name)
        
        # Add GPS coordinates at the end
        if gps_coords:
            lat, lon = gps_coords
            filename_parts.append(f"_{lat:.6f},{lon:.6f}_")
        
        return f"{'_'.join(filename_parts)}{extension}"
    
    def get_unique_filename(self, base_filename: str) -> str:
        """Ensures that the filename is unique in the destination directory."""
        if not self.dest_dir.exists():
            return base_filename
            
        counter = 0
        name, ext = os.path.splitext(base_filename)
        
        while True:
            if counter == 0:
                test_filename = base_filename
            else:
                test_filename = f"{name}_{counter}{ext}"
                
            if not (self.dest_dir / test_filename).exists():
                return test_filename
            counter += 1
    
    def create_gps_csv(self) -> None:
        """Creates a CSV file with GPS data for Google Maps import."""
        if not self.gps_data:
            print("No GPS data found - CSV file will not be created.")
            return
            
        csv_filename = self.dest_dir / "gps_positions.csv"
        
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header for Google Maps import
                writer.writerow(['Name', 'Latitude', 'Longitude', 'Description'])
                
                # Write GPS data
                for filename, lat, lon, date_str in self.gps_data:
                    description = f"Photo taken on {date_str}"
                    writer.writerow([filename, lat, lon, description])
                    
            print(f"GPS position data saved in: {csv_filename}")
            print(f"CSV file contains {len(self.gps_data)} entries for Google Maps import")
            
        except Exception as e:
            print(f"Error creating CSV file: {e}")
    
    def print_statistics(self) -> None:
        """Prints detailed statistics."""
        print("\n" + "="*60)
        print("STATISTICS")
        print("="*60)
        print(f"Total image files found: {self.stats['total_files']}")
        print(f"Successfully copied: {self.stats['copied_files']}")
        print(f"Copy errors: {self.stats['error_files']}")
        print()
        print("Data sources:")
        print(f"  - EXIF data used: {self.stats['exif_files']} ({self.stats['exif_files']/max(1, self.stats['total_files'])*100:.1f}%)")
        print(f"  - Filesystem date used: {self.stats['filesystem_date_files']} ({self.stats['filesystem_date_files']/max(1, self.stats['total_files'])*100:.1f}%)")
        print(f"  - Current date used: {self.stats['current_date_files']} ({self.stats['current_date_files']/max(1, self.stats['total_files'])*100:.1f}%)")
        if self.include_gps:
            print(f"  - GPS data found: {self.stats['gps_files']} ({self.stats['gps_files']/max(1, self.stats['total_files'])*100:.1f}%)")
        print("="*60)
    
    def sort_images(self) -> None:
        """Main function for sorting images."""
        # Create destination directory if it doesn't exist
        self.dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all image files
        image_files = self.find_image_files()
        
        if not image_files:
            print("No image files found.")
            return
        
        # Collect images with their data
        print("Analyzing image data...")
        images_with_data = []
        
        for image_path in tqdm(image_files, desc="Analyzing images"):
            try:
                date, source = self.get_image_date(image_path)
                gps_coords = self.get_gps_coordinates(image_path)
                subfolder = self.get_subfolder_name(image_path)
                images_with_data.append((image_path, date, source, gps_coords, subfolder))
            except Exception as e:
                print(f"Error analyzing {image_path}: {e}")
                self.stats['error_files'] += 1
        
        # Sort by date (oldest first) - GPS and directory have no influence
        images_with_data.sort(key=lambda x: x[1])
        
        # Copy and rename
        print(f"Copying {len(images_with_data)} images...")
        
        for image_path, date, source, gps_coords, subfolder in tqdm(images_with_data, desc="Copying images"):
            try:
                new_filename = self.generate_new_filename(image_path, date, gps_coords, subfolder)
                unique_filename = self.get_unique_filename(new_filename)
                dest_path = self.dest_dir / unique_filename
                
                shutil.copy2(image_path, dest_path)
                
                # Collect GPS data for CSV
                if gps_coords and self.include_gps:
                    lat, lon = gps_coords
                    date_str = date.strftime('%Y-%m-%d %H:%M:%S')
                    self.gps_data.append((unique_filename, lat, lon, date_str))
                
                # Create info string for output
                info_parts = [source]
                if gps_coords:
                    lat, lon = gps_coords
                    info_parts.append(f"GPS: {lat:.6f},{lon:.6f}")
                if subfolder:
                    info_parts.append(f"Folder: {subfolder.strip('_')}")
                
                info_str = " | ".join(info_parts)
                print(f"Copied: {image_path.name} -> {unique_filename} ({info_str})")
                self.stats['copied_files'] += 1
                
            except Exception as e:
                print(f"Error copying {image_path}: {e}")
                self.stats['error_files'] += 1
        
        print(f"\nDone! {self.stats['copied_files']} images were sorted and copied.")
        print(f"Destination directory: {self.dest_dir}")
        
        # Create CSV file for GPS data
        if self.include_gps:
            self.create_gps_csv()
        
        # Show statistics
        self.print_statistics()


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Sorts images by their capture date and copies them to a destination directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sort_images_by_date.py --source ~/Pictures/Unsorted --dest ~/Pictures/Sorted
  python sort_images_by_date.py --source /media/photos --dest ./sorted --gps
  python sort_images_by_date.py --source /media/photos --dest ./sorted --gps --dir
        """
    )
    
    parser.add_argument(
        '--source',
        required=True,
        help='Path to source directory (recursively finds all images in subdirectories)'
    )
    
    parser.add_argument(
        '--dest',
        required=True,
        help='Path to destination directory where all sorted images will be copied'
    )
    
    parser.add_argument(
        '--gps',
        action='store_true',
        help='Embed GPS coordinates in filename (format: _lat,lon_ at the end) and create CSV file'
    )
    
    parser.add_argument(
        '--dir',
        action='store_true',
        help='Embed subfolder names in filename'
    )
    
    args = parser.parse_args()
    
    try:
        sorter = ImageSorter(args.source, args.dest, args.gps, args.dir)
        sorter.sort_images()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 