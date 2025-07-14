# 🛰️ Pollyvent API Guide

This document describes how to use the public API for generating flyers using Pollyvent.

---

## 📮 Endpoint

**URL:**  
`https://images.indiana50501.org/generate-flyer/`

**Method:**  
`POST`

**Content-Type:**  
`application/json`

---

## 📥 Request Parameters

**Required Fields:**

- `title` — *(string)* — Title of the event  
- `datetime` — *(ISO 8601 string)* — e.g. `"2025-07-14T18:00"`  
- `location` — *(string)* — Physical or virtual location  
- `url` — *(string)* — URL to encode into the QR code

**Optional Fields:**

- `gradient` — *(list of 2–3 values)* — E.g. `["#FFFFFF", "#2F80ED", "vertical"]`  
  Defaults to `["white", "blue", "vertical"]`
- `layout` — *(string)* — Name of a registered layout (e.g. `"diagonal"`, `"centered"`)  
  Defaults to `"diagonal"`

---

## 🧪 Example Request

Save this as `event.json`:

```json
{
  "title": "Community Safety Training",
  "datetime": "2025-07-14T18:00",
  "location": "Garfield Park, Indianapolis",
  "url": "https://example.com/event-signup",
  "gradient": ["#FFFFFF", "#2F80ED", "vertical"],
  "layout": "diagonal"
}
```

Send it with curl:

```bash
curl -X POST https://images.indiana50501.org/generate-flyer/ \
  -H "Content-Type: application/json" \
  -d @event.json
```

## 📤 Example Response

```json
{
  "status": "ok",
  "flyer_url": "https://images.indiana50501.org/media/flyers/824a801441a941d69d3db1d422064800.png"
}
```

Use the returned `flyer_url` to download or embed the image.

## 🔒 Notes
- Only POST requests are supported.
- This API is not currently rate-limited — be respectful.
- Layout names must match those registered in the backend layout registry.


Built with ❤️ for the polly-verse.

