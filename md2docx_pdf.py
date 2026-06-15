#!/usr/bin/env python3
"""
md2docx_pdf.py --- 大学生作业一站式转换工具
============================================
扫描目录，自动检测 .md / .docx / .pdf / .drawio，每个文件转为其余格式。

.md     → .docx + .pdf    (drawio 引用自动替换为图片)
.docx   → .md + .pdf
.pdf    → .md + .docx     (需要 pdftotext)
.drawio → .png + .svg     (需要 drawio MCP，agent 处理)

直接跑:  python md2docx_pdf.py           扫描目录，交互式互转
加 -y:   python md2docx_pdf.py -y        跳过询问
加图表:  python md2docx_pdf.py -y --drawio   含图表导出

GitHub: https://github.com/cowhorse05/md2doc2pdf
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
from typing import Optional, List, Tuple, Dict

VERSION = "1.2.0"
REPO_URL = "https://github.com/cowhorse05/md2doc2pdf"

# ── Supported extensions ────────────────────────────────────────
MD_EXTS = {'.md', '.markdown', '.txt'}
DOC_EXTS = {'.docx', '.doc'}
PDF_EXTS = {'.pdf'}
DRAWIO_EXTS = {'.drawio', '.dio'}
ALL_EXTS = MD_EXTS | DOC_EXTS | PDF_EXTS | DRAWIO_EXTS

# ── CSS for PDF ───────────────────────────────────────────────
CHINESE_CSS = """<style>
  body{font-family:"Microsoft YaHei","SimSun","PingFang SC","Noto Sans SC",sans-serif;font-size:14px;line-height:1.8;margin:40px auto;max-width:800px;color:#333}
  h1{font-size:22px;font-weight:bold;border-bottom:2px solid #3b82f6;padding-bottom:8px;margin-top:24px}
  h2{font-size:18px;color:#1f2937;border-bottom:1px solid #e5e7eb;padding-bottom:5px;margin-top:20px}
  h3{font-size:15px;color:#374151;margin-top:16px}
  table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}
  th,td{border:1px solid #ddd;padding:6px 10px;text-align:left}
  th{background:#f5f5f5;font-weight:700}tr:nth-child(even){background:#fafafa}
  code{background:#f4f4f4;padding:1px 5px;border-radius:3px;font-size:13px;font-family:"Consolas","Courier New",monospace}
  pre{background:#f8f8f8;border:1px solid #e5e7eb;border-radius:6px;padding:12px 16px;overflow-x:auto;font-size:13px}
  pre code{background:none;padding:0}
  blockquote{border-left:4px solid #3b82f6;margin:12px 0;padding:6px 16px;background:#eff6ff}
  hr{border:none;border-top:1px solid #ddd;margin:20px 0}
  img{max-width:100%}a{color:#3b82f6}strong{color:#1f2937}
  @media print{body{margin:0}@page{margin:2cm}}
</style>"""

# ── Browser paths per platform ─────────────────────────────────
BROWSER_SEARCH: Dict[str, List[str]] = {
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
        '/usr/bin/google-chrome', '/usr/bin/chromium-browser',
        '/usr/bin/chromium', '/snap/bin/chromium',
    ],
}


# ── Platform helpers ───────────────────────────────────────────

def plat() -> str:
    return platform.system()  # Windows / Darwin / Linux


def find_tool(name: str, extra_paths: Optional[List[str]] = None) -> Optional[str]:
    """Find a CLI tool: check PATH first, then extra_paths."""
    found = shutil.which(name)
    if found:
        return found
    if extra_paths:
        for p in extra_paths:
            if os.path.isfile(p):
                return p
    return None


# ── Pandoc check + install prompt ──────────────────────────────

PANDOC_INSTALL = {
    'Windows': 'winget install pandoc',
    'Darwin': 'brew install pandoc',
    'Linux': 'sudo apt install pandoc',
}


def ensure_pandoc() -> bool:
    """Check pandoc. If missing, ask user before installing."""
    if shutil.which('pandoc'):
        v = subprocess.run(['pandoc', '--version'], capture_output=True,
                           timeout=5).stdout.decode('utf-8', errors='replace').split('\n')[0]
        print(f"  pandoc: {v}")
        return True

    print("\n  [MISSING] pandoc 未安装")
    print(f"  安装命令: {PANDOC_INSTALL.get(plat(), '请访问 https://pandoc.org/installing.html')}")
    print()
    ans = input("  是否现在安装? [y/N] ").strip().lower()
    if ans == 'y':
        cmd = PANDOC_INSTALL.get(plat())
        if cmd:
            print(f"  正在执行: {cmd}")
            ret = os.system(cmd)
            if ret == 0 and shutil.which('pandoc'):
                print("  pandoc 安装成功")
                return True
    print("  跳过 pandoc，无法继续。请手动安装后重试。")
    return False


# ── pdftotext check ────────────────────────────────────────────

PDFTOTEXT_INSTALL = {
    'Windows': 'winget install xpdfreader.xpdf-tools    (或下载 https://www.xpdfreader.com)',
    'Darwin': 'brew install poppler',
    'Linux': 'sudo apt install poppler-utils',
}


def has_pdftotext() -> bool:
    return shutil.which('pdftotext') is not None


# ── Conversion Engine ──────────────────────────────────────────

def pandoc_convert(src: Path, dst: Path) -> bool:
    """Use pandoc to convert between supported formats."""
    cmd = ['pandoc', str(src), '-o', str(dst), '--standalone']
    try:
        subprocess.run(cmd, capture_output=True, timeout=120)
        return dst.exists() and dst.stat().st_size > 50
    except Exception:
        return False


def any_to_pdf(src: Path, dst: Path, browser: str) -> bool:
    """Convert anything pandoc can read → PDF via HTML + browser."""
    fd, html = tempfile.mkstemp(suffix='.html', prefix='md2pdf_')
    os.close(fd)

    # pandoc → HTML
    ok = pandoc_convert(src, Path(html))
    if not ok:
        try: os.unlink(html)
        except OSError: pass
        return False

    # Inject CSS
    try:
        with open(html, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace('<head>', f'<head><meta charset="UTF-8">{CHINESE_CSS}')
        with open(html, 'w', encoding='utf-8') as f:
            f.write(c)
    except Exception:
        try: os.unlink(html)
        except OSError: pass
        return False

    # Browser → PDF
    url = 'file:///' + html.replace('\\', '/')
    subprocess.run([browser, '--headless', '--disable-gpu', '--no-sandbox',
                    f'--print-to-pdf={dst}',
                    '--no-pdf-header-footer', '--no-margins',
                    '--virtual-time-budget=15000', url],
                   capture_output=True, timeout=60)
    try: os.unlink(html)
    except OSError: pass
    return dst.exists() and dst.stat().st_size > 500


def pdf_to_text(src: Path, dst: Path) -> bool:
    """Extract text from PDF using pdftotext → save as markdown."""
    # Try pdftotext with layout preservation
    try:
        subprocess.run(['pdftotext', '-layout', '-nopgbrk',
                        str(src), str(dst)],
                       capture_output=True, timeout=60)
        if dst.exists() and dst.stat().st_size > 20:
            # Wrap in markdown frontmatter
            with open(dst, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(dst, 'w', encoding='utf-8') as f:
                f.write(f"# {src.stem}\n\n> 由 PDF 自动提取，格式可能有损。\n\n{content}")
            return True
    except Exception:
        pass
    return False


# ── Smart convert: one file → other two formats ────────────────

def convert_file(src: Path, browser: str, output_dir: Path) -> Tuple[int, int]:
    """
    Convert one file to the other two formats.
    Returns (ok, fail).
    """
    suffix = src.suffix.lower()
    base = output_dir / src.stem
    ok, fail = 0, 0
    size = src.stat().st_size
    label = {'.md': 'MD', '.docx': 'DOCX', '.doc': 'DOC', '.pdf': 'PDF'}.get(suffix, suffix)

    print(f"\n[{label}] {src.name} ({size:,} bytes)")

    if suffix == '.md':
        # MD → DOCX + PDF
        d_docx = Path(str(base) + '.docx')
        d_pdf = Path(str(base) + '.pdf')
        print(f"  -> DOCX: {d_docx.name} ... ", end='', flush=True)
        if pandoc_convert(src, d_docx):
            print(f"OK ({d_docx.stat().st_size:,} bytes)"); ok += 1
        else:
            print("FAIL"); fail += 1

        print(f"  -> PDF:  {d_pdf.name} ... ", end='', flush=True)
        if browser and any_to_pdf(src, d_pdf, browser):
            print(f"OK ({d_pdf.stat().st_size:,} bytes)"); ok += 1
        elif not browser:
            print("SKIP (no browser)"); fail += 1
        else:
            print("FAIL"); fail += 1

    elif suffix in ('.docx', '.doc'):
        # DOCX → MD + PDF
        d_md = Path(str(base) + '.md')
        d_pdf = Path(str(base) + '.pdf')
        print(f"  -> MD:   {d_md.name} ... ", end='', flush=True)
        if pandoc_convert(src, d_md):
            print(f"OK ({d_md.stat().st_size:,} bytes)"); ok += 1
        else:
            print("FAIL"); fail += 1

        print(f"  -> PDF:  {d_pdf.name} ... ", end='', flush=True)
        if browser and any_to_pdf(src, d_pdf, browser):
            print(f"OK ({d_pdf.stat().st_size:,} bytes)"); ok += 1
        elif not browser:
            print("SKIP (no browser)"); fail += 1
        else:
            print("FAIL"); fail += 1

    elif suffix == '.pdf':
        # PDF → MD + DOCX (need pdftotext)
        d_md = Path(str(base) + '.md')
        d_docx = Path(str(base) + '_from_pdf.docx')

        if has_pdftotext():
            print(f"  -> MD:   {d_md.name} ... ", end='', flush=True)
            if pdf_to_text(src, d_md):
                print(f"OK ({d_md.stat().st_size:,} bytes)"); ok += 1
                # Now MD → DOCX
                print(f"  -> DOCX: {d_docx.name} ... ", end='', flush=True)
                if pandoc_convert(d_md, d_docx):
                    print(f"OK ({d_docx.stat().st_size:,} bytes)"); ok += 1
                else:
                    print("FAIL"); fail += 1
            else:
                print("FAIL"); fail += 1
        else:
            print(f"  -> MD/DOCX: SKIP (需要 pdftotext，未安装)")
            print(f"    安装: {PDFTOTEXT_INSTALL.get(plat(), '请搜索 poppler-utils')}")
            fail += 2

    return ok, fail


# ── Scan directory for documents ───────────────────────────────

def scan_dir(directory: str) -> Dict[str, List[Path]]:
    """Find all documents (.md/.docx/.pdf) and diagrams (.drawio) in directory."""
    found: Dict[str, List[Path]] = {
        '.md': [], '.docx': [], '.doc': [], '.pdf': [],
        '.drawio': [], '.dio': [],
    }
    patterns = ['*.md', '*.docx', '*.doc', '*.pdf', '*.drawio', '*.dio']
    for pat in patterns:
        for f in glob.glob(os.path.join(directory, pat)):
            p = Path(f).resolve()
            if p.name.startswith('~$'):
                continue
            ext = p.suffix.lower()
            if ext in found:
                found[ext].append(p)
    return found


# ── Main ───────────────────────────────────────────────────────

def main():
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description='文档互转：.md / .docx / .pdf 互相转换。不传文件则扫描当前目录。',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
示例:
  %(prog)s                  扫描当前目录，列出所有文档，询问后转换
  %(prog)s report.md        单文件 → 其余两种格式
  %(prog)s -f both *.md     批量转换
  %(prog)s --scan ./docs    扫描指定目录

GitHub: {REPO_URL}
        """
    )
    parser.add_argument('inputs', nargs='*',
                        help='要转换的文件，支持通配符。不传则扫描目录。')
    parser.add_argument('-f', '--format', default='both',
                        choices=['docx', 'pdf', 'both'],
                        help='输出格式 (仅对 .md 有效；其他格式固定转两种)')
    parser.add_argument('-o', '--output', metavar='DIR', help='输出目录')
    parser.add_argument('-s', '--scan', metavar='DIR', nargs='?', const='.',
                        help='扫描目录中的文档 (默认: 当前目录)')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='跳过确认，直接全部转换')
    parser.add_argument('--drawio', action='store_true',
                        help='启用 drawio 图表导出 (需要 drawio MCP)')
    parser.add_argument('--version', action='version',
                        version=f'md2docx_pdf v{VERSION}')

    args = parser.parse_args()

    print(f"\n  md2docx_pdf v{VERSION}  {REPO_URL}")
    print(f"  平台: {plat()}")

    # Check pandoc
    if not ensure_pandoc():
        sys.exit(1)

    # Find browser
    browser = None
    for name in ['google-chrome', 'chrome', 'chromium', 'msedge']:
        browser = find_tool(name, BROWSER_SEARCH.get(plat(), []))
        if browser:
            break
    if browser:
        print(f"  浏览器: {Path(browser).name}")
    else:
        print("  浏览器: 未检测到 (PDF 输出将跳过)")

    # ── Determine what to convert ──────────────────────────
    output_dir = Path(args.output).resolve() if args.output else None

    # Scan mode: no inputs given, or --scan specified
    if args.scan or not args.inputs:
        scan_path = args.scan if args.scan else '.'
        scan_path = os.path.abspath(scan_path)
        print(f"\n  扫描目录: {scan_path}")
        found = scan_dir(scan_path)

        # Count files
        total = sum(len(v) for v in found.values())
        if total == 0:
            print("\n  未找到 .md / .docx / .pdf 文件。")
            sys.exit(0)

        drawio_files = found.get('.drawio', []) + found.get('.dio', [])
        doc_total = total - len(drawio_files)

        print(f"\n  找到 {doc_total} 个文档, {len(drawio_files)} 个图表:")
        LABELS = {'.md': 'Markdown', '.docx': 'Word', '.doc': 'Word(旧)',
                  '.pdf': 'PDF', '.drawio': 'DrawIO', '.dio': 'DrawIO'}
        for ext in ['.md', '.docx', '.doc', '.pdf', '.drawio', '.dio']:
            files = found.get(ext, [])
            if files:
                label = LABELS.get(ext, ext)
                icon = '📊' if ext in ('.drawio', '.dio') else '📄'
                print(f"    {icon} {label} ({ext}): {len(files)} 个")
                for f in files:
                    print(f"      {f.name}")

        # Report drawio files
        if drawio_files:
            print(f"\n  [DRAWIO] 发现 {len(drawio_files)} 个图表文件")
            for f in drawio_files:
                print(f"    {f.name}")
            if not args.drawio:
                print("  提示: 加 --drawio 参数可自动导出为图片 (需 drawio MCP)")
                print("  或让 agent 处理: agent 调用 drawio MCP 导出 .png/.svg")

        # Ask user
        if not args.yes:
            print()
            prompt = "  全部文档互转?"
            if drawio_files:
                prompt += " (图表需 --drawio 或 agent 处理)"
            ans = input(f"{prompt} [Y/n] ").strip().lower()
            if ans and ans != 'y':
                print("  已取消。")
                sys.exit(0)

        out = output_dir or Path(scan_path)
        total_ok, total_fail = 0, 0
        # Only convert documents (not drawio - that's MCP/agent territory)
        for ext in ['.md', '.docx', '.doc', '.pdf']:
            for f in found.get(ext, []):
                ok, fail = convert_file(f, browser, out)
                total_ok += ok
                total_fail += fail

    else:
        # Direct mode: convert given files
        input_files = []
        for pattern in args.inputs:
            for m in glob.glob(pattern, recursive=True):
                p = Path(m).resolve()
                if p.suffix.lower() in ('.md', '.docx', '.doc', '.pdf'):
                    if not p.name.startswith('~$'):
                        input_files.append(p)

        # If .md and user specified -f single format, respect it
        if args.format != 'both':
            # Standard single-format mode for .md
            input_files_md = [f for f in input_files if f.suffix == '.md']
            input_files_other = [f for f in input_files if f.suffix != '.md']

            total_ok, total_fail = 0, 0
            if input_files_other:
                print(f"  (非 .md 文件忽略 -f 参数，固定转为两种格式)")

            for f in input_files_md:
                out = output_dir or f.parent
                base = out / f.stem
                if args.format in ('docx', 'both'):
                    d = Path(str(base) + '.docx')
                    print(f"\n[MD] {f.name} -> DOCX ... ", end='', flush=True)
                    if pandoc_convert(f, d):
                        print(f"OK ({d.stat().st_size:,} bytes)"); total_ok += 1
                    else:
                        print("FAIL"); total_fail += 1
                if args.format in ('pdf', 'both'):
                    d = Path(str(base) + '.pdf')
                    print(f"[MD] {f.name} -> PDF ... ", end='', flush=True)
                    if browser and any_to_pdf(f, d, browser):
                        print(f"OK ({d.stat().st_size:,} bytes)"); total_ok += 1
                    else:
                        print("SKIP" if not browser else "FAIL")
                        total_fail += 1
            for f in input_files_other:
                ok, fail = convert_file(f, browser, output_dir or f.parent)
                total_ok += ok
                total_fail += fail
        else:
            total_ok, total_fail = 0, 0
            for f in input_files:
                ok, fail = convert_file(f, browser, output_dir or f.parent)
                total_ok += ok
                total_fail += fail

    # ── Summary ───────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"  OK {total_ok}   FAIL {total_fail}")
    if total_fail == 0:
        print("  全部转换完成!")
    print(f"{'='*50}")
    sys.exit(0 if total_fail == 0 else 1)


if __name__ == '__main__':
    main()
