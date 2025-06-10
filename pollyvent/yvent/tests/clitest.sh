#!/bin/bash

# Directory setup (optional but helpful)
mkdir -p output

# 1. Rally – Environment
python -m yvent \
  --title "We Have Only this Planet; The Environment Matters" \
  --datetime 2025-07-27T12:00 \
  --location "State House" \
  --qr-text "https://example.com/events/environment-rally" \
  --logo-path "assets/flierlogo.png" \
  --font-path "assets/DejaVuSans.ttf" \
  --output-path "output/test_environment.png"

# 2. Protest – Dads for Democracy
python -m yvent \
  --title "Dads for Democracy Rally" \
  --datetime 2025-06-15T16:00 \
  --location "Noblesville Court House" \
  --qr-text "https://example.com/events/dads-for-democracy" \
  --logo-path "assets/flierlogo.png" \
  --font-path "assets/DejaVuSans.ttf" \
  --output-path "output/test_dads.png"

# 3. Protest – No King Day
python -m yvent \
  --title "No King Day National Day of Mobilization" \
  --datetime 2025-06-14T12:00 \
  --location "Indiana State House" \
  --qr-text "https://example.com/events/no-king-day" \
  --logo-path "assets/flierlogo.png" \
  --font-path "assets/DejaVuSans.ttf" \
  --output-path "output/test_noking.png"

# 4. Tabling – Greenwood Pride
python -m yvent \
  --title "6/7 - Greenwood Pride Indiana 50501 Table" \
  --datetime 2025-06-07T12:00 \
  --location "Woodmen Park (near the Greenwood High School)" \
  --qr-text "https://example.com/events/greenwood-pride" \
  --logo-path "assets/flierlogo.png" \
  --font-path "assets/DejaVuSans.ttf" \
  --output-path "output/test_pride.png"

# 5. Protest – D-Day Protest
python -m yvent \
  --title "6/6 Protest - D Day" \
  --datetime 2025-06-06T12:00 \
  --location "Indianapolis State House" \
  --qr-text "https://example.com/events/d-day-protest" \
  --logo-path "assets/flierlogo.png" \
  --font-path "assets/DejaVuSans.ttf" \
  --output-path "output/test_dday.png"

echo "All test posters generated."
