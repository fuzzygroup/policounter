
# pollyvent/yvent/layouts/minimal.py

from .base import Layout
from .blocks.title_block import render_title
from .blocks.qr_block import render_qr_code
from .blocks.info_block import render_info_block
from .blocks.logo_block import render_logo


class MinimalLayout(Layout):
    """
    Recreates the original generate_flyer layout:
    - Diagonal rotated title
    - Logo in top left
    - QR code in bottom right
    - Date/time/location stacked above the QR
    """

    def render_frame(self, composer):
        margin = composer.margin
        bounds = [margin, margin, composer.width - margin, composer.height - margin]

        composer.draw.rounded_rectangle(
            bounds,
            radius=40,
            outline="black",
            width=10
        )

    def render(self, composer, data):
        self.validate_data(data)
        self.render_frame(composer)

        margin = composer.margin
        width = composer.width
        height = composer.height

        # 1. Logo centered top
        render_logo(
            composer,
            data["logo_path"],
            x=width // 2 - 750 // 2 + margin,
            y=margin,
            max_width=750
        )

        # 2. Title in center
        render_title(
            composer,
            text=data["title"],
            font_path=str(data["font_path"]),
            center_x=width // 2,
            center_y=height // 2,
            max_width=width - 2 * margin,
            max_height=height - 2 * margin,
            angle=0
        )

        # 3. Info block (bottom left)
        info_x = margin * 2
        info_y = height - height // 6

        info_x, info_y, info_w, info_h = render_info_block(
            composer,
            data,
            x=info_x,
            y=info_y,
            spacing=20,
            info_font_sz=60,
            loc_font_sz=62
        )

        # 4. QR code aligned to right of info block
        qr_box_size = info_h + info_h //4
        qr_padding = 20

        if data.get("qr_text"):
            qr_x = width - composer.margin - qr_box_size - qr_padding
            qr_y = int((info_y + (info_h // 2) - (qr_box_size // 2)) * .98)


            render_qr_code(
                composer,
                data["qr_text"],
                x=qr_x,
                y=qr_y,
                max_size=qr_box_size
            )

