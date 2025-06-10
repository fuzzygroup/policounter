import textwrap
from .base import ImageComposer, parse_event_data
from PIL import ImageFont

def generate_flyer_from_args(args):
    return generate_flyer(
        title=args.title,
        dt_str=args.datetime,
        location=args.location,
        qr_text=args.qr_text,
        logo_path=args.logo_path,
        font_path=args.font_path,
        output_path=args.output_path,
    )

def generate_flyer(title, dt_str, location, qr_text, logo_path, font_path, output_path):
    data = parse_event_data(
        title=title,
        dt_str=dt_str,
        location=location,
        qr_text=qr_text,
        logo_path=logo_path,
        font_path=font_path,
        output_path=output_path,
    )

    event_date = data["datetime"].strftime("%B %d, %Y")
    event_time = data["datetime"].strftime("%I:%M %p").lstrip('0')

    composer = ImageComposer(gradient=("white", "blue", "vertical"))
    composer.add_overlay(data["logo_path"], x=composer.margin, y=composer.margin, scale_to=750)

    title_font = composer.find_fitting_font(
        data["title"],
        str(data["font_path"]),
        max_width=composer.width - 2 * composer.margin,
        max_height=composer.height - 2 * composer.margin
    )

    info_font = ImageFont.truetype(str(data["font_path"]), 48)
    location_font = ImageFont.truetype(str(data["font_path"]), 38)

    center_x = composer.width // 2
    center_y = composer.height // 2
    composer.add_text(data["title"], x=center_x, y=center_y, font=title_font, rotate=45, anchor="mm")

    qr_box_size = 400
    qr_visual_padding = 60
    qr_margin = composer.margin + qr_visual_padding
    qr_x = composer.width - qr_box_size - qr_margin
    qr_y = composer.height - qr_box_size - qr_margin
    qr_img_width = 0

    if data["qr_text"]:
        qr_img_width = composer.add_qr_code(data["qr_text"], x=qr_x, y=qr_y)

    wrapped_location_lines = textwrap.wrap(data["location"], width=40)
    info_lines = [
        (event_date, info_font),
        (event_time, info_font),
    ] + [(line, location_font) for line in wrapped_location_lines]

    spacing = 10
    total_info_height = sum(
        composer.draw.textbbox((0, 0), text, font=font)[3] - composer.draw.textbbox((0, 0), text, font=font)[1]
        + spacing for text, font in info_lines
    ) - spacing

    current_y = qr_y - total_info_height - (spacing * 2)

    for text, font in info_lines:
        bbox = composer.draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_x = qr_x + qr_img_width - text_w
        composer.add_text(text, x=text_x, y=current_y, font=font)
        current_y += bbox[3] - bbox[1] + spacing

    composer.save_to(data["output_path"])
