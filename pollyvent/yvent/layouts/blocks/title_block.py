def render_title(composer, text, font_path, center_x, center_y, max_width, max_height, angle=45):
    """
    Fit the title within the given bounds and render it rotated at an angle centered on (center_x, center_y).
    """
    font = composer.find_fitting_font(
        text,
        font_path,
        max_width=max_width,
        max_height=max_height,
        angle=angle
    )
    composer.add_text(
        text,
        x=center_x,
        y=center_y,
        font=font,
        rotate=angle,
        anchor="mm"
    )

