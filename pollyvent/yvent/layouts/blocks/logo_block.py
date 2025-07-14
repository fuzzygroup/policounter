def render_logo(composer, logo_path, x, y, max_width=750):
    """
    Paste the logo image at the specified (x, y) position, scaled down to max_width if needed.
    """
    composer.add_overlay(logo_path, x=x, y=y, scale_to=max_width)

