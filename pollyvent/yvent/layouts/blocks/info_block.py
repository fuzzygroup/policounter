import textwrap
from PIL import ImageFont

def render_info_block(composer, data, qr_x, qr_y, qr_width, spacing=10):
    """
    Renders date, time, and location info above the QR code.
    Positions the info text to align right with the QR code.
    """
    event_date = data["datetime"].strftime("%B %d, %Y")
    event_time = data["datetime"].strftime("%I:%M %p").lstrip('0')

    font_path = str(data["font_path"])
    info_font = ImageFont.truetype(font_path, 48)
    location_font = ImageFont.truetype(font_path, 38)

    wrapped_location_lines = textwrap.wrap(data["location"], width=40)
    info_lines = [
        (event_date, info_font),
        (event_time, info_font),
    ] + [(line, location_font) for line in wrapped_location_lines]

    total_info_height = sum(
        composer.draw.textbbox((0, 0), text, font=font)[3] -
        composer.draw.textbbox((0, 0), text, font=font)[1]
        + spacing for text, font in info_lines
    ) - spacing

    current_y = qr_y - total_info_height - spacing * 2

    for text, font in info_lines:
        bbox = composer.draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = qr_x + qr_width - text_width
        composer.add_text(text, x=text_x, y=current_y, font=font)
        current_y += bbox[3] - bbox[1] + spacing

