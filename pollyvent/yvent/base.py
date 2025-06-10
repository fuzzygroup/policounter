import math
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import qrcode


DEFAULT_WIDTH = 1570
DEFAULT_HEIGHT = 2048
DEFAULT_MARGIN = 60


def parse_event_data(title: str, dt_str: str, location: str, qr_text: str, logo_path: Path, font_path: Path, output_path: Path):
    event_datetime = datetime.fromisoformat(dt_str)
    logo_path = Path(logo_path).resolve()
    font_path = Path(font_path).resolve()
    output_path = Path(output_path).resolve()

    return {
        "title": title,
        "datetime": event_datetime,
        "location": location,
        "qr_text": qr_text,
        "logo_path": logo_path,
        "font_path": font_path,
        "output_path": output_path,
    }


class ImageComposer:
    def __init__(self, output_width=DEFAULT_WIDTH, output_height=DEFAULT_HEIGHT, background_color='white', margin=DEFAULT_MARGIN, gradient=None):
        self.width = output_width
        self.height = output_height
        self.margin = margin

        if gradient:
            self.canvas = self.create_gradient_background(*gradient)
        else:
            self.canvas = Image.new('RGB', (self.width, self.height), background_color)

        self.draw = ImageDraw.Draw(self.canvas)

    def create_gradient_background(self, from_color, to_color, direction='vertical'):
        base = Image.new('RGB', (self.width, self.height), from_color)
        top = Image.new('RGB', (self.width, self.height), to_color)
        mask = Image.new('L', (self.width, self.height))
        mask_data = []

        if direction == 'vertical':
            for y in range(self.height):
                mask_data.extend([int(255 * (y / self.height))] * self.width)
        else:  # horizontal
            for y in range(self.height):
                row = [int(255 * (x / self.width)) for x in range(self.width)]
                mask_data.extend(row)

        mask.putdata(mask_data)
        gradient = Image.composite(top, base, mask)
        return gradient

    def add_overlay(self, png_path, x, y, scale_to=None):
        overlay = Image.open(png_path).convert('RGBA')
        if scale_to:
            overlay.thumbnail((scale_to, scale_to))
        self.canvas.paste(overlay, (x, y), overlay)

    def find_fitting_font(self, text, font_path, max_width, max_height, starting_size=140, angle=45):
        size = starting_size
        while size > 10:
            font = ImageFont.truetype(font_path, size)
            dummy_img = Image.new("RGBA", (1, 1))
            draw = ImageDraw.Draw(dummy_img)
            bbox = draw.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]

            # Rotate dims
            rotated_w = abs(w * math.cos(math.radians(angle))) + abs(h * math.sin(math.radians(angle)))
            rotated_h = abs(w * math.sin(math.radians(angle))) + abs(h * math.cos(math.radians(angle)))

            if rotated_w <= max_width and rotated_h <= max_height:
                return font
            size -= 4  # shrink step
        return ImageFont.truetype(font_path, 10)  # fallback


    def add_text(self, text, x, y, font=None, font_size=48, color='black', rotate=0, anchor="lt"):
        font = font or ImageFont.truetype("DejaVuSans.ttf", font_size)

        bbox = self.draw.textbbox((0, 0), text, font=font, anchor=anchor)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        # Create transparent image
        text_img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        draw = ImageDraw.Draw(text_img)
        draw.text((w // 2, h // 2) if anchor == "mm" else (0, 0), text, font=font, fill=color, anchor=anchor)

        if rotate:
            text_img = text_img.rotate(rotate, expand=True)

        paste_x = x - (text_img.width // 2 if anchor == "mm" else 0)
        paste_y = y - (text_img.height // 2 if anchor == "mm" else 0)

        self.canvas.paste(text_img, (paste_x, paste_y), text_img)

    def measure_text(self, text, font):
        bbox = self.draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height

    def add_qr_code(self, qr_text, x, y, max_size=400, border_modules=4):
        # Temporary QR object to get module count
        test_qr = qrcode.QRCode(border=border_modules)
        test_qr.add_data(qr_text)
        test_qr.make(fit=True)

        num_modules = test_qr.modules_count
        total_modules = num_modules + 2 * border_modules
        pixel_size = max(1, max_size // total_modules)

        # Now create QR with correct pixel size
        qr = qrcode.QRCode(
            box_size=pixel_size,
            border=border_modules,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        self.canvas.paste(img, (x, y), img)
        return img.width


    def save_to(self, path):
        self.canvas.save(path)
