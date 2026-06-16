#!/usr/bin/env python3
"""
DocWizard 一键安装脚本
======================
自动检测平台 → 提示安装 document-skills 插件 → clone DocWizard → 验证环境
跨平台：Windows / macOS / Linux

用法:
  python3 setup.py          # 交互式安装
  python3 setup.py --yes    # 跳过确认，自动安装
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/cowhorse05/DocWizard.git"
SKILLS_DIR = Path.home() / ".claude" / "skills" / "DocWizard"
PLUGIN_CMD = "/plugin install document-skills@anthropic-agent-skills"


def detect_platform():
    system = platform.system()
    return {
        "Windows": "Windows",
        "Darwin": "macOS",
        "Linux": "Linux",
    }.get(system, system)


def run(cmd, **kwargs):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kwargs)


def heading(text):
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def step(n, total, text):
    print(f"  [{n}/{total}] {text}")


def check_mark(ok):
    return "✓" if ok else "✗"


def main():
    auto_yes = "--yes" in sys.argv or "-y" in sys.argv
    plat = detect_platform()
    total_steps = 5

    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "  DocWizard v3.0.0 — 一键安装向导".center(52) + "║")
    print("║" + f"  平台: {plat}".ljust(52) + "║")
    print("╚" + "═" * 58 + "╝")

    # ── Step 1: Python ──────────────────────────────────────────
    heading("Step 1: Python 环境")
    py_ver = sys.version.split()[0]
    py_ok = sys.version_info >= (3, 7)
    step(1, total_steps, f"Python {py_ver}")
    print(f"  {check_mark(py_ok)} Python {py_ver}")
    if not py_ok:
        print("  ✗ 需要 Python 3.7+, 请先升级 Python")
        sys.exit(1)

    # ── Step 2: Git ─────────────────────────────────────────────
    heading("Step 2: Git")
    git_ok = shutil.which("git") is not None
    step(2, total_steps, "Git")
    if git_ok:
        ver = run("git --version").stdout.strip()
        print(f"  ✓ {ver}")
    else:
        print("  ✗ Git 未安装")
        if plat == "Windows":
            print("  安装: winget install Git.Git")
        elif plat == "macOS":
            print("  安装: brew install git")
        else:
            print("  安装: sudo apt install git")
        print("  请先安装 Git 后重试。")
        sys.exit(1)

    # ── Step 3: document-skills 插件 ────────────────────────────
    heading("Step 3: document-skills 插件")
    step(3, total_steps, "document-skills@anthropic-agent-skills")
    print(f"  此插件包含: docx, pdf, pptx, xlsx 四个 Skill")
    print()
    print(f"  请在 Claude Code 中运行以下命令来安装:")
    print(f"    {PLUGIN_CMD}")
    print()
    print("  (此步骤需要在 Claude Code 内部执行，无法通过脚本自动完成)")

    if not auto_yes:
        input("  按 Enter 继续...")

    # ── Step 4: Clone DocWizard ─────────────────────────────────
    heading("Step 4: Clone DocWizard")
    step(4, total_steps, f"Clone → {SKILLS_DIR}")

    if SKILLS_DIR.exists():
        print(f"  ✓ 目录已存在: {SKILLS_DIR}")
        print("  正在 git pull 更新...")
        result = run(f"git -C {SKILLS_DIR} pull origin main")
        if result.returncode == 0:
            print("  ✓ 已更新到最新版本")
        else:
            print(f"  ⚠ 更新失败: {result.stderr.strip()}")
    else:
        SKILLS_DIR.parent.mkdir(parents=True, exist_ok=True)
        print(f"  正在 clone {REPO_URL} ...")
        result = run(f"git clone {REPO_URL} {SKILLS_DIR}")
        if result.returncode == 0:
            print(f"  ✓ Clone 完成 → {SKILLS_DIR}")
        else:
            print(f"  ✗ Clone 失败: {result.stderr.strip()}")
            print(f"  请手动执行: git clone {REPO_URL} {SKILLS_DIR}")
            sys.exit(1)

    # ── Step 5: 验证 ────────────────────────────────────────────
    heading("Step 5: 验证安装")
    step(5, total_steps, "验证")

    checks = []
    # Check SKILL.md
    skill_md = SKILLS_DIR / "SKILL.md"
    checks.append(("SKILL.md", skill_md.exists()))
    # Check helpers
    mermaid_py = SKILLS_DIR / "helpers" / "render_mermaid.py"
    checks.append(("helpers/render_mermaid.py", mermaid_py.exists()))
    black_py = SKILLS_DIR / "helpers" / "black_text.py"
    checks.append(("helpers/black_text.py", black_py.exists()))
    # Check task.md
    task_md = SKILLS_DIR / "task.md"
    checks.append(("task.md", task_md.exists()))

    all_ok = True
    for name, ok in checks:
        print(f"  {check_mark(ok)} {name}")
        if not ok:
            all_ok = False

    if not all_ok:
        print("\n  ⚠ 部分文件缺失，请重新 clone 仓库。")
        sys.exit(1)

    # ── 完成 ────────────────────────────────────────────────────
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "  安装完成！".center(52) + "║")
    print("║" + "".center(52) + "║")
    print("║" + "  在 Claude Code 中执行:".center(48) + "║")
    print("║" + f"  {PLUGIN_CMD}".center(52) + "║")
    print("║" + "  然后说「执行 task.md」即可开始使用".center(46) + "║")
    print("╚" + "═" + 58 + "╝")
    print()


if __name__ == "__main__":
    main()