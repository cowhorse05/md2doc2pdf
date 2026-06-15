# md2docx-pdf

> Cross-platform CLI tool: Markdown → DOCX + PDF, with full CJK support.
> Auto-detects platform, checks dependencies, gives clear install instructions.

[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](#)
[![Python](https://img.shields.io/badge/python-3.7+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## Quick Start

```bash
# Download
git clone https://github.com/cowhorse05/md2doc2pdf.git
cd md2doc2pdf

# Install dependencies (auto-detected on first run with install hints)
#   - pandoc (required): https://pandoc.org/installing.html
#   - Chrome/Edge (optional, for PDF only)

# Convert a Markdown file
python md2docx_pdf.py report.md

# Convert to PDF
python md2docx_pdf.py report.md -f pdf

# Convert to both DOCX + PDF
python md2docx_pdf.py report.md -f both

# Batch convert all .md files
python md2docx_pdf.py *.md -f both

# Custom output directory
python md2docx_pdf.py report.md -f both -o ./output
```

---

## Features

- **DOCX output** — clean `.docx` via pandoc, preserving headings, tables, code blocks
- **PDF output** — professional `.pdf` via headless Chrome/Edge, with injected CJK CSS
- **Auto-detection** — finds Chrome/Edge/Chromium across Windows, macOS, Linux
- **Dependency check** — on first run, detects missing tools and prints platform-specific install commands
- **Batch mode** — `*.md` glob patterns, multiple files at once
- **CJK fonts** — auto-injects `Microsoft YaHei`, `SimSun`, `PingFang SC`, `Noto Sans SC`
- **Clean output** — tables with alternating rows, styled code blocks, bordered blockquotes

---

## Installing Dependencies

### Step 1: Install Python 3.7+

Already installed? Check: `python --version`

| Platform | Install |
|----------|---------|
| **Windows** | `winget install python` or https://www.python.org/downloads/ |
| **macOS** | `brew install python` |
| **Linux** | `sudo apt install python3` |

### Step 2: Install pandoc (required)

| Platform | Command |
|----------|---------|
| **Windows** | `winget install pandoc` |
| **macOS** | `brew install pandoc` |
| **Linux (Debian/Ubuntu)** | `sudo apt install pandoc` |
| **Linux (Fedora)** | `sudo dnf install pandoc` |
| **Linux (Arch)** | `sudo pacman -S pandoc` |

Or download from: https://pandoc.org/installing.html

### Step 3: Install a browser (for PDF only)

Skip this if you only need DOCX output.

| Platform | Option |
|----------|--------|
| **Windows** | Google Chrome or Microsoft Edge (usually pre-installed) |
| **macOS** | `brew install --cask google-chrome` |
| **Linux** | `sudo apt install chromium-browser` |

The tool will auto-detect your browser from common install paths.

---

## Usage

```
usage: md2docx_pdf.py [-h] [-f {docx,pdf,both}] [-o DIR] [--version]
                      inputs [inputs ...]

positional arguments:
  inputs                Markdown file(s) or glob patterns (e.g. "*.md")

options:
  -h, --help            show this help message and exit
  -f, --format {docx,pdf,both}
                        Output format (default: docx)
  -o, --output DIR      Output directory (default: same as input file)
  --version             show version number and exit
```

---

## Examples

```bash
# Basic: single file to DOCX
python md2docx_pdf.py report.md

# Single file to PDF
python md2docx_pdf.py report.md -f pdf

# Single file to both formats
python md2docx_pdf.py report.md -f both

# Batch: all .md files to both formats
python md2docx_pdf.py *.md -f both

# With custom output directory
python md2docx_pdf.py report.md -f both -o ./output

# Multiple specific files
python md2docx_pdf.py report1.md report2.md report3.md -f both
```

### Sample Output

```
==================================================
  md2docx_pdf v1.0.0   https://github.com/cowhorse05/md2doc2pdf
  Markdown -> DOCX / PDF Converter
==================================================

[CHECK] Verifying dependencies...
  Platform detected: Windows
  pandoc: pandoc 3.9.0.2
  browser: chrome.exe
[OK] All dependencies satisfied

  Files to convert: 2
  Format: both
  Output: (same as input)

[FILE] report1.md (18,139 bytes)
  -> DOCX: report1.docx ... [OK] (23,000 bytes)
  -> PDF:  report1.pdf ... [OK] (652,383 bytes)

[FILE] report2.md (19,188 bytes)
  -> DOCX: report2.docx ... [OK] (23,568 bytes)
  -> PDF:  report2.pdf ... [OK] (836,750 bytes)

==================================================
  [OK] 4 succeeded   [FAIL] 0 failed   [TOTAL] 2 file(s)
==================================================
```

---

## PDF Output Styling

The tool injects a clean, print-optimized CSS stylesheet into every PDF:

| Element | Style |
|---------|-------|
| **Headings** | h1 blue bottom-border, h2 gray bottom-border |
| **Tables** | Bordered cells, bold headers, alternating row colors |
| **Code** | Light gray background, monospace (Consolas/Courier New) |
| **Blockquotes** | Blue left border, light blue background |
| **Fonts** | Microsoft YaHei → SimSun → PingFang SC → Noto Sans SC |

If your system lacks Chinese fonts, install them:

| Platform | Command |
|----------|---------|
| **Windows** | Already included (Microsoft YaHei, SimSun) |
| **macOS** | Already included (PingFang SC) |
| **Linux** | `sudo apt install fonts-noto-cjk` |

---

## How It Works

```
Markdown (.md)
    │
    ├──> pandoc ──> DOCX (.docx)     [direct conversion]
    │
    └──> pandoc ──> HTML ──> Chrome/Edge headless ──> PDF (.pdf)
                        │
                        └── CSS injected for CJK + tables + code
```

- **DOCX**: pandoc converts Markdown directly to Word format
- **PDF**: pandoc first converts to HTML5, then the tool injects custom CSS, then a headless browser renders it to PDF

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `pandoc not found` | Install pandoc (see [Installing Dependencies](#installing-dependencies)) |
| `No browser found` for PDF | Install Chrome/Edge, or set `BROWSER_PATH` env variable |
| Chinese characters garbled in PDF | Install CJK fonts: `sudo apt install fonts-noto-cjk` (Linux) |
| `Permission denied` | Check file permissions or close the .docx if opened in Word |
| `File not found` for glob patterns | Use quotes: `python md2docx_pdf.py "*.md" -f both` |

---

## Contributing

Issues and pull requests welcome at: https://github.com/cowhorse05/md2doc2pdf

---

## License

MIT — Li Yufeng, 2026
