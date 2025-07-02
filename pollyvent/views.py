# pollyvent/views.py
import os
import uuid
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from pollyvent.yvent.generator import generate_flyer

def generate_flyer_view(request):
    title = request.GET.get("title")
    dt_str = request.GET.get("datetime")
    location = request.GET.get("location")
    url = request.GET.get("url")

    if not all([title, dt_str, location, url]):
        return HttpResponse("Missing required parameters", status=400)

    # Create output directory inside MEDIA_ROOT
    output_dir = os.path.join(settings.MEDIA_ROOT, "flyers")
    os.makedirs(output_dir, exist_ok=True)

    # Generate unique filename
    filename = f"{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_dir, filename)

    # Static asset paths (absolute)
    logo_path = os.path.join(settings.BASE_DIR, "pollyvent", "yvent", "assets", "flierlogo.png")
    font_path = os.path.join(settings.BASE_DIR, "pollyvent", "yvent", "assets", "DejaVuSans.ttf")

    # Generate the flyer image
    generate_flyer(
        title=title,
        dt_str=dt_str,
        location=location,
        qr_text=url,  # Could be dynamic if needed
        logo_path=logo_path,
        font_path=font_path,
        output_path=output_path,
    )

    # Build absolute URL to saved image
    relative_url = f"/media/flyers/{filename}"
    full_url = request.build_absolute_uri(relative_url)

    return JsonResponse({
        "status": "ok",
        "flyer_url": full_url
    })

