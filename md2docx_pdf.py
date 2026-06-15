#!/usr/bin/env python3
"""
md2docx_pdf.py --- Markdown to DOCX & PDF Converter
====================================================
Cross-platform CLI tool for converting Markdown files to
professional DOCX (Word) and PDF documents with full CJK support.

GitHub: https://github.com/cowhorse05/md2doc2pdf
Author: Li Yufeng
Version: 1.0.0
License: MIT
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import glob
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple


# ── Config ────────────────────────────────────────────────────

VERSION = "1.0.0"
REPO_URL = "https://github.com/cowhorse05/md2doc2pdf"

CHINESE_CSS = """<style>
  body{font-family:"Microsoft YaHei","SimSun","PingFang SC","Noto Sans SC",sans-serif;font-size:14px;line-height:1.8;margin:40px auto;max-width:800px;color:#333}
  h1{font-size:22px;font-weight:bold;border-bottom:2px solid #3b82f6;padding-bottom:8px;margin-top:24px}
  h2{font-size:18px;color:#1f2937;border-bottom:1px solid #e5e7eb;padding-bottom:5px;margin-top:20px}
  h3{font-size:15px;color:#374151;margin-top:16px}
  h4{font-size:14px;color:#4b5563}
  table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}
  th,td{border:1px solid #ddd;padding:6px 10px;text-align:left}
  th{background:#f5f5f5;font-weight:700}
  tr:nth-child(even){background:#fafafa}
  code{background:#f4f4f4;padding:1px 5px;border-radius:3px;font-size:13px;font-family:"Consolas","Courier New",monospace}
  pre{background:#f8f8f8;border:1px solid #e5e7eb;border-radius:6px;padding:12px 16px;overflow-x:auto;font-size:13px}
  pre code{background:none;padding:0}
  blockquote{border-left:4px solid #3b82f6;margin:12px 0;padding:6px 16px;background:#eff6ff}
  hr{border:none;border-top:1px solid #ddd;margin:20px 0}
  img{max-width:100%}a{color:#3b82f6}strong{color:#1f2937}
  @media print{body{margin:0}@page{margin:2cm}}
</style>"""

# Browser search paths by platform
BROWSER_SEARCH = {
    'Windows': [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    ],
    'Darwin': [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    ],
    'Linux': [
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
        '/snap/bin/chromium',
    ],
}

BROWSER_CMD_NAMES = [
    'google-chrome', 'chrome', 'chromium', 'chromium-browser',
    'msedge', 'microsoft-edge',
]


# ── Platform Utilities ────────────────────────────────────────

def get_platform_name() -> str:
    """Return human-readable platform name."""
    return platform.system()  # 'Windows', 'Darwin', 'Linux'


def get_install_instructions(tool: str) -> str:
    """Return platform-specific install instructions for a tool."""
    plat = get_platform_name()
    instructions = {
        'pandoc': {
            'Windows': [
                '  winget install pandoc',
                '  # or download from: https://pandoc.org/installing.html',
            ],
            'Darwin': [
                '  brew install pandoc',
            ],
            'Linux': [
                '  sudo apt install pandoc        # Debian/Ubuntu',
                '  sudo dnf install pandoc        # Fedora',
                '  sudo pacman -S pandoc          # Arch',
            ],
        },
        'browser': {
            'Windows': [
                '  # Install Google Chrome: https://www.google.com/chrome/',
                '  # Or Microsoft Edge (already installed on Windows 10+)',
            ],
            'Darwin': [
                '  brew install --cask google-chrome',
                '  # Or: brew install --cask microsoft-edge',
            ],
            'Linux': [
                '  sudo apt install chromium-browser   # Debian/Ubuntu',
                '  sudo dnf install chromium           # Fedora',
                '  # Or install google-chrome from https://www.google.com/chrome/',
            ],
        },
    }
    return '\n'.join(instructions.get(tool, {}).get(plat, ['  Please install manually']))


# ── Dependency Detection ──────────────────────────────────────

def find_browser() -> Optional[str]:
    """Auto-detect an available Chromium-based browser."""
    plat = get_platform_name()
    candidates = list(BROWSER_SEARCH.get(plat, []))

    # Also check PATH
    for name in BROWSER_CMD_NAMES:
        found = shutil.which(name)
        if found and found not in candidates:
            candidates.append(found)

    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def check_pandoc() -> bool:
    """Check if pandoc is installed and accessible."""
    return shutil.which('pandoc') is not None


def check_dependencies(fmt: str) -> Tuple[bool, List[str]]:
    """Check all required dependencies.
    Returns (all_ok, error_messages).
    """
    errors = []
    plat = get_platform_name()

    print(f"  Platform detected: {plat}")

    # Check pandoc
    if check_pandoc():
        pandoc_ver = subprocess.run(
            ['pandoc', '--version'], capture_output=True, timeout=5
        ).stdout.decode('utf-8', errors='replace').split('\n')[0]
        print(f"  pandoc: {pandoc_ver}")
    else:
        errors.append(
            "[MISSING] pandoc -- required for all conversions\n"
            f"{get_install_instructions('pandoc')}"
        )
        print("  pandoc: NOT FOUND")

    # Check browser (only needed for PDF)
    if fmt in ('pdf', 'both'):
        browser = find_browser()
        if browser:
            print(f"  browser: {Path(browser).name}")
        else:
            errors.append(
                "[MISSING] Chromium browser (Chrome/Edge) -- required for PDF\n"
                f"{get_install_instructions('browser')}\n"
                "  Or set BROWSER_PATH env variable to your browser executable."
            )
            print("  browser: NOT FOUND")

    return len(errors) == 0, errors


# ── Converters ────────────────────────────────────────────────

def md_to_docx(input_path: Path, output_path: Path) -> bool:
    """Convert Markdown to DOCX using pandoc."""
    cmd = [
        'pandoc',
        str(input_path),
        '-o', str(output_path),
        '--from', 'markdown+smart',
        '--to', 'docx',
        '--standalone',
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        if output_path.exists() and output_path.stat().st_size > 100:
            return True
        return False
    except Exception as e:
        print(f"  Exception: {e}")
        return False


def md_to_pdf(input_path: Path, output_path: Path,
              browser_path: str) -> bool:
    """Convert Markdown to PDF via HTML + headless browser."""
    fd, html_path = tempfile.mkstemp(suffix='.html', prefix='md2pdf_')
    os.close(fd)

    # Step 1: MD -> HTML
    cmd_html = [
        'pandoc',
        str(input_path),
        '-o', html_path,
        '--from', 'markdown+smart',
        '--to', 'html5',
        '--standalone',
        '--metadata', 'title=',
    ]
    try:
        result = subprocess.run(cmd_html, capture_output=True, timeout=30)
        if result.returncode != 0:
            print(f"  HTML conversion failed")
            try:
                os.unlink(html_path)
            except OSError:
                pass
            return False
    except Exception as e:
        print(f"  HTML conversion exception: {e}")
        try:
            os.unlink(html_path)
        except OSError:
            pass
        return False

    # Step 2: Inject CSS
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace(
            '<head>', f'<head><meta charset="UTF-8">{CHINESE_CSS}')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"  CSS injection failed: {e}")
        try:
            os.unlink(html_path)
        except OSError:
            pass
        return False

    # Step 3: HTML -> PDF
    html_url = 'file:///' + html_path.replace('\\', '/')
    cmd_pdf = [
        browser_path,
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        f'--print-to-pdf={output_path}',
        '--no-pdf-header-footer',
        '--no-margins',
        '--virtual-time-budget=15000',
        html_url,
    ]
    try:
        subprocess.run(cmd_pdf, capture_output=True, timeout=45)
    except subprocess.TimeoutExpired:
        print(f"  Browser timed out after 45s")
    except Exception as e:
        print(f"  Browser exception: {e}")
    finally:
        try:
            os.unlink(html_path)
        except OSError:
            pass

    return output_path.exists() and output_path.stat().st_size > 500


# ── Conversion Engine ─────────────────────────────────────────

def convert_file(input_path: Path, fmt: str, output_dir: Optional[Path],
                 browser_path: Optional[str]) -> Tuple[int, int]:
    """Convert one file. Returns (ok, fail) counts."""
    if output_dir is None:
        output_dir = input_path.parent

    base_name = input_path.stem
    ok, fail = 0, 0
    size = input_path.stat().st_size

    print(f"\n[FILE] {input_path.name} ({size:,} bytes)")

    if fmt in ('docx', 'both'):
        docx_path = output_dir / f'{base_name}.docx'
        print(f"  -> DOCX: {docx_path.name} ... ", end='', flush=True)
        if md_to_docx(input_path, docx_path):
            out_size = docx_path.stat().st_size
            print(f"[OK] ({out_size:,} bytes)")
            ok += 1
        else:
            print("[FAIL]")
            fail += 1

    if fmt in ('pdf', 'both'):
        pdf_path = output_dir / f'{base_name}.pdf'
        print(f"  -> PDF:  {pdf_path.name} ... ", end='', flush=True)
        if browser_path is None:
            print("[SKIP] (no browser)")
        elif md_to_pdf(input_path, pdf_path, browser_path):
            out_size = pdf_path.stat().st_size
            print(f"[OK] ({out_size:,} bytes)")
            ok += 1
        else:
            print("[FAIL]")
            fail += 1

    return ok, fail


# ── Main ──────────────────────────────────────────────────────

def main():
    # Fix encoding on Windows
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description='Convert Markdown to professional DOCX/PDF with CJK support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s report.md                  # DOCX only (default)
  %(prog)s report.md -f both          # DOCX + PDF
  %(prog)s *.md -f pdf                # Batch convert to PDF
  %(prog)s report.md -f both -o ./out # Custom output directory

GitHub: {REPO_URL}
        """
    )
    parser.add_argument('inputs', nargs='+',
                        help='Markdown file(s) or glob patterns')
    parser.add_argument('-f', '--format', default='docx',
                        choices=['docx', 'pdf', 'both'],
                        help='Output format (default: docx)')
    parser.add_argument('-o', '--output', metavar='DIR',
                        help='Output directory')
    parser.add_argument('--version', action='version',
                        version=f'md2docx_pdf v{VERSION}')

    args = parser.parse_args()

    # ── Header ────────────────────────────────────────────
    print(f"""\n{'='*50}
  md2docx_pdf v{VERSION}   {REPO_URL}
  Markdown -> DOCX / PDF Converter
{'='*50}\n""")

    # ── Dependency check ──────────────────────────────────
    print("[CHECK] Verifying dependencies...")
    all_ok, errors = check_dependencies(args.format)

    if errors:
        print(f"\n{'='*50}")
        print("  DEPENDENCY ISSUES DETECTED")
        print(f"{'='*50}")
        for e in errors:
            print(f"\n{e}")
        print(f"\n{'='*50}")
        print(f"  GitHub: {REPO_URL}")
        print(f"{'='*50}")
        sys.exit(1)

    print("[OK] All dependencies satisfied\n")

    # ── Resolve input files ───────────────────────────────
    input_files: List[Path] = []
    for pattern in args.inputs:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            for m in matches:
                p = Path(m).resolve()
                if p.suffix.lower() in ('.md', '.markdown', '.txt'):
                    input_files.append(p)
        else:
            p = Path(pattern).resolve()
            if p.exists():
                input_files.append(p)
            else:
                print(f"[WARN] Not found: {pattern}")

    if not input_files:
        print("\n[ERROR] No .md files found!")
        sys.exit(1)

    # De-duplicate
    seen = set()
    unique = []
    for f in input_files:
        if f not in seen:
            seen.add(f)
            unique.append(f)

    print(f"  Files to convert: {len(unique)}")
    print(f"  Format: {args.format}")
    print(f"  Output: {args.output or '(same as input)'}")

    # ── Convert ───────────────────────────────────────────
    output_dir = Path(args.output).resolve() if args.output else None
    browser = find_browser()
    total_ok, total_fail = 0, 0

    for f in unique:
        ok, fail = convert_file(f, args.format, output_dir, browser)
        total_ok += ok
        total_fail += fail

    # ── Summary ───────────────────────────────────────────
    print(f"""\n{'='*50}
  [OK] {total_ok} succeeded   [FAIL] {total_fail} failed   [TOTAL] {len(unique)} file(s)
{'='*50}""")
    if output_dir:
        print(f"  Output: {output_dir}")

    sys.exit(0 if total_fail == 0 else 1)


if __name__ == '__main__':
    main()
