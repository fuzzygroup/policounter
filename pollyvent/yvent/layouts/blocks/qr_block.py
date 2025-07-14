def render_qr_code(composer, qr_text, x, y, max_size=400):
    """
    Render a high-correction QR code at (x, y), scaled to fit within max_size.
    Returns the width of the generated image for downstream layout logic.
    """
    return composer.add_qr_code(qr_text, x=x, y=y, max_size=max_size)

