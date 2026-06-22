#!/usr/bin/env python3
"""
DOCX black-text post-processor.
Patches word/document.xml and word/styles.xml to force text color to
pure black (#000000).  Uses xml.etree.ElementTree for safe, namespace-aware
XML manipulation — deliberately avoids regex to prevent structural corruption
(e.g. breaking self-closing tags in theme1.xml).

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
from xml.etree import ElementTree as ET

# OOXML namespaces
NS_W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def _register_namespaces():
    """Register OOXML namespaces so ElementTree uses prefixes (not ns0/ns1)."""
    for prefix, uri in [('w', NS_W), ('a', NS_A), ('r', NS_R),
                         ('mc', 'http://schemas.openxmlformats.org/markup-compatibility/2006'),
                         ('w14', 'http://schemas.microsoft.com/office/word/2010/wordml')]:
        ET.register_namespace(prefix, uri)
    ET.register_namespace('', NS_W)  # default namespace for w: elements


def _patch_xml_with_etree(xml_bytes: bytes, xml_name: str) -> bytes:
    """Patch an OOXML XML file using ElementTree.

    Only modifies word/styles.xml and word/document.xml — all other
    XML files (especially word/theme/theme1.xml) are returned unchanged
    to avoid corrupting DrawingML namespace elements (a:srgbClr, etc.).
    """
    # ── SAFETY: only patch known wordprocessingML files ──────────
    SAFE_FILES = {'word/styles.xml', 'word/document.xml'}

    if xml_name not in SAFE_FILES:
        return xml_bytes

    _register_namespaces()

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        # Fallback for malformed XML: use scoped regex (w:color only)
        xml_str = xml_bytes.decode('utf-8')
        xml_str = re.sub(
            r'(<w:color\b[^>]*?)w:val="[^"]*"',
            r'\1w:val="000000"',
            xml_str
        )
        # Strip theme color references (they would override w:val)
        xml_str = re.sub(r'\s*w:themeColor="[^"]*"', '', xml_str)
        xml_str = re.sub(r'\s*w:themeShade="[^"]*"', '', xml_str)
        xml_str = re.sub(r'\s*w:themeTint="[^"]*"', '', xml_str)
        return xml_str.encode('utf-8')

    color_tag = f'{{{NS_W}}}color'
    for elem in root.iter(color_tag):
        val_attr = f'{{{NS_W}}}val'
        if val_attr in elem.attrib:
            elem.set(val_attr, '000000')
        # Remove theme color references — they override explicit w:val
        for theme_attr in (f'{{{NS_W}}}themeColor', f'{{{NS_W}}}themeShade',
                           f'{{{NS_W}}}themeTint'):
            if theme_attr in elem.attrib:
                del elem.attrib[theme_attr]

    # For styles.xml: ensure <w:rPrDefault> forces black as document default
    if xml_name == 'word/styles.xml':
        doc_defaults = root.find(f'{{{NS_W}}}docDefaults')
        if doc_defaults is not None:
            rpr_default = doc_defaults.find(f'{{{NS_W}}}rPrDefault')
            if rpr_default is None:
                rpr_default = ET.SubElement(doc_defaults,
                                            f'{{{NS_W}}}rPrDefault')
            rpr = rpr_default.find(f'{{{NS_W}}}rPr')
            if rpr is None:
                rpr = ET.SubElement(rpr_default, f'{{{NS_W}}}rPr')
            # Only add w:color if not already present
            existing = rpr.find(f'{{{NS_W}}}color')
            if existing is None:
                color = ET.SubElement(rpr, f'{{{NS_W}}}color')
                color.set(f'{{{NS_W}}}val', '000000')

    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def force_black_text_in_docx(docx_path: Path) -> bool:
    """Post-process a docx file to force ALL text to black.

    Uses xml.etree.ElementTree for safe namespace-aware XML manipulation.
    Only patches word/document.xml and word/styles.xml — deliberately
    skips word/theme/theme1.xml because theme files use the DrawingML
    namespace (a:srgbClr) which has different element structure than
    wordprocessingML (w:color).  Broad regex on theme files can break
    self-closing tags and corrupt the DOCX.

    Returns True on success.
    """
    try:
        # Read original zip into memory
        with zipfile.ZipFile(docx_path, 'r') as zin:
            files = {name: zin.read(name) for name in zin.namelist()}

        patched = 0

        for name in list(files.keys()):
            if not name.endswith('.xml'):
                continue
            try:
                new_xml = _patch_xml_with_etree(files[name], name)
            except Exception:
                continue

            if new_xml != files[name]:
                files[name] = new_xml
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