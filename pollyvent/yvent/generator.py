import textwrap
from .base import ImageComposer, parse_event_data
from .layouts.centered import CenteredLayout
from .layouts import get_layout
from PIL import ImageFont

def generate_flyer_from_args(args):
    gradient = (
        tuple(args.gradient.split(',')) if hasattr(args, "gradient") and args.gradient else None
    )

    return generate_flyer(
        title=args.title,
        dt_str=args.datetime,
        location=args.location,
        qr_text=args.qr_text,
        logo_path=args.logo_path,
        font_path=args.font_path,
        output_path=args.output_path,
        gradient=gradient,
    )


def generate_flyer(title, dt_str, location, qr_text, logo_path, font_path, output_path, gradient=None, layout_name="diagonal"):
    data = parse_event_data(
        title=title,
        dt_str=dt_str,
        location=location,
        qr_text=qr_text,
        logo_path=logo_path,
        font_path=font_path,
        output_path=output_path,
    )
    # Set up the canvas
    gradient = gradient or ("white", "blue", "vertical")
    composer = ImageComposer(gradient=gradient)

    # Use the layout system
    layout = get_layout(layout_name);
    layout.render(composer, data)

    # Save the final image
    composer.save_to(data["output_path"])


