# PictureSort - Image Sorting by Date

A Python script for automatically sorting and renaming images based on their capture date.

> **🇩🇪 Deutsche Version verfügbar**: [README_de.md](README_de.md)

## Use Case: Vacation Photos and Slideshow Preparation

This script is particularly useful for organizing vacation photos from multiple devices (phones, cameras, drones, etc.) into a chronologically ordered collection for slideshow creation. Simply pass the folder containing all your vacation photos in subfolders to the script, and it will create a chronologically ordered sequence in an export folder based on capture dates. It's also possible to generate a CSV from GPS tags for Google Maps import to track your route later.

### Perfect for:
- **Vacation photos** from multiple devices
- **Event photography** with multiple photographers
- **Drone footage** mixed with ground photos
- **Family trips** with photos from different phones
- **Professional shoots** with multiple cameras
- **Creating chronological slideshows**
- **Route tracking** via Google Maps

## Features

- Recursive search for image files (.jpg, .jpeg, .png)
- Extraction of EXIF capture date from images
- Fallback to filesystem creation date if no EXIF data available
- Sorting by date (oldest first)
- Automatic renaming in format: `YYYYMMDD_HHMMSS_originalfilename.jpg`
- **GPS coordinates in filename** (optional, at the end of filename)
- **Subfolder names in filename** (optional)
- **CSV export for Google Maps import** (when GPS is enabled)
- Conflict avoidance through automatic counters
- Progress bars for better user experience
- Detailed statistics at the end

## Installation

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python sort_images_by_date.py --source /path/to/source --dest /path/to/destination
```

### With GPS Coordinates
```bash
python sort_images_by_date.py --source /path/to/source --dest /path/to/destination --gps
```

### With Subfolder Names
```bash
python sort_images_by_date.py --source /path/to/source --dest /path/to/destination --dir
```

### With GPS and Subfolder Names
```bash
python sort_images_by_date.py --source /path/to/source --dest /path/to/destination --gps --dir
```

## Command Line Options

### Required Options
- `--source SOURCE`: Path to source directory (recursively finds all images in subdirectories)
- `--dest DEST`: Path to destination directory where all sorted images will be copied

### Optional Options
- `--gps`: Embed GPS coordinates in filename (format: _lat,lon_ at the end) and create CSV file
- `--dir`: Embed subfolder names in filename
- `-h, --help`: Show help message

## Filename Formats

### Basic Format
```
YYYYMMDD_HHMMSS_originalfilename.jpg
```

### With Subfolder Names
```
YYYYMMDD_HHMMSS__subfolder__originalfilename.jpg
```

### With GPS Coordinates
```
YYYYMMDD_HHMMSS_originalfilename__lat,lon_.jpg
```

### With Subfolder and GPS
```
YYYYMMDD_HHMMSS__subfolder__originalfilename__lat,lon_.jpg
```

## GPS Features

### GPS in Filename
- **Format**: `_51.324867,12.575267_` (directly copyable to Google Maps)
- **Position**: At the end of filename
- **Precision**: 6 decimal places

### CSV Export for Google Maps
When `--gps` is enabled, a `gps_positions.csv` file is automatically created:
- **File**: `gps_positions.csv` in destination directory
- **Format**: `Name,Latitude,Longitude,Description`
- **Import**: Directly importable to Google Maps
- **Description**: Contains capture date and time

## Examples

### Example 1: Basic Sorting
```bash
python sort_images_by_date.py --source ~/Pictures/Unsorted --dest ~/Pictures/Sorted
```
**Result**: `20250627_185246_PXL_20250627_165246421.jpg`

### Example 2: With GPS Coordinates
```bash
python sort_images_by_date.py --source ~/Pictures/Unsorted --dest ~/Pictures/Sorted --gps
```
**Result**: `20250627_185246_PXL_20250627_165246421__51.324867,12.575267_.jpg`
**Additionally**: `gps_positions.csv` is created

### Example 3: With Subfolder Names
```bash
python sort_images_by_date.py --source ~/Pictures/Unsorted --dest ~/Pictures/Sorted --dir
```
**Result**: `20250627_185246__input__PXL_20250627_165246421.jpg`

### Example 4: Full Features
```bash
python sort_images_by_date.py --source ~/Pictures/Unsorted --dest ~/Pictures/Sorted --gps --dir
```
**Result**: `20250627_185246__input__PXL_20250627_165246421__51.324867,12.575267_.jpg`
**Additionally**: `gps_positions.csv` is created

## Vacation Photo Workflow Example

### Scenario: European Road Trip
You have photos from:
- **Phone 1**: Family photos and quick snapshots
- **Phone 2**: Partner's phone with different angles
- **Camera**: High-quality landscape shots
- **Drone**: Aerial views of cities and landscapes

### Folder Structure Before:
```
Vacation_2025/
├── Phone1/
│   ├── IMG_001.jpg
│   ├── IMG_002.jpg
│   └── ...
├── Phone2/
│   ├── PXL_001.jpg
│   ├── PXL_002.jpg
│   └── ...
├── Camera/
│   ├── DSC_001.jpg
│   ├── DSC_002.jpg
│   └── ...
└── Drone/
    ├── DJI_001.jpg
    ├── DJI_002.jpg
    └── ...
```

### Command:
```bash
python sort_images_by_date.py --source ~/Vacation_2025 --dest ~/Vacation_2025_Sorted --gps --dir
```

### Result:
```
Vacation_2025_Sorted/
├── 20250627_080000__Phone1__IMG_001__48.8566,2.3522_.jpg
├── 20250627_080015__Phone2__PXL_001__48.8566,2.3522_.jpg
├── 20250627_080030__Camera__DSC_001__48.8566,2.3522_.jpg
├── 20250627_080045__Drone__DJI_001__48.8566,2.3522_.jpg
├── 20250627_120000__Phone1__IMG_002__48.8566,2.3522_.jpg
├── 20250627_120015__Phone2__PXL_002__48.8566,2.3522_.jpg
├── 20250627_120030__Camera__DSC_002__48.8566,2.3522_.jpg
├── 20250627_120045__Drone__DJI_002__48.8566,2.3522_.jpg
└── gps_positions.csv
```

### Benefits:
1. **Chronological order** for slideshow creation
2. **Device identification** in filenames
3. **GPS coordinates** for route tracking
4. **Single folder** for easy slideshow software import
5. **Consistent naming** across all devices

## Output

### Progress Display
- Progress bar for image analysis
- Progress bar for copy process
- Detailed information for each copied file

### Statistics at the End
```
============================================================
STATISTICS
============================================================
Total image files found: 1114
Successfully copied: 1114
Copy errors: 0

Data sources:
  - EXIF data used: 1112 (99.8%)
  - Filesystem date used: 2 (0.2%)
  - Current date used: 0 (0.0%)
  - GPS data found: 774 (69.5%)
============================================================
```

### CSV Export (with --gps)
```
GPS position data saved in: /path/to/destination/gps_positions.csv
CSV file contains 774 entries for Google Maps import
```

## Requirements

- Python 3.6+
- Pillow (PIL) for image processing
- tqdm for progress bars

## Error Handling

- Automatic fallback mechanisms for missing EXIF data
- Robust GPS extraction with various formats
- Unique filenames through automatic counters
- Detailed error messages

## Notes

- Sorting is done **only by date** - GPS and directory have no influence
- GPS coordinates are placed **at the end** of filename
- Subfolder names are only extracted from the first subdirectory
- The CSV file is directly importable to Google Maps

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)

## How It Works

1. The script recursively searches the source directory for image files
2. For each image, it attempts to extract the EXIF capture date
3. If no EXIF date is available, it uses the filesystem creation date
4. All images are sorted by date (oldest first)
5. Images are copied to the destination directory and renamed
6. In case of naming conflicts, a counter is automatically added

## License

This project is under the MIT License.
