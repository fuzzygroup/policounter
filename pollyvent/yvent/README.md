# Yvent — Event Flier Generator

**Yvent** is a minimal Python CLI tool that generates printable event fliers with QR codes, logos, and custom fonts. It uses [Pillow](https://python-pillow.org) and [qrcode](https://pypi.org/project/qrcode/) to render styled posters, making it perfect for quick, local flyer generation without external dependencies like ImageMagick.

## Features

- Custom event title, date, time, and location
- Diagonal title text overlay
- Embedded logo
- QR code generation
- Gradient or solid background
- Custom font support

## Requirements

- Python 3.7+
- [Pillow](https://pypi.org/project/Pillow/)
- [qrcode](https://pypi.org/project/qrcode/)

Install dependencies:

```bash
pip install Pillow qrcode
```

## Usage

Run the script with your event data:

```bash
python -m yvent \
  --title "Test Event" \
  --datetime 2025-06-15T18:30 \
  --location "Test Location" \
  --qr-text "https://example.com" \
  --logo-path "assets/flierlogo.png" \
  --font-path "assets/break-down.ttf" \
  --output-path "output/event.png"
```

## Arguments

| Argument        | Description                                        |
| --------------- | -------------------------------------------------- |
| `--title`       | Event title                                        |
| `--datetime`    | ISO8601 datetime string (e.g., `2025-06-15T18:30`) |
| `--location`    | Event location                                     |
| `--qr-text`     | Text or URL to embed in QR code                    |
| `--logo-path`   | Path to logo image (PNG recommended)               |
| `--font-path`   | Path to `.ttf` font file                           |
| `--output-path` | Output image path (`.png`)                         |
