#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 <input.html> [output.pdf]" >&2
  exit 1
fi

INPUT_HTML="$1"
if [ ! -f "$INPUT_HTML" ]; then
  echo "Error: HTML file not found: $INPUT_HTML" >&2
  exit 1
fi

ABS_HTML="$(cd "$(dirname "$INPUT_HTML")" && pwd)/$(basename "$INPUT_HTML")"
if [ "$#" -eq 2 ]; then
  OUTPUT_PDF="$2"
  mkdir -p "$(dirname "$OUTPUT_PDF")"
  ABS_PDF="$(cd "$(dirname "$OUTPUT_PDF")" && pwd)/$(basename "$OUTPUT_PDF")"
else
  ABS_PDF="${ABS_HTML%.*}.pdf"
fi

BROWSER=""
for candidate in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
  "$(command -v google-chrome 2>/dev/null || true)" \
  "$(command -v chromium 2>/dev/null || true)"; do
  if [ -n "$candidate" ] && [ -x "$candidate" ]; then
    BROWSER="$candidate"
    break
  fi
done

if [ -z "$BROWSER" ]; then
  echo "Error: No headless Chromium/Chrome/Edge browser found." >&2
  exit 1
fi

FILE_URL="$(python3 -c 'import pathlib, sys; print(pathlib.Path(sys.argv[1]).resolve().as_uri())' "$ABS_HTML")"

"$BROWSER" \
  --headless=new \
  --disable-gpu \
  --no-pdf-header-footer \
  --print-to-pdf="$ABS_PDF" \
  "$FILE_URL"

if [ ! -s "$ABS_PDF" ]; then
  echo "Error: Failed to generate PDF: $ABS_PDF" >&2
  exit 1
fi

echo "Exported PDF: $ABS_PDF"
