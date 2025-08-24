#!/usr/bin/env python3
"""
PictureSort - Bildsortierung nach Datum

Ein Skript zum automatischen Sortieren und Umbenennen von Bildern
basierend auf ihrem Aufnahmedatum.
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
    print(f"Fehler: Benötigte Bibliothek nicht gefunden: {e}")
    print("Bitte installiere die Abhängigkeiten mit: pip install -r requirements.txt")
    sys.exit(1)


class ImageSorter:
    """Hauptklasse für die Bildsortierung."""
    
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
        # Liste für GPS-Daten für CSV-Export
        self.gps_data = []
        
    def find_image_files(self) -> List[Path]:
        """Findet alle Bilddateien im Quellverzeichnis rekursiv."""
        image_files = []
        
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Quellverzeichnis existiert nicht: {self.source_dir}")
            
        print(f"Durchsuche Verzeichnis: {self.source_dir}")
        
        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                image_files.append(file_path)
                
        print(f"Gefunden: {len(image_files)} Bilddateien")
        self.stats['total_files'] = len(image_files)
        return image_files
    
    def get_gps_coordinates(self, image_path: Path) -> Optional[Tuple[float, float]]:
        """Extrahiert GPS-Koordinaten aus einem Bild."""
        if not self.include_gps:
            return None
            
        try:
            with Image.open(image_path) as img:
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    
                    # GPS-Tags finden
                    gps_tags = {}
                    for tag_id in exif:
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        if isinstance(tag, str) and tag.startswith('GPS'):
                            gps_tags[tag] = exif[tag_id]
                    
                    # GPS-Koordinaten extrahieren
                    if 'GPSLatitude' in gps_tags and 'GPSLongitude' in gps_tags:
                        try:
                            lat = self._convert_to_degrees(gps_tags['GPSLatitude'])
                            lon = self._convert_to_degrees(gps_tags['GPSLongitude'])
                            
                            # GPS-Latitude-Referenz berücksichtigen
                            if 'GPSLatitudeRef' in gps_tags and gps_tags['GPSLatitudeRef'] == 'S':
                                lat = -lat
                            
                            # GPS-Longitude-Referenz berücksichtigen
                            if 'GPSLongitudeRef' in gps_tags and gps_tags['GPSLongitudeRef'] == 'W':
                                lon = -lon
                            
                            self.stats['gps_files'] += 1
                            return (lat, lon)
                        except Exception as e:
                            print(f"Fehler bei GPS-Konvertierung für {image_path}: {e}")
                    
                    # Alternative: GPSInfo-Format (wie in den Debug-Ausgaben gesehen)
                    elif 'GPSInfo' in gps_tags:
                        gps_info = gps_tags['GPSInfo']
                        try:
                            # GPSInfo hat die Struktur: {1: 'N', 2: (lat_deg, lat_min, lat_sec), 3: 'E', 4: (lon_deg, lon_min, lon_sec)}
                            if 2 in gps_info and 4 in gps_info:
                                lat_dms = gps_info[2]  # (degrees, minutes, seconds)
                                lon_dms = gps_info[4]  # (degrees, minutes, seconds)
                                
                                lat = self._convert_to_degrees(lat_dms)
                                lon = self._convert_to_degrees(lon_dms)
                                
                                # Referenz berücksichtigen
                                if 1 in gps_info and gps_info[1] == 'S':
                                    lat = -lat
                                if 3 in gps_info and gps_info[3] == 'W':
                                    lon = -lon
                                
                                self.stats['gps_files'] += 1
                                return (lat, lon)
                        except Exception as e:
                            print(f"Fehler bei GPSInfo-Konvertierung für {image_path}: {e}")
                        
        except Exception as e:
            print(f"Warnung: Konnte GPS-Daten nicht lesen für {image_path}: {e}")
        
        return None
    
    def _convert_to_degrees(self, dms) -> float:
        """Konvertiert GPS-Koordinaten von DMS (Degrees, Minutes, Seconds) zu Dezimalgrad."""
        degrees = float(dms[0])
        minutes = float(dms[1])
        seconds = float(dms[2])
        
        return degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    def get_image_date(self, image_path: Path) -> Tuple[datetime, str]:
        """Extrahiert das Aufnahmedatum aus einem Bild und gibt Datum und Quelle zurück."""
        try:
            with Image.open(image_path) as img:
                # Versuche Exif-Daten zu lesen
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    
                    # Suche nach dem DateTime-Original Tag
                    for tag_id in exif:
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        if tag == 'DateTimeOriginal':
                            date_str = exif[tag_id]
                            try:
                                # Parse Exif-Datum (Format: YYYY:MM:DD HH:MM:SS)
                                date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                                self.stats['exif_files'] += 1
                                return date, f"EXIF: {date_str}"
                            except ValueError:
                                pass
                                
        except Exception as e:
            print(f"Warnung: Konnte Exif-Daten nicht lesen für {image_path}: {e}")
        
        # Fallback: Verwende Dateisystem-Erstellungsdatum
        try:
            stat = image_path.stat()
            # Verwende das früheste verfügbare Datum
            date = datetime.fromtimestamp(min(stat.st_ctime, stat.st_mtime))
            self.stats['filesystem_date_files'] += 1
            return date, f"Dateisystem: {date.strftime('%Y-%m-%d %H:%M:%S')}"
        except Exception as e:
            print(f"Warnung: Konnte Dateisystem-Datum nicht lesen für {image_path}: {e}")
            # Letzter Fallback: Aktuelles Datum
            date = datetime.now()
            self.stats['current_date_files'] += 1
            return date, f"Aktuelles Datum: {date.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def get_subfolder_name(self, image_path: Path) -> str:
        """Extrahiert den Namen des Unterordners relativ zum Quellverzeichnis."""
        if not self.include_dir:
            return ""
            
        try:
            # Relativer Pfad vom Quellverzeichnis
            relative_path = image_path.relative_to(self.source_dir)
            
            # Wenn das Bild direkt im Quellverzeichnis liegt
            if relative_path.parent == Path('.'):
                return ""
            
            # Ersten Unterordner-Namen extrahieren
            subfolder = relative_path.parts[0]
            return f"_{subfolder}_"
            
        except Exception:
            return ""
    
    def generate_new_filename(self, original_path: Path, date: datetime, gps_coords: Optional[Tuple[float, float]] = None, subfolder: str = "") -> str:
        """Generiert einen neuen Dateinamen basierend auf dem Datum, GPS und Unterordner."""
        date_str = date.strftime('%Y%m%d_%H%M%S')
        original_name = original_path.stem
        extension = original_path.suffix.lower()
        
        # Entferne ungültige Zeichen aus dem Dateinamen
        safe_name = re.sub(r'[^\w\-_.]', '_', original_name)
        
        # Baue Dateinamen zusammen - GPS kommt ans Ende
        filename_parts = [date_str]
        
        if subfolder:
            filename_parts.append(subfolder)
        
        filename_parts.append(safe_name)
        
        # GPS-Koordinaten ans Ende setzen
        if gps_coords:
            lat, lon = gps_coords
            filename_parts.append(f"_{lat:.6f},{lon:.6f}_")
        
        return f"{'_'.join(filename_parts)}{extension}"
    
    def get_unique_filename(self, base_filename: str) -> str:
        """Stellt sicher, dass der Dateiname im Zielverzeichnis eindeutig ist."""
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
        """Erstellt eine CSV-Datei mit GPS-Daten für Google Maps Import."""
        if not self.gps_data:
            print("Keine GPS-Daten gefunden - CSV-Datei wird nicht erstellt.")
            return
            
        csv_filename = self.dest_dir / "gps_positions.csv"
        
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header für Google Maps Import
                writer.writerow(['Name', 'Latitude', 'Longitude', 'Description'])
                
                # GPS-Daten schreiben
                for filename, lat, lon, date_str in self.gps_data:
                    description = f"Foto aufgenommen am {date_str}"
                    writer.writerow([filename, lat, lon, description])
                    
            print(f"GPS-Positionsdaten gespeichert in: {csv_filename}")
            print(f"CSV-Datei enthält {len(self.gps_data)} Einträge für Google Maps Import")
            
        except Exception as e:
            print(f"Fehler beim Erstellen der CSV-Datei: {e}")
    
    def print_statistics(self) -> None:
        """Gibt eine detaillierte Statistik aus."""
        print("\n" + "="*60)
        print("STATISTIK")
        print("="*60)
        print(f"Gesamte Bilddateien gefunden: {self.stats['total_files']}")
        print(f"Erfolgreich kopiert: {self.stats['copied_files']}")
        print(f"Fehler beim Kopieren: {self.stats['error_files']}")
        print()
        print("Datenquellen:")
        print(f"  - EXIF-Daten verwendet: {self.stats['exif_files']} ({self.stats['exif_files']/max(1, self.stats['total_files'])*100:.1f}%)")
        print(f"  - Dateisystem-Datum verwendet: {self.stats['filesystem_date_files']} ({self.stats['filesystem_date_files']/max(1, self.stats['total_files'])*100:.1f}%)")
        print(f"  - Aktuelles Datum verwendet: {self.stats['current_date_files']} ({self.stats['current_date_files']/max(1, self.stats['total_files'])*100:.1f}%)")
        if self.include_gps:
            print(f"  - GPS-Daten gefunden: {self.stats['gps_files']} ({self.stats['gps_files']/max(1, self.stats['total_files'])*100:.1f}%)")
        print("="*60)
    
    def sort_images(self) -> None:
        """Hauptfunktion zum Sortieren der Bilder."""
        # Erstelle Zielverzeichnis falls es nicht existiert
        self.dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Finde alle Bilddateien
        image_files = self.find_image_files()
        
        if not image_files:
            print("Keine Bilddateien gefunden.")
            return
        
        # Sammle Bilder mit ihren Daten
        print("Analysiere Bilddaten...")
        images_with_data = []
        
        for image_path in tqdm(image_files, desc="Analysiere Bilder"):
            try:
                date, source = self.get_image_date(image_path)
                gps_coords = self.get_gps_coordinates(image_path)
                subfolder = self.get_subfolder_name(image_path)
                images_with_data.append((image_path, date, source, gps_coords, subfolder))
            except Exception as e:
                print(f"Fehler beim Analysieren von {image_path}: {e}")
                self.stats['error_files'] += 1
        
        # Sortiere nach Datum (älteste zuerst) - GPS und Verzeichnis haben keinen Einfluss
        images_with_data.sort(key=lambda x: x[1])
        
        # Kopiere und benenne um
        print(f"Kopiere {len(images_with_data)} Bilder...")
        
        for image_path, date, source, gps_coords, subfolder in tqdm(images_with_data, desc="Kopiere Bilder"):
            try:
                new_filename = self.generate_new_filename(image_path, date, gps_coords, subfolder)
                unique_filename = self.get_unique_filename(new_filename)
                dest_path = self.dest_dir / unique_filename
                
                shutil.copy2(image_path, dest_path)
                
                # GPS-Daten für CSV sammeln
                if gps_coords and self.include_gps:
                    lat, lon = gps_coords
                    date_str = date.strftime('%Y-%m-%d %H:%M:%S')
                    self.gps_data.append((unique_filename, lat, lon, date_str))
                
                # Erstelle Info-String für Ausgabe
                info_parts = [source]
                if gps_coords:
                    lat, lon = gps_coords
                    info_parts.append(f"GPS: {lat:.6f},{lon:.6f}")
                if subfolder:
                    info_parts.append(f"Ordner: {subfolder.strip('_')}")
                
                info_str = " | ".join(info_parts)
                print(f"Kopiert: {image_path.name} -> {unique_filename} ({info_str})")
                self.stats['copied_files'] += 1
                
            except Exception as e:
                print(f"Fehler beim Kopieren von {image_path}: {e}")
                self.stats['error_files'] += 1
        
        print(f"\nFertig! {self.stats['copied_files']} Bilder wurden sortiert und kopiert.")
        print(f"Zielverzeichnis: {self.dest_dir}")
        
        # Erstelle CSV-Datei für GPS-Daten
        if self.include_gps:
            self.create_gps_csv()
        
        # Zeige Statistik
        self.print_statistics()


def main():
    """Hauptfunktion mit Kommandozeilen-Interface."""
    parser = argparse.ArgumentParser(
        description="Sortiert Bilder nach ihrem Aufnahmedatum und kopiert sie in ein Zielverzeichnis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python sort_images_by_date.py --source ~/Bilder/Unsortiert --dest ~/Bilder/Sortiert
  python sort_images_by_date.py --source /media/fotos --dest ./sortiert --gps
  python sort_images_by_date.py --source /media/fotos --dest ./sortiert --gps --dir
        """
    )
    
    parser.add_argument(
        '--source',
        required=True,
        help='Pfad zum Quellverzeichnis (rekursiv alle Bilder in Unterordnern finden)'
    )
    
    parser.add_argument(
        '--dest',
        required=True,
        help='Pfad zum Zielverzeichnis, in das alle sortierten Bilder kopiert werden'
    )
    
    parser.add_argument(
        '--gps',
        action='store_true',
        help='GPS-Koordinaten in den Dateinamen einbetten (Format: _lat,lon_ am Ende) und CSV-Datei erstellen'
    )
    
    parser.add_argument(
        '--dir',
        action='store_true',
        help='Unterordner-Namen in den Dateinamen einbetten'
    )
    
    args = parser.parse_args()
    
    try:
        sorter = ImageSorter(args.source, args.dest, args.gps, args.dir)
        sorter.sort_images()
    except KeyboardInterrupt:
        print("\nAbgebrochen durch Benutzer.")
        sys.exit(1)
    except Exception as e:
        print(f"Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 