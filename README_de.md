# PictureSort - Bildsortierung nach Datum

Ein Python-Skript zum automatischen Sortieren und Umbenennen von Bildern basierend auf ihrem Aufnahmedatum.

> **🇺🇸 English version available**: [README.md](README.md)

## Anwendungsfall: Urlaubsbilder und Slideshow-Vorbereitung

Dieses Skript ist besonders nützlich, um Urlaubsbilder von mehreren Geräten (Telefone, Kameras, Drohnen, etc.) in eine chronologisch geordnete Sammlung für die Slideshow-Erstellung zu organisieren. Übergeben Sie einfach den Ordner mit allen Ihren Urlaubsbildern in Unterordnern an das Skript, und es erstellt eine chronologisch geordnete Sequenz in einem Export-Ordner basierend auf den Aufnahmedaten. Es ist auch möglich, eine CSV-Datei aus GPS-Tags zu generieren, um Ihre Route später über Google Maps zu verfolgen.

### Perfekt für:
- **Urlaubsbilder** von mehreren Geräten
- **Event-Fotografie** mit mehreren Fotografen
- **Drohnen-Aufnahmen** gemischt mit Bodenfotos
- **Familienreisen** mit Fotos von verschiedenen Telefonen
- **Professionelle Aufnahmen** mit mehreren Kameras
- **Chronologische Slideshows** erstellen
- **Routen-Tracking** über Google Maps

## Features

- Rekursive Suche nach Bilddateien (.jpg, .jpeg, .png)
- Extraktion des EXIF-Aufnahmedatums aus Bildern
- Fallback auf Dateisystem-Erstellungsdatum wenn kein Exif vorhanden
- Sortierung nach Datum (älteste zuerst)
- Automatische Umbenennung im Format: `YYYYMMDD_HHMMSS_originalfilename.jpg`
- **GPS-Koordinaten im Dateinamen** (optional, am Ende des Dateinamens)
- **Unterordner-Namen im Dateinamen** (optional)
- **CSV-Export für Google Maps Import** (bei GPS-Aktivierung)
- Vermeidung von Dateinamen-Konflikten durch Zähler
- Fortschrittsbalken für bessere Benutzerfreundlichkeit
- Detaillierte Statistik am Ende

## Installation

1. Klone oder lade das Repository herunter
2. Installiere die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```

## Verwendung

### Grundlegende Verwendung
```bash
python sort_images_by_date.py --source /pfad/zu/quellordner --dest /pfad/zu/zielordner
```

### Mit GPS-Koordinaten
```bash
python sort_images_by_date.py --source /pfad/zu/quellordner --dest /pfad/zu/zielordner --gps
```

### Mit Unterordner-Namen
```bash
python sort_images_by_date.py --source /pfad/zu/quellordner --dest /pfad/zu/zielordner --dir
```

### Mit GPS und Unterordner-Namen
```bash
python sort_images_by_date.py --source /pfad/zu/quellordner --dest /pfad/zu/zielordner --gps --dir
```

## Kommandozeilen-Optionen

### Erforderliche Optionen
- `--source SOURCE`: Pfad zum Quellverzeichnis (rekursiv alle Bilder in Unterordnern finden)
- `--dest DEST`: Pfad zum Zielverzeichnis, in das alle sortierten Bilder kopiert werden

### Optionale Optionen
- `--gps`: GPS-Koordinaten in den Dateinamen einbetten (Format: _lat,lon_ am Ende) und CSV-Datei erstellen
- `--dir`: Unterordner-Namen in den Dateinamen einbetten
- `-h, --help`: Zeigt die Hilfe-Nachricht an

## Dateinamen-Formate

### Grundformat
```
YYYYMMDD_HHMMSS_originalfilename.jpg
```

### Mit Unterordner-Namen
```
YYYYMMDD_HHMMSS__unterordner__originalfilename.jpg
```

### Mit GPS-Koordinaten
```
YYYYMMDD_HHMMSS_originalfilename__lat,lon_.jpg
```

### Mit Unterordner und GPS
```
YYYYMMDD_HHMMSS__unterordner__originalfilename__lat,lon_.jpg
```

## GPS-Funktionen

### GPS im Dateinamen
- **Format**: `_51.324867,12.575267_` (direkt für Google Maps kopierbar)
- **Position**: Am Ende des Dateinamens
- **Präzision**: 6 Dezimalstellen

### CSV-Export für Google Maps
Bei Aktivierung von `--gps` wird automatisch eine `gps_positions.csv` Datei erstellt:
- **Datei**: `gps_positions.csv` im Zielverzeichnis
- **Format**: `Name,Latitude,Longitude,Description`
- **Import**: Direkt in Google Maps importierbar
- **Beschreibung**: Enthält Aufnahmedatum und -zeit

## Beispiele

### Beispiel 1: Grundlegende Sortierung
```bash
python sort_images_by_date.py --source ~/Bilder/Unsortiert --dest ~/Bilder/Sortiert
```
**Ergebnis**: `20250627_185246_PXL_20250627_165246421.jpg`

### Beispiel 2: Mit GPS-Koordinaten
```bash
python sort_images_by_date.py --source ~/Bilder/Unsortiert --dest ~/Bilder/Sortiert --gps
```
**Ergebnis**: `20250627_185246_PXL_20250627_165246421__51.324867,12.575267_.jpg`
**Zusätzlich**: `gps_positions.csv` wird erstellt

### Beispiel 3: Mit Unterordner-Namen
```bash
python sort_images_by_date.py --source ~/Bilder/Unsortiert --dest ~/Bilder/Sortiert --dir
```
**Ergebnis**: `20250627_185246__input__PXL_20250627_165246421.jpg`

### Beispiel 4: Vollständige Funktionen
```bash
python sort_images_by_date.py --source ~/Bilder/Unsortiert --dest ~/Bilder/Sortiert --gps --dir
```
**Ergebnis**: `20250627_185246__input__PXL_20250627_165246421__51.324867,12.575267_.jpg`
**Zusätzlich**: `gps_positions.csv` wird erstellt

## Urlaubsbilder-Workflow-Beispiel

### Szenario: Europäische Rundreise
Sie haben Fotos von:
- **Telefon 1**: Familienfotos und Schnappschüsse
- **Telefon 2**: Partner-Telefon mit verschiedenen Perspektiven
- **Kamera**: Hochwertige Landschaftsaufnahmen
- **Drohne**: Luftaufnahmen von Städten und Landschaften

### Ordnerstruktur vorher:
```
Urlaub_2025/
├── Telefon1/
│   ├── IMG_001.jpg
│   ├── IMG_002.jpg
│   └── ...
├── Telefon2/
│   ├── PXL_001.jpg
│   ├── PXL_002.jpg
│   └── ...
├── Kamera/
│   ├── DSC_001.jpg
│   ├── DSC_002.jpg
│   └── ...
└── Drohne/
    ├── DJI_001.jpg
    ├── DJI_002.jpg
    └── ...
```

### Befehl:
```bash
python sort_images_by_date.py --source ~/Urlaub_2025 --dest ~/Urlaub_2025_Sortiert --gps --dir
```

### Ergebnis:
```
Urlaub_2025_Sortiert/
├── 20250627_080000__Telefon1__IMG_001__48.8566,2.3522_.jpg
├── 20250627_080015__Telefon2__PXL_001__48.8566,2.3522_.jpg
├── 20250627_080030__Kamera__DSC_001__48.8566,2.3522_.jpg
├── 20250627_080045__Drohne__DJI_001__48.8566,2.3522_.jpg
├── 20250627_120000__Telefon1__IMG_002__48.8566,2.3522_.jpg
├── 20250627_120015__Telefon2__PXL_002__48.8566,2.3522_.jpg
├── 20250627_120030__Kamera__DSC_002__48.8566,2.3522_.jpg
├── 20250627_120045__Drohne__DJI_002__48.8566,2.3522_.jpg
└── gps_positions.csv
```

### Vorteile:
1. **Chronologische Reihenfolge** für Slideshow-Erstellung
2. **Geräte-Identifikation** in Dateinamen
3. **GPS-Koordinaten** für Routen-Tracking
4. **Einzelner Ordner** für einfachen Slideshow-Software-Import
5. **Konsistente Benennung** über alle Geräte hinweg

## Ausgabe

### Fortschrittsanzeige
- Fortschrittsbalken für Bildanalyse
- Fortschrittsbalken für Kopiervorgang
- Detaillierte Informationen für jede kopierte Datei

### Statistik am Ende
```
============================================================
STATISTIK
============================================================
Gesamte Bilddateien gefunden: 1114
Erfolgreich kopiert: 1114
Fehler beim Kopieren: 0

Datenquellen:
  - EXIF-Daten verwendet: 1112 (99.8%)
  - Dateisystem-Datum verwendet: 2 (0.2%)
  - Aktuelles Datum verwendet: 0 (0.0%)
  - GPS-Daten gefunden: 774 (69.5%)
============================================================
```

### CSV-Export (bei --gps)
```
GPS-Positionsdaten gespeichert in: /pfad/zu/zielordner/gps_positions.csv
CSV-Datei enthält 774 Einträge für Google Maps Import
```

## Anforderungen

- Python 3.6+
- Pillow (PIL) für Bildverarbeitung
- tqdm für Fortschrittsbalken

## Fehlerbehandlung

- Automatische Fallback-Mechanismen für fehlende Exif-Daten
- Robuste GPS-Extraktion mit verschiedenen Formaten
- Eindeutige Dateinamen durch automatische Zähler
- Detaillierte Fehlermeldungen

## Hinweise

- Die Sortierung erfolgt **nur nach Datum** - GPS und Verzeichnis haben keinen Einfluss
- GPS-Koordinaten werden **am Ende** des Dateinamens platziert
- Unterordner-Namen werden nur vom ersten Unterverzeichnis extrahiert
- Die CSV-Datei ist direkt in Google Maps importierbar

## Unterstützte Bildformate

- JPEG (.jpg, .jpeg)
- PNG (.png)

## Wie es funktioniert

1. Das Skript durchsucht rekursiv das Quellverzeichnis nach Bilddateien
2. Für jedes Bild wird versucht, das EXIF-Aufnahmedatum zu extrahieren
3. Falls kein EXIF-Datum vorhanden ist, wird das Dateisystem-Erstellungsdatum verwendet
4. Alle Bilder werden nach Datum sortiert (älteste zuerst)
5. Die Bilder werden in das Zielverzeichnis kopiert und umbenannt
6. Bei Namenskonflikten wird automatisch ein Zähler hinzugefügt

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
