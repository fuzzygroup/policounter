import argparse
from pathlib import Path
from yvent.generator import generate_flyer_from_args

def get_parser():
    parser = argparse.ArgumentParser(
        description="Generate a custom event flier with QR code and branding."
    )
    parser.add_argument('--title', required=True, help='Title of the event')
    parser.add_argument('--datetime', required=True, help='Date and time of the event (e.g., 2025-06-15T18:30)')
    parser.add_argument('--location', required=True, help='Location of the event')
    parser.add_argument('--qr-text', required=True, help='Text to encode in the QR code')
    parser.add_argument('--logo-path', type=Path, required=True, help='Path to the logo image file')
    parser.add_argument('--font-path', type=Path, required=True, help='Path to the font file (e.g., .ttf)')
    parser.add_argument('--output-path', type=Path, required=True, help='Path to save the output image or PDF')
    return parser

def main():
    args = get_parser().parse_args()
    generate_flyer_from_args(args)

if __name__ == '__main__':
    main()
