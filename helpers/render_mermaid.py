#!/usr/bin/env python3
"""
Mermaid → PNG renderer using mermaid.ink API.
Pure Python stdlib — zero dependencies.

Usage:
  python helpers/render_mermaid.py <file.md> [--output-dir DIR]
"""

import argparse
import base64
import re
import sys
import urllib.request
from pathlib import Path
from typing import Optional


def render_mermaid_to_png(mermaid_code: str, output_path: Path) -> bool:
    """Render Mermaid code to PNG using mermaid.ink API.
    Uses raw base64 encode + User-Agent header (required by mermaid.ink).
    No dependencies needed. Returns True if PNG was saved successfully.
    """
    try:
        encoded = base64.urlsafe_b64encode(
            mermaid_code.encode('utf-8')
        ).decode('ascii')
        url = f'https://mermaid.ink/img/{encoded}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            output_path.write_bytes(resp.read())
        return output_path.exists() and output_path.stat().st_size > 100
    except Exception:
        return False


def extract_mermaid_blocks(md_path: Path) -> list:
    """Extract all Mermaid code blocks from a markdown file.
    Returns list of dicts with keys: index, code, name, start, end.
    """
    text = md_path.read_text(encoding='utf-8')
    blocks = []
    pattern = re.compile(r'```mermaid\s*\n(.*?)```', re.DOTALL)
    for i, m in enumerate(pattern.finditer(text)):
        code = m.group(1).strip()
        first_line = code.split('\n')[0].strip()
        if first_line.startswith('graph') or first_line.startswith('flowchart'):
            name = f'diagram_{i+1:02d}'
        elif first_line.startswith('journey'):
            name = f'journey_{i+1:02d}'
        elif first_line.startswith('sequenceDiagram'):
            name = f'sequence_{i+1:02d}'
        elif first_line.startswith('gantt'):
            name = f'gantt_{i+1:02d}'
        elif first_line.startswith('pie'):
            name = f'pie_{i+1:02d}'
        elif first_line.startswith('classDiagram'):
            name = f'class_{i+1:02d}'
        elif first_line.startswith('stateDiagram'):
            name = f'state_{i+1:02d}'
        elif first_line.startswith('erDiagram'):
            name = f'er_{i+1:02d}'
        else:
            name = f'mermaid_{i+1:02d}'
        blocks.append({
            'index': i,
            'code': code,
            'name': name,
            'start': m.start(),
            'end': m.end(),
        })
    return blocks


def render_all_mermaid_in_md(md_path: Path, output_dir: Optional[Path] = None) -> int:
    """Scan a .md file for Mermaid blocks, render each to PNG,
    and replace the code block with an image reference.
    Returns the number of blocks rendered.
    """
    out_dir = output_dir or md_path.parent
    text = md_path.read_text(encoding='utf-8')
    blocks = extract_mermaid_blocks(md_path)
    if not blocks:
        return 0

    rendered = 0
    # Process in reverse order to preserve positions
    for block in reversed(blocks):
        png_path = out_dir / f"{block['name']}.png"
        ok = render_mermaid_to_png(block['code'], png_path)
        if ok:
            caption = f"图{block['index']+1}"
            replacement = f'![{caption}]({png_path.name})'
            text = text[:block['start']] + replacement + text[block['end']:]
            rendered += 1
            print(f"  [MERMAID] {block['name']} → {png_path.name} ({png_path.stat().st_size:,} bytes)")
        else:
            print(f"  [MERMAID] {block['name']} → FAILED (network error?)")

    md_path.write_text(text, encoding='utf-8')
    return rendered


def main():
    parser = argparse.ArgumentParser(
        description='Render Mermaid code blocks in a markdown file to PNG images.')
    parser.add_argument('input', help='Markdown file to process')
    parser.add_argument('--output-dir', '-o', help='Output directory for PNG files (default: same as input)')
    args = parser.parse_args()

    md_path = Path(args.input).resolve()
    if not md_path.exists():
        print(f"Error: file not found: {md_path}")
        sys.exit(1)

    out_dir = Path(args.output_dir).resolve() if args.output_dir else None
    n = render_all_mermaid_in_md(md_path, out_dir)
    if n == 0:
        print("No Mermaid blocks found.")
    else:
        print(f"\nRendered {n} Mermaid diagram(s) to PNG.")
    sys.exit(0)


if __name__ == '__main__':
    main()