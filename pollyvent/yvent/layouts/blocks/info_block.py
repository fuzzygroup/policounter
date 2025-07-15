import textwrap
from PIL import ImageFont

def render_info_block(
    composer,
    data,
    x,
    y,
    spacing=10,
    info_font_sz=48,
    loc_font_sz=38,
    wrap_width=40
):
    """
    Renders date, time, and location info starting at (x, y), top-left aligned.

    Returns:
        A tuple (x, y, width, height) representing the bounding box of the entire info block.
    """
    event_date = data["datetime"].strftime("%B %d, %Y")
    event_time = data["datetime"].strftime("%I:%M %p").lstrip('0')

    font_path = str(data["font_path"])
    info_font = ImageFont.truetype(font_path, info_font_sz)
    location_font = ImageFont.truetype(font_path, loc_font_sz)

    wrapped_location_lines = textwrap.wrap(data["location"], width=wrap_width)
    lines = [
        (event_date, info_font),
        (event_time, info_font),
    ] + [(line, location_font) for line in wrapped_location_lines]

    current_y = y
    max_line_width = 0

    for text, font in lines:
        bbox = composer.draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        composer.add_text(text, x=x, y=current_y, font=font)
        current_y += text_height + spacing

        max_line_width = max(max_line_width, text_width)

    total_height = current_y - y - spacing
    return (x, y, max_line_width, total_height)

