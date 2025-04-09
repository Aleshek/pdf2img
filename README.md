# pdf2img

A tool to capture PDF pages as images by taking screenshots, especially useful for PDFs with DRM protection.

## Overview

This utility helps extract visual content from protected PDFs by:
1. Opening the PDF with the system's default viewer
2. Taking screenshots of each page
3. Saving the screenshots as images
4. Optionally detecting the end of the document automatically

This approach bypasses DRM/security measures since it uses the visual rendering of the PDF rather than trying to access the encrypted content directly.

## Installation

### Requirements
- Python 3.6 or higher
- A PDF viewer installed on your system

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/pdf2img.git
   cd pdf2img
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
# Automatically capture all pages in a PDF (detects end of document)
python pdf2img.py path/to/your/protected.pdf --auto-capture --output-dir "output_images"

# Capture a specific number of pages
python pdf2img.py path/to/your/protected.pdf --screenshot 10 --output-dir "output_images"
```

### Advanced Options

```bash
python pdf2img.py path/to/your/protected.pdf --auto-capture \
  --output-dir "output_images" \
  --delay 1.5 \
  --similarity 0.92 \
  --similar-pages 2 \
  --startup-delay 8 \
  --no-close
```

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `pdf_path` | Path to the PDF file to process (required) |
| `--output-dir` | Directory to save images (default: "pdf_images") |
| `--screenshot N` | Take N screenshots, manually changing pages |
| `--auto-capture` | Automatically capture PDF pages with end detection |
| `--max-pages` | Maximum pages to capture in auto mode (default: 500) |
| `--delay` | Delay between screenshots in seconds (default: 2.0) |
| `--similarity` | Similarity threshold for auto-detection (0-1) (default: 0.95) |
| `--similar-pages` | Number of similar pages to confirm end of document (default: 2) |
| `--startup-delay` | Delay in seconds to wait for PDF to open (default: 5) |
| `--no-close` | Don't close the PDF viewer when done |

## How It Works

1. **PDF Opening**: The script opens the PDF using your system's default PDF viewer
2. **Window Management**: Attempts to focus the window and maximize the view
3. **Screenshot Capture**: Takes screenshots of each page
4. **Page Navigation**: Either:
   - Waits for you to manually navigate pages (`--screenshot` option)
   - Automatically presses spacebar to advance pages (`--auto-capture` option)
5. **End Detection**: When using auto-capture, detects the end of the document by comparing consecutive pages for similarity
6. **PDF Closing**: Closes the PDF viewer when done (unless `--no-close` is specified)

## Notes

- The script requires the PDF to be visible on screen during capture
- Quality of captured images depends on your screen resolution and PDF viewer settings
- For best results, ensure the PDF takes up as much screen space as possible
- When using automatic page turning, make sure the PDF viewer responds to the spacebar to turn pages

## License

[MIT License](LICENSE)
