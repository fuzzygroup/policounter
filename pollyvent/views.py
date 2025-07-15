# pollyvent/views.py

import uuid
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
import json

@csrf_exempt
def generate_flyer_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST supported")

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    required = ["title", "datetime", "location", "url"]
    missing = [key for key in required if key not in body]
    if missing:
        honeybadger.notify(
            f"Flyer generation failed: missing required fields",
            context={
                "missing": missing,
                "body": body,
                "remote_ip": request.META.get("REMOTE_ADDR"),
                "user_agent": request.META.get("HTTP_USER_AGENT"),
                "path": request.path
            }
        )
        return HttpResponseBadRequest(f"Missing one of: {', '.join(required)}")


    # Optional params
    gradient = body.get("gradient")  # optional tuple like ["white", "blue", "vertical"]
    layout_name = body.get("layout", "diagonal")

    logo_path = os.path.join(settings.BASE_DIR, "pollyvent", "yvent", "assets", "flierlogo.png")
    font_path = os.path.join(settings.BASE_DIR, "pollyvent", "yvent", "assets", "Ultra-Regular.ttf")

    from pollyvent.yvent.generator import generate_flyer

    filename = f"{uuid.uuid4().hex}.png"
    output_path = os.path.join(settings.MEDIA_ROOT, "flyers", filename)

    generate_flyer(
        title=body["title"],
        dt_str=body["datetime"],
        location=body["location"],
        qr_text=body["url"],
        logo_path=logo_path,
        font_path=font_path,
        output_path=output_path,
        gradient=tuple(gradient) if gradient else None,
        layout_name=layout_name
        )


    relative_url = f"/media/flyers/{filename}"
    full_url = request.build_absolute_uri(relative_url)

    return JsonResponse({
        "status": "ok",
        "flyer_url": full_url
    })

