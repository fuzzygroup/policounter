# 🎨 Pollyvent

> Print the message. Spread the word. From raw data to designed impact.

**Pollyvent** is the image generation engine of the polly-verse. It creates event flyers with high visual impact using structured data and composable design logic.

Originally built to serve activist and protest communities, Pollyvent transforms event metadata into eye-catching images, complete with titles, logos, dates, locations, and scannable QR codes.

---

## ✅ Features

- Gradient backgrounds and transparent overlays
- Dynamically scaled, wrapped, and rotated text
- Logo support with smart placement and scaling
- QR code embedding with customizable size and location
- Modular layout system for flexible flyer design
- CLI and API usage supported

## 🧱 Layout System
Pollyvent’s layout system separates **design intent** from **drawing logic**. Layouts define where elements go, how they relate, and what styles or behaviors they follow. This makes flyer design modular, reusable, and easy to extend.

### 📂 Layouts Directory Structure
```bash
pollyvent/
└── yvent/
  └── layouts/
    ├── base.py # Base Layout class
    ├── diagonal.py # A sample layout implementation
    ├── centered.py # Another layout option
    └── blocks/ # Reusable design components
      ├── title_block.py
      ├── info_block.py
      ├── qr_block.py
      └── logo_block.py
```

### 🔧 Composable Blocks

Each layout is built from **blocks**, which encapsulate drawing logic for specific components:
- `title_block`: Rotated, centered, or wrapped text headers
- `info_block`: Dates, times, and locations stacked or aligned
- `qr_block`: Scannable QR codes with layout-aware padding
- `logo_block`: Overlaying organizational or event branding

Each block is responsible for rendering its portion of the image to the shared `ImageComposer` instance.

---

## ✨ Example Usage

### Programming interface

``` bash
from pollyvent.yvent.layouts.diagonal import DiagonalLayout
from pollyvent.yvent.generator import ImageComposer

layout = DiagonalLayout()
composer = ImageComposer(gradient=("white", "blue"))
layout.render(composer, event_data)
composer.save_to("flyer.png")
```
 
### API Endpoint: Generate Flyer via GET Request

## API Endpoint: Generate Flyer via GET Request

You can generate a flyer remotely by sending a GET request to the flyer generation endpoint.

**Endpoint:**  
`https://images.indiana50501.org/generate-flyer/`

**Required query parameters:**

- `title`: Title of the event (URL-encoded)
- `datetime`: ISO8601 format datetime (e.g. `2025-07-14T18:00`)
- `location`: Location string (URL-encoded)
- `url`: URL to be encoded as a QR code (URL-encoded)

***Example request***

```
https://images.indiana50501.org/generate-flyer/?title=Community+Safety+Training&datetime=2025-07-14T18%3A00&location=Garfield+Park%2C+Indianapolis&url=https%3A%2F%2Fexample.com%2Fevent-signup
```


***Example JSON response:***
```json
{
  "status": "ok",
  "flyer_url": "https://images.indiana50501.org/media/flyers/824a801441a941d69d3db1d422064800.png"
}
``` 
You can use the `flyer_url` to download or embed the generated flyer image.

### CLI Usage
Coming soon: A CLI interface to generate flyers from event JSON or YAML data.

## 📎 Related Files

- [yvent/generator.py](./yvent/generator.py): Contains legacy procedural flyer creation logic
- [yvent/base.py](./yvent/base.py): Core image composition functions (ImageComposer)
- [yvent/cli.py](./yvent/cli.py): (In development) CLI entrypoint for batch flyer creation
- [yvent/tests/](./yvent/tests/): Unit tests for layout rendering and output validation

## 📐 Goals
- Separate flyer design from drawing
- Enable reusable layouts and theme variants
- Support testable, scriptable, and automated generation
- Allow easy integration into web apps, bots, or command-line tools

## 🖼️ Example Outputs
(Add screenshots or thumbnails of generated flyers here to inspire confidence and show diversity of layouts.)

> Flyers are ephemeral, but the design system behind them doesn’t have to be.
