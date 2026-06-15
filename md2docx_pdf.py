#!/usr/bin/env python3
"""
md2docx_pdf.py --- 大学生作业一站式转换工具
============================================
扫描目录，自动检测 .md / .docx / .pdf / .tex / .drawio，每个文件转为其余格式。

.md     → .docx + .pdf    (drawio 引用自动替换为图片)
.docx   → .md + .pdf
.pdf    → .md + .docx     (需要 pdftotext)
.tex    → .pdf            (需要 xelatex / pdflatex，可选)
.drawio → .png + .svg     (需要 drawio MCP)

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

VERSION = "1.5.0"
REPO_URL = "https://github.com/cowhorse05/md2doc2pdf"

# ── Supported extensions ────────────────────────────────────────
MD_EXTS = {'.md', '.markdown', '.txt'}
DOC_EXTS = {'.docx', '.doc'}
PDF_EXTS = {'.pdf'}
DRAWIO_EXTS = {'.drawio', '.dio'}
TEX_EXTS = {'.tex'}
ALL_EXTS = MD_EXTS | DOC_EXTS | PDF_EXTS | DRAWIO_EXTS | TEX_EXTS

# ── LaTeX install instructions ──────────────────────────────────
LATEX_INSTALL = {
    'Windows': 'winget install MiKTeX.MiKTeX   (或 https://miktex.org/download)',
    'Darwin': 'brew install --cask mactex        (约 4GB，也可用 brew install basictex)',
    'Linux': 'sudo apt install texlive-xetex texlive-latex-extra texlive-lang-chinese',
}

# ── Config file ──────────────────────────────────────────────────
def _config_path() -> Path:
    """Path to the persistent config file (alongside the script)."""
    return Path(__file__).resolve().parent / '.md2pdf_setup.json'


def load_setup_config() -> dict:
    """Load saved setup choices."""
    cp = _config_path()
    if cp.exists():
        try:
            import json
            return json.loads(cp.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


def save_setup_config(cfg: dict):
    """Save setup choices to disk."""
    import json
    _config_path().write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2),
        encoding='utf-8')


# ── Self-update ──────────────────────────────────────────────────

def check_update():
    """Check GitHub for newer versions and offer to git pull."""
    script_dir = Path(__file__).resolve().parent
    git_dir = script_dir / '.git'
    if not git_dir.exists():
        print("  未检测到 git 仓库，无法自动更新。")
        print(f"  请手动访问: {REPO_URL}")
        return False

    print(f"  当前版本: v{VERSION}")
    print(f"  远程仓库: {REPO_URL}")
    print()

    # Fetch latest tags from remote
    print("  正在检查更新...")
    ret = subprocess.run(
        ['git', 'fetch', 'origin', '--tags'],
        capture_output=True, timeout=30, cwd=str(script_dir)
    )
    if ret.returncode != 0:
        print("  ⚠ 无法连接到远程仓库，请检查网络。")
        print(f"  手动检查: {REPO_URL}/releases")
        return False

    # Get latest tag
    ret = subprocess.run(
        ['git', 'tag', '--sort=-creatordate'],
        capture_output=True, timeout=10, cwd=str(script_dir),
        text=True
    )
    tags = [t.strip() for t in ret.stdout.strip().split('\n') if t.strip()]
    # Non-tagged: check if origin/main is ahead
    ret2 = subprocess.run(
        ['git', 'rev-list', '--count', 'HEAD..origin/main'],
        capture_output=True, timeout=10, cwd=str(script_dir),
        text=True
    )
    behind = int(ret2.stdout.strip()) if ret2.stdout.strip().isdigit() else 0

    if behind > 0 or (tags and tags[0] != f'v{VERSION}'):
        print(f"  🔔 发现新版本!")
        if tags:
            print(f"     最新标签: {tags[0]}")
        print(f"     落后 {behind} 个提交")
        print()
        ans = input("  是否更新到最新版本? [Y/n] ").strip().lower()
        if ans != 'n':
            print("  正在 git pull...")
            ret = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                capture_output=True, timeout=30, cwd=str(script_dir)
            )
            if ret.returncode == 0:
                print("  ✓ 更新成功! 请重新运行以使用新版本。")

                # Re-read VERSION from updated file
                version_file = script_dir / 'md2docx_pdf.py'
                if version_file.exists():
                    import re
                    content = version_file.read_text(encoding='utf-8')
                    m = re.search(r'VERSION\s*=\s*"([^"]+)"', content)
                    if m:
                        print(f"  新版本: v{m.group(1)}")
                return True
            else:
                print("  ⚠ git pull 失败，请手动更新:")
                print(f"    cd {script_dir} && git pull origin main")
                return False
        else:
            print("  已跳过更新。")
            return False
    else:
        print("  ✓ 已是最新版本。")
        return True

def setup_wizard():
    """
    Interactive setup wizard --- walks through all dependencies,
    letting the user choose which optional components to install.
    """
    cfg = load_setup_config()
    installed = set(cfg.get('installed', []))
    skipped = set(cfg.get('skipped', []))

    print()
    print("=" * 60)
    print("  md2docx_pdf 设置向导")
    print("=" * 60)
    print()

    step = 0
    total = 5

    # ── Step 1: Python ───────────────────────────────────────
    step += 1
    py_ver = sys.version.split()[0]
    print(f"  [{step}/{total}] Python 环境")
    print(f"  Python {py_ver}  ✓")
    print()

    # ── Step 2: pandoc (required) ────────────────────────────
    step += 1
    print(f"  [{step}/{total}] pandoc (必装，所有格式转换都需要)")
    if shutil.which('pandoc'):
        v = subprocess.run(
            ['pandoc', '--version'], capture_output=True, timeout=5
        ).stdout.decode('utf-8', errors='replace').split('\n')[0]
        print(f"  {v}  ✓")
        installed.discard('pandoc')
        skipped.discard('pandoc')
    else:
        print("  [缺失] pandoc 未安装")
        cmd = PANDOC_INSTALL.get(plat(), '请访问 https://pandoc.org/installing.html')
        print(f"  安装命令: {cmd}")
        print()
        ans = input("  是否现在安装? [Y/n] ").strip().lower()
        if ans != 'n':
            print(f"  正在执行: {cmd}")
            ret = os.system(cmd)
            if ret == 0 and shutil.which('pandoc'):
                print("  pandoc 安装成功 ✓")
                installed.add('pandoc')
                skipped.discard('pandoc')
            else:
                print("  安装可能失败，请手动安装后重试。")
        else:
            print("  已跳过 (pandoc 是必装项，转换前需要手动安装)")
            skipped.add('pandoc')
    print()

    # ── Step 3: pdftotext (optional) ─────────────────────────
    step += 1
    print(f"  [{step}/{total}] pdftotext (可选，PDF → 文字提取)")
    print("  用途: 把 PDF 转回 .md / .docx，提取 PDF 中的文字内容")
    if has_pdftotext():
        print("  pdftotext 已安装 ✓")
        installed.add('pdftotext')
        skipped.discard('pdftotext')
    else:
        cmd = PDFTOTEXT_INSTALL.get(plat(), '请搜索 poppler-utils')
        print(f"  [未安装] 安装命令: {cmd}")
        print()
        ans = input("  是否安装? [y/N] ").strip().lower()
        if ans == 'y':
            print(f"  正在执行: {cmd}")
            ret = os.system(cmd)
            if ret == 0 and has_pdftotext():
                print("  pdftotext 安装成功 ✓")
                installed.add('pdftotext')
                skipped.discard('pdftotext')
            else:
                print("  安装可能失败，请手动安装后重试。")
                skipped.add('pdftotext')
        else:
            print("  已跳过 (以后需要可重新运行 --setup)")
            skipped.add('pdftotext')
    print()

    # ── Step 4: LaTeX (optional) ─────────────────────────────
    step += 1
    print(f"  [{step}/{total}] LaTeX (可选，.tex → PDF 编译)")
    print("  用途: 编译 .tex 文件为 PDF")
    print("  ⚠ 注意: 安装包较大 (数百MB ~ 4GB)，仅 .tex 文件编译需要")
    latex_cmd = has_latex()
    if latex_cmd:
        print(f"  {Path(latex_cmd).name} 已安装 ✓")
        installed.add('latex')
        skipped.discard('latex')
    else:
        cmd = LATEX_INSTALL.get(plat(), '手动安装 texlive 或 miktex')
        print(f"  [未安装] 安装命令: {cmd}")
        print()
        ans = input("  是否安装? [y/N] ").strip().lower()
        if ans == 'y':
            print(f"  正在执行: {cmd}")
            print("  (安装可能需要较长时间，请耐心等待...)")
            ret = os.system(cmd)
            if ret == 0 and has_latex():
                print("  LaTeX 安装成功 ✓")
                installed.add('latex')
                skipped.discard('latex')
            else:
                print("  安装可能失败，请手动安装后重试。")
                skipped.add('latex')
        else:
            print("  已跳过 (以后需要可重新运行 --setup)")
            skipped.add('latex')
    print()

    # ── Step 5: Browser (PDF output) ─────────────────────────
    step += 1
    print(f"  [{step}/{total}] 浏览器 (PDF 输出需要)")
    print("  用途: HTML → PDF 渲染，生成排版精美的 PDF 文件")
    browser = None
    for name in ['google-chrome', 'chrome', 'chromium', 'msedge']:
        browser = find_tool(name, BROWSER_SEARCH.get(plat(), []))
        if browser:
            break
    if browser:
        print(f"  {Path(browser).name} ✓  ({browser})")
        installed.add('browser')
        skipped.discard('browser')
    else:
        print("  [未检测到] 搜索了以下位置:")
        for p in BROWSER_SEARCH.get(plat(), []):
            exists = "✓" if os.path.isfile(p) else "✗"
            print(f"    {exists} {p}")
        print()
        print("  请选择:")
        print("    1. 手动输入浏览器路径")
        print("    2. 安装 Chrome (推荐)")
        print("    3. 跳过 (PDF 输出将不可用)")
        ans = input("  请选择 [1/2/3] (默认 3): ").strip()
        if ans == '1':
            path = input("  请输入浏览器可执行文件路径: ").strip()
            if path and (os.path.isfile(path) or shutil.which(path)):
                cfg['browser_path'] = path
                print(f"  已设置浏览器路径: {path}")
                installed.add('browser')
            else:
                print("  路径无效，已跳过。")
                skipped.add('browser')
        elif ans == '2':
            p = plat()
            if p == 'Windows':
                print("  请手动下载安装 Chrome: https://www.google.com/chrome/")
                print("  或使用系统自带的 Edge (通常自动检测到)")
            elif p == 'Darwin':
                print("  brew install --cask google-chrome")
                print("  或手动下载: https://www.google.com/chrome/")
                ans2 = input("  是否用 brew 安装? [y/N] ").strip().lower()
                if ans2 == 'y':
                    os.system('brew install --cask google-chrome')
            else:
                print("  sudo apt install chromium-browser")
                print("  或: wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -")
                ans2 = input("  是否用 apt 安装 chromium? [y/N] ").strip().lower()
                if ans2 == 'y':
                    os.system('sudo apt install -y chromium-browser')
            skipped.add('browser')
        else:
            print("  已跳过 (PDF 输出将不可用，以后需要可重新运行 --setup)")
            skipped.add('browser')
    print()

    # ── Step 6: Final choice — scan & execute? ────────────────
    step += 1
    print(f"  [{step}/{step}] 【最后选项】是否现在扫描目录并完成任务?")
    print()
    if 'pandoc' in skipped:
        print("  ⚠ pandoc 未安装，无法继续转换。请先安装 pandoc。")
        print()
    else:
        print("  环境配好了！要不要现在就扫描当前目录，开始转换文档？")
        print("    A. 是，扫描目录并转换")
        print("    B. 我先填 task.md，待会说「执行」")
        print("    C. 先不，以后再说")
        print()
        ans = input("  请选择 [A/B/C] (默认 B): ").strip().upper()
        cfg['final_choice'] = ans if ans else 'B'

        if ans == 'A':
            cfg['auto_scan'] = True
            save_setup_config(cfg)
            print()
            print("=" * 60)
            print("  开始扫描目录...")
            print("=" * 60)
            # Fall through to scan mode — return signal to main()
            # We set a flag in config so main() knows to auto-scan
        elif ans == 'C':
            print()
            print("  好的，随时可以说「执行 task.md」或运行:")
            print("    python md2docx_pdf.py")
            print("    python md2docx_pdf.py -y")
        else:
            print()
            print("  好的，请把要转换的文件填到 task.md 的「我的任务」里，")
            print("  勾上要转的格式，然后说「执行 task.md」。")
            print()
            print("  或者直接运行:")
            print("    python md2docx_pdf.py          扫描目录，交互转换")
            print("    python md2docx_pdf.py -y       跳过询问，直接全转")
            print("    python md2docx_pdf.py file.md  单文件互转")

    # ── Summary ──────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  设置完成!")
    print()
    if installed:
        print(f"  ✓ 已安装: {', '.join(sorted(installed))}")
    if skipped:
        skipped_friendly = []
        for s in sorted(skipped):
            label = {
                'pandoc': 'pandoc (必装!)',
                'pdftotext': 'pdftotext (PDF→文字)',
                'latex': 'LaTeX (.tex→PDF)',
                'browser': '浏览器 (PDF输出)',
            }.get(s, s)
            skipped_friendly.append(label)
        print(f"  ○ 已跳过: {', '.join(skipped_friendly)}")
    if 'pandoc' in skipped:
        print()
        print("  ⚠ pandoc 是必装项! 转换前请先手动安装:")
        print(f"    {PANDOC_INSTALL.get(plat(), 'https://pandoc.org/installing.html')}")
    print()
    print("  提示: 可随时重新运行 python md2docx_pdf.py --setup 安装跳过的组件")
    print("  更新: python md2docx_pdf.py --update    检查并更新到最新版本")
    print("=" * 60)

    # Save choices
    cfg['installed'] = sorted(installed)
    cfg['skipped'] = sorted(skipped)
    cfg['last_setup'] = True
    save_setup_config(cfg)

    # If auto_scan, don't exit — return to main() for scan+convert
    if cfg.get('auto_scan'):
        return  # Let main() continue to scan and convert

    # If pandoc missing, don't proceed to conversion
    if 'pandoc' in skipped:
        sys.exit(1)
    sys.exit(0)

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


def has_latex() -> Optional[str]:
    """Return the path to xelatex or pdflatex, whichever is available."""
    for cmd in ('xelatex', 'pdflatex'):
        p = shutil.which(cmd)
        if p:
            return p
    return None


# ── Conversion Engine ──────────────────────────────────────────

# ── Reference DOCX (black text) ─────────────────────────────────
_REF_DOCX: Optional[Path] = None


def _ensure_reference_docx() -> Optional[Path]:
    """Create a reference.docx with all text forced to black.
    Cached in memory—only generated once per session.
    """
    global _REF_DOCX
    if _REF_DOCX is not None:
        return _REF_DOCX

    import zipfile, re as _re

    script_dir = Path(__file__).resolve().parent
    ref_path = script_dir / 'reference.docx'
    tmp_dir = script_dir / '_ref_tmp'

    try:
        # Step 1: generate minimal docx
        md = script_dir / '_ref_src.md'
        md.write_text('# X\n\nBody.\n\n|A|B|\n|-|-|\n|1|2|\n', encoding='utf-8')
        subprocess.run(['pandoc', str(md), '-o', str(ref_path), '--standalone'],
                       capture_output=True, timeout=30)
        md.unlink()

        # Step 2: extract, fix xml, repack
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir()

        with zipfile.ZipFile(ref_path) as z:
            z.extractall(str(tmp_dir))

        # Patch styles.xml – force all colors to black
        styles_path = tmp_dir / 'word' / 'styles.xml'
        if styles_path.exists():
            xml = styles_path.read_text(encoding='utf-8')
            xml = _re.sub(r'<w:color w:val="[^"]*"', '<w:color w:val="000000"', xml)
            # Ensure default run props force black
            if '<w:rPrDefault>' not in xml:
                xml = xml.replace(
                    '</w:docDefaults>',
                    '<w:rPrDefault><w:rPr><w:color w:val="000000"/></w:rPr></w:rPrDefault></w:docDefaults>')
            styles_path.write_text(xml, encoding='utf-8')

        # Patch document.xml
        doc_xml = tmp_dir / 'word' / 'document.xml'
        if doc_xml.exists():
            xml = doc_xml.read_text(encoding='utf-8')
            xml = _re.sub(r'<w:color w:val="[^"]*"', '<w:color w:val="000000"', xml)
            doc_xml.write_text(xml, encoding='utf-8')

        # Repack
        ref_path.unlink()
        with zipfile.ZipFile(ref_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for root, _, files in os.walk(str(tmp_dir)):
                for fn in files:
                    full = Path(root) / fn
                    arc = str(full.relative_to(tmp_dir)).replace('\\', '/')
                    zout.write(str(full), arc)

        shutil.rmtree(tmp_dir)
        _REF_DOCX = ref_path
        return ref_path

    except Exception as e:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"  (参考模板生成失败，使用默认样式: {e})")
        return None


def pandoc_convert(src: Path, dst: Path) -> bool:
    """Use pandoc to convert between supported formats.
    Uses black-text reference.docx for all DOCX output.
    """
    cmd = ['pandoc', str(src), '-o', str(dst), '--standalone']

    # Use reference docx for .docx output to force black text
    if dst.suffix.lower() == '.docx':
        ref = _ensure_reference_docx()
        if ref and ref.exists():
            cmd += ['--reference-doc=' + str(ref)]

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


def tex_to_pdf(src: Path, dst: Path, latex_cmd: str) -> bool:
    """Compile .tex to PDF using xelatex/pdflatex.
    Runs twice for cross-references. Cleans .aux/.log junk.
    """
    work_dir = dst.parent
    base = src.stem

    for _ in range(2):
        subprocess.run(
            [latex_cmd, '-interaction=nonstopmode',
             '-output-directory=' + str(work_dir), str(src)],
            capture_output=True, timeout=120, cwd=str(work_dir))

    pdf = work_dir / (base + '.pdf')
    if pdf.exists() and pdf.stat().st_size > 500:
        if pdf.resolve() != dst.resolve():
            shutil.move(str(pdf), str(dst))
        for ext in ('.aux', '.log', '.out', '.toc', '.synctex.gz'):
            (work_dir / (base + ext)).unlink(missing_ok=True)
        return True
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
    label = {'.md': 'MD', '.docx': 'DOCX', '.doc': 'DOC',
             '.pdf': 'PDF', '.tex': 'TEX', '.drawio': 'DRAWIO'}.get(suffix, suffix)

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

    elif suffix == '.tex':
        # LaTeX → PDF (and optionally MD via pdftotext after)
        latex_cmd = has_latex()
        d_pdf = Path(str(base) + '.pdf')
        if latex_cmd:
            latex_name = Path(latex_cmd).name
            print(f"  -> PDF:  {d_pdf.name} ... ", end='', flush=True)
            if tex_to_pdf(src, d_pdf, latex_cmd):
                sz = d_pdf.stat().st_size
                print(f"OK ({sz:,} bytes) via {latex_name}"); ok += 1
            else:
                print("FAIL (编译错误，查看 .log)"); fail += 1
        else:
            print(f"  -> PDF:  SKIP (LaTeX 未安装)")
            print(f"    安装: {LATEX_INSTALL.get(plat(), '手动安装 texlive 或 miktex')}")
            fail += 1

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
        '.md': [], '.docx': [], '.doc': [], '.pdf': [], '.tex': [],
        '.drawio': [], '.dio': [],
    }
    patterns = ['*.md', '*.docx', '*.doc', '*.pdf', '*.tex',
                '*.drawio', '*.dio']
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
    parser.add_argument('--setup', action='store_true',
                        help='运行交互式设置向导，选择安装可选组件')
    parser.add_argument('--install', action='store_true',
                        help='同 --setup，运行交互式设置向导')
    parser.add_argument('--update', '--upgrade', action='store_true',
                        help='检查 GitHub 仓库是否有新版本并更新')
    parser.add_argument('--version', action='version',
                        version=f'md2docx_pdf v{VERSION}')

    args = parser.parse_args()

    print(f"\n  md2docx_pdf v{VERSION}  {REPO_URL}")
    print(f"  平台: {plat()}")

    # ── Update check ───────────────────────────────────────
    if getattr(args, 'update', False):
        check_update()
        sys.exit(0)

    # ── Setup wizard ──────────────────────────────────────
    if args.setup or args.install:
        setup_wizard()
        # setup_wizard may return (if auto_scan) or sys.exit(0)
        # If it returned with auto_scan, continue to scan below
        cfg = load_setup_config()
        if not cfg.get('auto_scan'):
            sys.exit(0)
        # auto_scan: force scan mode with current directory
        print("  自动进入扫描模式...")
        args.scan = '.'  # Trigger scan mode below

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

    latex = has_latex()
    if latex:
        print(f"  LaTeX: {Path(latex).name}")
    else:
        print(f"  LaTeX: 未安装 (可选，.tex 编译需要)")

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
                  '.pdf': 'PDF', '.tex': 'LaTeX', '.drawio': 'DrawIO', '.dio': 'DrawIO'}
        for ext in ['.md', '.docx', '.doc', '.pdf', '.tex', '.drawio', '.dio']:
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
        for ext in ['.md', '.docx', '.doc', '.pdf', '.tex']:
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
                if p.suffix.lower() in ('.md', '.docx', '.doc', '.pdf', '.tex'):
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
