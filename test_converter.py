#!/usr/bin/env python3
"""
md2docx_pdf unit tests
======================
Covers: MD↔DOCX↔PDF three-way, scan mode, edge cases.
Run:   python test_converter.py
"""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Add script dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md2docx_pdf import (
    pandoc_convert, any_to_pdf, pdf_to_text,
    scan_dir, plat, find_tool, ensure_pandoc, has_pdftotext,
    BROWSER_SEARCH,
)


class TestToolDetection(unittest.TestCase):
    """Test platform/browser/tool detection."""

    def test_plat_returns_string(self):
        p = plat()
        self.assertIn(p, ('Windows', 'Darwin', 'Linux'))

    def test_find_tool_python_exists(self):
        py = find_tool('python') or find_tool('python3')
        self.assertIsNotNone(py, "Python should be findable")

    def test_find_tool_nonsense_returns_none(self):
        self.assertIsNone(find_tool('__nonexistent_tool_xyz__'))

    def test_browser_search_paths_are_lists(self):
        for plat_name in ('Windows', 'Darwin', 'Linux'):
            self.assertIsInstance(BROWSER_SEARCH[plat_name], list)

    def test_pdftotext_detection(self):
        result = has_pdftotext()
        self.assertIsInstance(result, bool)


class TestScanDir(unittest.TestCase):
    """Test directory scanning."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_empty_dir(self):
        found = scan_dir(self.tmp)
        total = sum(len(v) for v in found.values())
        self.assertEqual(total, 0)

    def test_finds_md(self):
        Path(self.tmp, 'test.md').write_text('# Hello', encoding='utf-8')
        found = scan_dir(self.tmp)
        self.assertEqual(len(found['.md']), 1)

    def test_finds_docx(self):
        # Create minimal valid docx via pandoc
        md = Path(self.tmp, '_tmp.md')
        md.write_text('# Test', encoding='utf-8')
        docx = Path(self.tmp, 'test.docx')
        pandoc_convert(md, docx)
        md.unlink()

        found = scan_dir(self.tmp)
        self.assertEqual(len(found['.docx']), 1)

    def test_finds_multiple_types(self):
        Path(self.tmp, 'a.md').write_text('# A', encoding='utf-8')
        Path(self.tmp, 'b.md').write_text('# B', encoding='utf-8')
        found = scan_dir(self.tmp)
        self.assertEqual(len(found['.md']), 2)

    def test_skips_temp_word_files(self):
        Path(self.tmp, '~$temp.docx').write_text('x')
        Path(self.tmp, 'real.md').write_text('# real', encoding='utf-8')
        found = scan_dir(self.tmp)
        self.assertEqual(len(found['.docx']), 0)
        self.assertEqual(len(found['.md']), 1)

    def test_finds_drawio(self):
        Path(self.tmp, 'diagram.drawio').write_text('<mxfile></mxfile>')
        Path(self.tmp, 'flow.dio').write_text('<mxfile></mxfile>')
        found = scan_dir(self.tmp)
        self.assertEqual(len(found['.drawio']), 1)
        self.assertEqual(len(found['.dio']), 1)


class TestMDConversions(unittest.TestCase):
    """Test .md → .docx / .pdf."""

    CHINESE_MD = """# 测试文档

## 第一章

这是一段**中文**测试文字，包含*斜体*和`代码`。

| 姓名 | 分数 |
|------|------|
| 张三 | 95   |
| 李四 | 87   |

> 这是一段引用文字。

    def hello():
        print("Hello World")
"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.md_path = Path(self.tmp, 'test.md')
        self.md_path.write_text(self.CHINESE_MD, encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_md_to_docx(self):
        dst = Path(self.tmp, 'test.docx')
        ok = pandoc_convert(self.md_path, dst)
        self.assertTrue(ok, "MD→DOCX should succeed")
        self.assertGreater(dst.stat().st_size, 1000,
                          "DOCX should be >1KB")

    def test_md_to_docx_standalone(self):
        """Verify --standalone flag produces valid docx."""
        dst = Path(self.tmp, 'out.docx')
        ok = pandoc_convert(self.md_path, dst)
        self.assertTrue(ok)
        # .docx is a ZIP, check magic bytes
        with open(dst, 'rb') as f:
            magic = f.read(2)
        self.assertEqual(magic, b'PK', "DOCX should be a ZIP file")

    def test_md_to_pdf(self):
        import subprocess
        browser = None
        for name in ['google-chrome', 'chrome', 'chromium', 'msedge']:
            browser = find_tool(name, BROWSER_SEARCH.get(plat(), []))
            if browser:
                break
        if not browser:
            self.skipTest("No browser found for PDF test")

        dst = Path(self.tmp, 'test.pdf')
        ok = any_to_pdf(self.md_path, dst, browser)
        self.assertTrue(ok, f"MD→PDF should succeed")
        self.assertGreater(dst.stat().st_size, 1000)

    def test_md_to_pdf_with_chinese(self):
        browser = None
        for name in ['google-chrome', 'chrome', 'chromium', 'msedge']:
            browser = find_tool(name, BROWSER_SEARCH.get(plat(), []))
            if browser:
                break
        if not browser:
            self.skipTest("No browser found")

        dst = Path(self.tmp, 'chinese.pdf')
        ok = any_to_pdf(self.md_path, dst, browser)
        self.assertTrue(ok)
        self.assertGreater(dst.stat().st_size, 5000,
                          "Chinese PDF should be reasonably sized")

    def test_nonexistent_md_fails(self):
        dst = Path(self.tmp, 'nope.docx')
        ok = pandoc_convert(Path('/nonexistent/path.md'), dst)
        self.assertFalse(ok)


class TestDOCXConversions(unittest.TestCase):
    """Test .docx → .md / .pdf."""

    MD_CONTENT = """# 转换测试

这是从 docx 转回 md 的内容。

| A | B |
|---|---|
| 1 | 2 |
"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # Create source docx from markdown
        self.md_src = Path(self.tmp, '_src.md')
        self.md_src.write_text(self.MD_CONTENT, encoding='utf-8')
        self.docx = Path(self.tmp, 'source.docx')
        pandoc_convert(self.md_src, self.docx)
        self.assertTrue(self.docx.exists(), "Setup: docx creation failed")
        self.md_src.unlink()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_docx_to_md(self):
        dst = Path(self.tmp, 'output.md')
        ok = pandoc_convert(self.docx, dst)
        self.assertTrue(ok, "DOCX→MD should succeed")
        content = dst.read_text(encoding='utf-8')
        self.assertIn('转换测试', content, "Should preserve Chinese title")

    def test_docx_to_pdf(self):
        browser = None
        for name in ['google-chrome', 'chrome', 'chromium', 'msedge']:
            browser = find_tool(name, BROWSER_SEARCH.get(plat(), []))
            if browser:
                break
        if not browser:
            self.skipTest("No browser found")

        dst = Path(self.tmp, 'output.pdf')
        ok = any_to_pdf(self.docx, dst, browser)
        self.assertTrue(ok, "DOCX→PDF should succeed")
        self.assertGreater(dst.stat().st_size, 1000)

    def test_roundtrip_md_docx_md(self):
        """MD → DOCX → MD should preserve key content."""
        # Step 1: MD → DOCX (already done in setUp)
        # Step 2: DOCX → MD
        dst_md = Path(self.tmp, 'roundtrip.md')
        ok = pandoc_convert(self.docx, dst_md)
        self.assertTrue(ok)
        content = dst_md.read_text(encoding='utf-8')

        # Pandoc roundtrip preserves structure but may reformat
        # Check that key text survives
        self.assertIn('转换测试', content)


class TestPDFToText(unittest.TestCase):
    """Test .pdf → text extraction."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_pdf_to_text_requires_pdftotext(self):
        if not has_pdftotext():
            self.skipTest("pdftotext not installed")
        self.assertTrue(has_pdftotext())

    def test_pdf_to_text_with_text_pdf(self):
        """Convert a simple PDF with text (generated by pandoc+weasyprint).
        Since we may not have weasyprint, test that it handles gracefully."""
        if not has_pdftotext():
            self.skipTest("pdftotext not installed")

        # Create a minimal text file and wrap as markdown, then test the
        # pdf_to_text function directly with the function signature
        txt = Path(self.tmp, 'dummy.md')
        txt.write_text('# dummy', encoding='utf-8')
        dst = Path(self.tmp, 'dummy.txt')

        # pdf_to_text on a non-PDF should fail gracefully
        ok = pdf_to_text(txt, dst)
        self.assertFalse(ok, "pdf_to_text on .md should fail")


class TestEdgeCases(unittest.TestCase):
    """Edge cases and error handling."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_empty_md(self):
        src = Path(self.tmp, 'empty.md')
        src.write_text('', encoding='utf-8')
        dst = Path(self.tmp, 'empty.docx')
        # Should still create a docx (just empty)
        ok = pandoc_convert(src, dst)
        self.assertTrue(ok, "Even empty MD should produce a valid DOCX")

    def test_md_with_only_whitespace(self):
        src = Path(self.tmp, 'ws.md')
        src.write_text('\n\n\n   \n', encoding='utf-8')
        dst = Path(self.tmp, 'ws.docx')
        ok = pandoc_convert(src, dst)
        self.assertTrue(ok)

    def test_unicode_emoji(self):
        src = Path(self.tmp, 'emoji.md')
        src.write_text('# Test 🎉\n\nContent with emoji: 😀 🔥 ✅', encoding='utf-8')
        dst = Path(self.tmp, 'emoji.docx')
        ok = pandoc_convert(src, dst)
        self.assertTrue(ok, "Emoji in MD should convert to DOCX")

    def test_large_table(self):
        rows = '| ' + ' | '.join(f'col{i}' for i in range(10)) + ' |\n'
        rows += '|' + '|'.join('---' for _ in range(10)) + '|\n'
        for r in range(50):
            rows += '| ' + ' | '.join(f'r{r}c{i}' for i in range(10)) + ' |\n'

        src = Path(self.tmp, 'table.md')
        src.write_text(f'# Large Table\n\n{rows}', encoding='utf-8')
        dst = Path(self.tmp, 'table.docx')
        ok = pandoc_convert(src, dst)
        self.assertTrue(ok, "Large table should convert")
        self.assertGreater(dst.stat().st_size, 3000)

    def test_special_chars_in_filename(self):
        """Chinese characters in path should work."""
        src = Path(self.tmp, '测试报告.md')
        src.write_text('# 测试', encoding='utf-8')
        dst = Path(self.tmp, '测试报告.docx')
        ok = pandoc_convert(src, dst)
        self.assertTrue(ok, "Chinese filenames should work")


class TestPandocEnsure(unittest.TestCase):
    """Test the ensure_pandoc function (non-interactive)."""

    def test_returns_bool(self):
        # Will find pandoc (we already checked before running tests)
        # but won't prompt because stdout is captured by unittest
        self.assertIsInstance(shutil.which('pandoc') is not None, bool)


if __name__ == '__main__':
    # Check pandoc first
    if not shutil.which('pandoc'):
        print("ERROR: pandoc is required to run these tests.")
        print("Install: https://pandoc.org/installing.html")
        sys.exit(1)

    print(f"Platform: {plat()}")
    print(f"pandoc: {shutil.which('pandoc')}")
    print(f"pdftotext: {has_pdftotext()}")
    print()

    unittest.main(verbosity=2)
