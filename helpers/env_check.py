#!/usr/bin/env python3
"""
DocWizard 环境检测器 — 检测 harness、平台、能力可用性，输出报告。
纯 Python stdlib，零依赖。

用法:
  python3 helpers/env_check.py          # 输出完整检测报告
  python3 helpers/env_check.py --json   # JSON 格式输出（供程序消费）
  python3 helpers/env_check.py --quiet  # 仅输出摘要
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def detect_platform():
    """检测操作系统平台。"""
    system = platform.system()
    mapping = {
        'Windows': 'Windows',
        'Darwin': 'macOS',
        'Linux': 'Linux',
    }
    return mapping.get(system, system)


def detect_python():
    """检测 Python 命令和版本。"""
    py_info = {
        'available': False,
        'command': None,
        'version': 'unknown',
    }
    for cmd in ['python3', 'python']:
        if shutil.which(cmd):
            try:
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
                ver = result.stdout.strip() or result.stderr.strip()
                py_info['available'] = True
                py_info['command'] = cmd
                py_info['version'] = ver
                break
            except Exception:
                continue
    return py_info


def detect_git():
    """检测 Git 是否可用。"""
    git_info = {'available': False, 'version': 'unknown'}
    if shutil.which('git'):
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=5)
            git_info['available'] = True
            git_info['version'] = result.stdout.strip()
        except Exception:
            pass
    return git_info


def detect_harness():
    """检测 AI 编程工具 harness。"""
    harness = {
        'detected': 'unknown',
        'name': 'Unknown',
        'skills_path': '.agents/skills/DocWizard/',
        'document_skills': False,
        'note': None,
    }

    cwd = Path.cwd()
    if (cwd / '.claude').exists() or os.environ.get('CLAUDE_CODE'):
        harness['detected'] = 'claude_code'
        harness['name'] = 'Claude Code'
        harness['skills_path'] = '.claude/skills/DocWizard/'
        harness['document_skills'] = True
    elif (cwd / '.opencode').exists() or os.environ.get('OPENCODE'):
        harness['detected'] = 'opencode'
        harness['name'] = 'OpenCode'
        harness['skills_path'] = '.claude/skills/DocWizard/ 或 .opencode/skills/DocWizard/'
        harness['document_skills'] = True
    elif (cwd / '.codex').exists() or (cwd / '.agents').exists() or os.environ.get('CODEX_CLI'):
        harness['detected'] = 'codex'
        harness['name'] = 'Codex (OpenAI)'
        harness['skills_path'] = '.codex/skills/DocWizard/ 或 .agents/skills/DocWizard/'
        harness['document_skills'] = False
    elif (cwd / '.cursor').exists():
        harness['detected'] = 'cursor'
        harness['name'] = 'Cursor'
        harness['skills_path'] = '.cursor/rules/docwizard.mdc'
        harness['document_skills'] = False
        harness['note'] = '需运行 python docs/convert_to_mdc.py 将 SKILL.md 转换为 .mdc 格式'

    return harness


def detect_document_skills():
    """检测 document-skills 插件是否可用。"""
    ds_info = {'available': False, 'method': 'unknown'}

    # 检查是否在 Claude Code / OpenCode 环境中
    cwd = Path.cwd()
    if (cwd / '.claude').exists() or (cwd / '.opencode').exists():
        ds_info['available'] = True
        ds_info['method'] = 'Claude Code / OpenCode 原生支持'
    elif (cwd / '.codex').exists() or (cwd / '.agents').exists() or (cwd / '.cursor').exists():
        ds_info['available'] = False
        ds_info['method'] = '降级为 Python 库（python-docx, python-pptx, openpyxl, pdfplumber, pandas）'
        ds_info['fallback'] = 'pip install python-docx python-pptx openpyxl pdfplumber pandas'

    return ds_info


def detect_latex():
    """检测 LaTeX 编译器。"""
    latex_info = {'available': False, 'compiler': None}
    for compiler in ['tectonic', 'xelatex', 'pdflatex']:
        if shutil.which(compiler):
            latex_info['available'] = True
            latex_info['compiler'] = compiler
            break
    return latex_info


def detect_typst():
    """检测 Typst 编译器。"""
    typst_info = {'available': False, 'version': 'unknown'}
    if shutil.which('typst'):
        try:
            result = subprocess.run(['typst', '--version'], capture_output=True, text=True, timeout=5)
            typst_info['available'] = True
            typst_info['version'] = result.stdout.strip().split('\n')[0]
        except Exception:
            pass
    return typst_info


def detect_mermaid_ink():
    """检测 mermaid.ink 服务可用性。"""
    import urllib.request

    mi_info = {'available': False, 'method': 'mermaid.ink (在线)'}
    try:
        test_url = ('https://mermaid.ink/img/'
                    'eyJjb2RlIjoiZ3JhcGggVERcbiAgICBBW0hlbGxvXSAtLT4gQntXb3JsZH0ifQ==')
        req = urllib.request.Request(test_url, headers={'User-Agent': 'DocWizard/3.1'})
        resp = urllib.request.urlopen(req, timeout=10)
        if resp.status == 200 and len(resp.read()) > 100:
            mi_info['available'] = True
    except Exception:
        pass

    # 检测本地 mermaid-cli 备选
    if shutil.which('mmdc'):
        mi_info['local_fallback'] = 'mermaid-cli (mmdc) 可用'
    else:
        mi_info['local_fallback'] = '未安装 mermaid-cli（npm install -g @mermaid-js/mermaid-cli）'

    return mi_info


def detect_ocr():
    """检测 OCR 工具可用性。"""
    ocr_info = {
        'tesseract': {'available': False},
        'mineru_skill': {'available': False, 'note': 'Claude Code Skill (npx skills add Nebutra/MinerU-Skill)，非 Python 包，运行时检测'},
        'chandra_ocr': {'available': False},
        'surya_ocr': {'available': False},
        'marker_pdf': {'available': False},
    }

    if shutil.which('tesseract'):
        try:
            result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True, timeout=5)
            ocr_info['tesseract']['available'] = True
            ocr_info['tesseract']['version'] = result.stdout.strip().split('\n')[0]
        except Exception:
            pass

    # 检测 Python OCR 包
    for pkg, key in [('chandra_ocr', 'chandra_ocr'), ('surya_ocr', 'surya_ocr'),
                      ('marker_pdf', 'marker_pdf')]:
        try:
            result = subprocess.run(
                [sys.executable, '-c', f'import {pkg}; print(getattr({pkg}, "__version__", "installed"))'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                ocr_info[key]['available'] = True
                ocr_info[key]['version'] = result.stdout.strip()
        except Exception:
            pass

    return ocr_info


def detect_archive_tools():
    """检测压缩工具。"""
    archive = {'zip': 'Python stdlib (始终可用)', 'rar': None, 'seven_z': None}

    for cmd in ['unrar', '7z', '7z.exe']:
        if shutil.which(cmd):
            archive['rar'] = cmd
            break
    for cmd in ['7z', '7z.exe', '7za', '7za.exe']:
        if shutil.which(cmd):
            archive['seven_z'] = cmd
            break

    return archive


def run_full_check():
    """运行完整环境检测，返回字典。"""
    return {
        'docwizard_version': '3.1.0',
        'platform': detect_platform(),
        'python': detect_python(),
        'git': detect_git(),
        'harness': detect_harness(),
        'document_skills': detect_document_skills(),
        'latex': detect_latex(),
        'typst': detect_typst(),
        'mermaid_ink': detect_mermaid_ink(),
        'ocr': detect_ocr(),
        'archive_tools': detect_archive_tools(),
    }


def print_report(report, quiet=False):
    """打印可读的检测报告。"""
    if quiet:
        harness = report['harness']
        ds = report['document_skills']
        mi = report['mermaid_ink']
        ocr = report['ocr']
        available_ocr = [k for k, v in ocr.items() if v.get('available')]
        print(f"Harness: {harness['name']} | "
              f"document-skills: {'✅' if ds['available'] else '❌'} | "
              f"Mermaid: {'✅' if mi['available'] else '❌'} | "
              f"OCR: {', '.join(available_ocr) if available_ocr else 'tesseract' if ocr['tesseract']['available'] else 'none'} | "
              f"LaTeX: {'✅' if report['latex']['available'] else '❌'} | "
              f"Typst: {'✅' if report['typst']['available'] else '❌'}")
        return

    h = report['harness']
    py = report['python']
    ds = report['document_skills']
    mi = report['mermaid_ink']
    ocr = report['ocr']
    latex = report['latex']
    typst = report['typst']
    archive = report['archive_tools']

    print("=" * 55)
    print("  DocWizard 环境检测报告")
    print("=" * 55)
    print(f"  平台:       {report['platform']}")
    print(f"  Python:     {'✅ ' + py['version'] if py['available'] else '❌ 未安装'}")
    print(f"  Git:        {'✅' if report['git']['available'] else '❌ 未安装'}")
    print()
    print(f"  Harness:    {h['name']}")
    print(f"  Skills 路径: {h['skills_path']}")
    print(f"  document-skills: {'✅ 可用' if ds['available'] else '❌ 不可用 → ' + ds.get('fallback', ds['method'])}")
    print()
    print(f"  Mermaid:    {'✅ mermaid.ink 可用' if mi['available'] else '❌ mermaid.ink 不可达'}")
    print(f"  本地备选:    {mi['local_fallback']}")
    print()
    print(f"  LaTeX:      {'✅ ' + latex['compiler'] if latex['available'] else '❌ 未安装（推荐: tectonic）'}")
    print(f"  Typst:      {'✅ ' + typst['version'] if typst['available'] else '❌ 未安装'}")
    print()
    print("  OCR 工具:")
    for tool, info in ocr.items():
        label = {'tesseract': 'Tesseract', 'mineru_skill': 'MinerU Skill',
                 'chandra_ocr': 'Chandra OCR', 'surya_ocr': 'Surya OCR',
                 'marker_pdf': 'marker-pdf'}[tool]
        ver = f" ({info.get('version', '')})" if info.get('version') else ""
        print(f"    {tool:15s} {'✅' if info.get('available') else '❌'} {label}{ver}")
    print()
    print(f"  压缩工具:    ZIP: {archive['zip']}")
    if archive['rar']:
        print(f"              RAR: {archive['rar']}")
    if archive['seven_z']:
        print(f"              7z:  {archive['seven_z']}")
    print("=" * 55)


def main():
    parser = argparse.ArgumentParser(description='DocWizard 环境检测器')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    parser.add_argument('--quiet', '-q', action='store_true', help='仅输出摘要')
    args = parser.parse_args()

    report = run_full_check()

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report, quiet=args.quiet)


if __name__ == '__main__':
    main()