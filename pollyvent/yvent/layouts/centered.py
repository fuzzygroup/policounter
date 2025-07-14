
# pollyvent/yvent/layouts/cneter.py

from .base import Layout
from .blocks.title_block import render_title
from .blocks.qr_block import render_qr_code
from .blocks.info_block import render_info_block
from .blocks.logo_block import render_logo


class CenteredLayout(Layout):
    """
    Recreates the original generate_flyer layout:
    - Diagonal rotated title
    - Logo in top left
    - QR code in bottom right
    - Date/time/location stacked above the QR
    """

    def render(self, composer, data):
        self.validate_data(data)

        margin = composer.margin
        width = composer.width
        height = composer.height

        # 1. Logo in top-left
        render_logo(composer, data["logo_path"], x=margin, y=margin, max_width=750)

        # 2. title, centered
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

        # 3. QR Code in bottom right
        qr_padding = 60
        qr_margin = margin + qr_padding
        qr_box_size = 400
        qr_x = width - qr_box_size - qr_margin
        qr_y = height - qr_box_size - qr_margin

        qr_img_width = 0
        if data.get("qr_text"):
            qr_img_width = render_qr_code(
                composer,
                data["qr_text"],
                x=qr_x,
                y=qr_y,
                max_size=qr_box_size
            )

        # 4. Info block (date, time, location) above QR
        render_info_block(
            composer,
            data,
            qr_x=qr_x,
            qr_y=qr_y,
            qr_width=qr_img_width,
            spacing=10
        )
