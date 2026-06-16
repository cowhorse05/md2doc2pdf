#!/usr/bin/env python3
"""
DOCX black-text post-processor.
Patches ALL XML files inside a DOCX (ZIP) to force text color to pure black (#000000).
Pure Python stdlib — zero dependencies.

Usage:
  python helpers/black_text.py <file.docx> [file2.docx ...]
"""

import argparse
import io
import re
import sys
import zipfile
from pathlib import Path


def force_black_text_in_docx(docx_path: Path) -> bool:
    """Post-process a docx file to force ALL text to black.
    Patches ALL XML files in the ZIP, plus the theme to neutralize colors.
    Aggressive mode: replaces any 6-char hex color with 000000.
    Returns True on success.
    """
    try:
        # Read original zip into memory
        with zipfile.ZipFile(docx_path, 'r') as zin:
            files = {name: zin.read(name) for name in zin.namelist()}

        patched = 0

        # Patch ALL XML files for color attributes
        for name in list(files.keys()):
            if not name.endswith('.xml'):
                continue
            try:
                xml = files[name].decode('utf-8')
            except UnicodeDecodeError:
                continue

            original = xml

            # 1. Replace all w:color values with 000000
            xml = re.sub(
                r'(<w:color\b[^>]*?)w:val="[^"]*"',
                r'\1w:val="000000"',
                xml
            )

            # 2. Kill all themeColor/themeShade/themeTint — they override w:val
            xml = re.sub(r'\s*w:themeColor="[^"]*"', '', xml)
            xml = re.sub(r'\s*w:themeShade="[^"]*"', '', xml)
            xml = re.sub(r'\s*w:themeTint="[^"]*"', '', xml)

            # 3. Aggressive: any standalone w:val="XXXXXX" (6-char hex) → 000000
            xml = re.sub(
                r'(w:val=")([0-9A-Fa-f]{6})(")',
                r'\g<1>000000\3',
                xml
            )

            if xml != original:
                files[name] = xml.encode('utf-8')
                patched += 1

        # Also patch theme XML to neutralize theme colors
        theme_paths = [
            'word/theme/theme1.xml',
            'word/theme/theme.xml',
            'word/theme/theme2.xml',
        ]
        for tp in theme_paths:
            if tp in files:
                xml = files[tp].decode('utf-8')
                original = xml
                # Replace all theme color values with black
                xml = re.sub(
                    r'(<a:dk1>|<a:lt1>|<a:dk2>|<a:lt2>|<a:accent\d>|<a:hlink>|<a:folHlink>).*?</\1>',
                    r'\g<1><a:srgbClr val="000000"/></\1>',
                    xml
                )
                # Nuke all srgbClr values in theme
                xml = re.sub(
                    r'<a:srgbClr val="[^"]*"',
                    '<a:srgbClr val="000000"',
                    xml
                )
                # Kill systemClr references
                xml = re.sub(
                    r'<a:sysClr val="[^"]*"[^>]*>',
                    '<a:srgbClr val="000000">',
                    xml
                )
                if xml != original:
                    files[tp] = xml.encode('utf-8')
                    patched += 1

        if patched == 0:
            return True  # Nothing changed, already clean

        # Build new zip in memory
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zout:
            for name, data in files.items():
                zout.writestr(name, data)
        new_bytes = buf.getvalue()

        # Write back
        try:
            docx_path.write_bytes(new_bytes)
        except PermissionError:
            alt = docx_path.parent / f'{docx_path.stem}_black{docx_path.suffix}'
            alt.write_bytes(new_bytes)
            print(f"  (file locked, wrote to {alt.name})")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Force all text in DOCX files to pure black (#000000).')
    parser.add_argument('files', nargs='+', help='One or more .docx files to process')
    args = parser.parse_args()

    ok, fail = 0, 0
    for f in args.files:
        path = Path(f).resolve()
        if not path.exists():
            print(f"  SKIP: file not found: {f}")
            fail += 1
            continue
        if path.suffix.lower() != '.docx':
            print(f"  SKIP: not a .docx file: {f}")
            fail += 1
            continue

        print(f"  Processing: {path.name} ... ", end='', flush=True)
        if force_black_text_in_docx(path):
            print("OK")
            ok += 1
        else:
            print("FAIL")
            fail += 1

    print(f"\n  OK {ok}  FAIL {fail}")
    sys.exit(0 if fail == 0 else 1)


if __name__ == '__main__':
    main()