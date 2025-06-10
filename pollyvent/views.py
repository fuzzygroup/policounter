# pollyvent/views.py
import os
from django.http import HttpResponse
from pollyvent.yvent.generator import generate_flyer
from tempfile import NamedTemporaryFile
from django.conf import settings

BASE_DIR = settings.BASE_DIR

logo_path = os.path.join(BASE_DIR, "pollyvent", "yvent", "assets", "flierlogo.png")
font_path = os.path.join(BASE_DIR, "pollyvent", "yvent", "assets", "DejaVuSans.ttf")

def generate_flyer_view(request):
    title = request.GET.get("title")
    dt_str = request.GET.get("datetime")
    location = request.GET.get("location")

    if not all([title, dt_str, location]):
        return HttpResponse("Missing required parameters", status=400)

    # Use static asset paths
    logo_path = "assets/flierlogo.png"
    font_path = "assets/DejaVuSans.ttf"

    with NamedTemporaryFile(suffix=".png") as tmp:
        generate_flyer(
            title=title,
            dt_str=dt_str,
            location=location,
            qr_text="scan this",  # or also from GET param
            logo_path=logo_path,
            font_path=font_path,
            output_path=tmp.name
        )

        with open(tmp.name, "rb") as f:
            return HttpResponse(f.read(), content_type="image/png")
