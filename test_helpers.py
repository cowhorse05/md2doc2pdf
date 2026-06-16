#!/usr/bin/env python3
"""
DocWizard helper tests.
Tests Mermaid rendering and DOCX black-text post-processing.
No pandoc dependency. Run: python test_helpers.py
"""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers.render_mermaid import (
    render_mermaid_to_png,
    extract_mermaid_blocks,
    render_all_mermaid_in_md,
)
from helpers.black_text import force_black_text_in_docx


class TestMermaidExtraction(unittest.TestCase):
    def test_extract_flowchart(self):
        md = """# Test
```mermaid
graph TB
  A --> B
```
"""
        p = Path(tempfile.mktemp(suffix='.md'))
        p.write_text(md, encoding='utf-8')
        try:
            blocks = extract_mermaid_blocks(p)
            self.assertEqual(len(blocks), 1)
            self.assertEqual(blocks[0]['name'], 'diagram_01')
            self.assertIn('A --> B', blocks[0]['code'])
        finally:
            p.unlink(missing_ok=True)

    def test_extract_journey(self):
        md = """```mermaid
journey
  title My day
  section Morning
    Wake up: 1: Me
```
"""
        p = Path(tempfile.mktemp(suffix='.md'))
        p.write_text(md, encoding='utf-8')
        try:
            blocks = extract_mermaid_blocks(p)
            self.assertEqual(len(blocks), 1)
            self.assertEqual(blocks[0]['name'], 'journey_01')
        finally:
            p.unlink(missing_ok=True)

    def test_extract_sequence(self):
        md = """```mermaid
sequenceDiagram
  A->>B: Hello
```
"""
        p = Path(tempfile.mktemp(suffix='.md'))
        p.write_text(md, encoding='utf-8')
        try:
            blocks = extract_mermaid_blocks(p)
            self.assertEqual(len(blocks), 1)
            self.assertEqual(blocks[0]['name'], 'sequence_01')
        finally:
            p.unlink(missing_ok=True)

    def test_extract_multiple(self):
        md = """```mermaid
graph LR
  A --> B
```

```mermaid
journey
  title Test
```
"""
        p = Path(tempfile.mktemp(suffix='.md'))
        p.write_text(md, encoding='utf-8')
        try:
            blocks = extract_mermaid_blocks(p)
            self.assertEqual(len(blocks), 2)
            self.assertEqual(blocks[0]['name'], 'diagram_01')
            self.assertEqual(blocks[1]['name'], 'journey_02')
        finally:
            p.unlink(missing_ok=True)

    def test_no_mermaid_blocks(self):
        md = "# Just text\n\nNo diagrams here."
        p = Path(tempfile.mktemp(suffix='.md'))
        p.write_text(md, encoding='utf-8')
        try:
            blocks = extract_mermaid_blocks(p)
            self.assertEqual(len(blocks), 0)
        finally:
            p.unlink(missing_ok=True)

    def test_extract_gantt(self):
        md = """```mermaid
gantt
  title Project
  section Phase 1
    Task 1: a1, 2024-01-01, 30d
```
"""
        p = Path(tempfile.mktemp(suffix='.md'))
        p.write_text(md, encoding='utf-8')
        try:
            blocks = extract_mermaid_blocks(p)
            self.assertEqual(len(blocks), 1)
            self.assertEqual(blocks[0]['name'], 'gantt_01')
        finally:
            p.unlink(missing_ok=True)


class TestMermaidRendering(unittest.TestCase):
    def test_render_simple_diagram(self):
        code = 'graph TB\n  A[Start] --> B[End]'
        p = Path(tempfile.mktemp(suffix='.png'))
        try:
            ok = render_mermaid_to_png(code, p)
            if ok:
                self.assertGreater(p.stat().st_size, 100)
            else:
                self.skipTest("mermaid.ink API unavailable (network issue)")
        finally:
            p.unlink(missing_ok=True)


class TestMermaidInPlace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_blocks_returns_zero(self):
        md = Path(self.tmp, 'test.md')
        md.write_text('# No diagrams', encoding='utf-8')
        n = render_all_mermaid_in_md(md)
        self.assertEqual(n, 0)

    def test_blocks_replaced(self):
        md = Path(self.tmp, 'test.md')
        md.write_text("""# Test

```mermaid
graph TB
  A --> B
```
""", encoding='utf-8')
        n = render_all_mermaid_in_md(md)
        if n == 0:
            self.skipTest("mermaid.ink API unavailable")
        content = md.read_text(encoding='utf-8')
        self.assertNotIn('```mermaid', content)
        self.assertIn('!', content)
        self.assertIn('.png', content)


class TestBlackText(unittest.TestCase):
    def test_nonexistent_file(self):
        ok = force_black_text_in_docx(Path('/nonexistent/file.docx'))
        self.assertFalse(ok)

    def test_non_docx_zip(self):
        p = Path(tempfile.mktemp(suffix='.docx'))
        p.write_text('not a zip file')
        try:
            ok = force_black_text_in_docx(p)
            self.assertFalse(ok)
        finally:
            p.unlink(missing_ok=True)


if __name__ == '__main__':
    print(f"Python: {sys.version.split()[0]}")
    print()
    unittest.main(verbosity=2)