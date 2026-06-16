#!/usr/bin/env python3
"""
将 DocWizard SKILL.md 转换为 Cursor .cursor/rules/docwizard.mdc 格式。

Cursor 使用 .mdc 文件（YAML frontmatter + Markdown 正文），而非 SKILL.md。
此脚本自动完成格式转换。

用法:
  python3 docs/convert_to_mdc.py                          # 在当前目录生成
  python3 docs/convert_to_mdc.py --output ./docwizard.mdc  # 指定输出路径
  python3 docs/convert_to_mdc.py --source ./SKILL.md       # 指定源文件

生成的 .mdc 文件可以直接放入 .cursor/rules/ 目录使用。
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path


MDC_FRONTMATTER = """---
description: "DocWizard — AI-powered one-stop homework assistant. Format conversion, data analysis, PPT generation, archive extraction, Chinese academic formatting."
globs:
  - "*.md"
  - "*.docx"
  - "*.pdf"
  - "*.csv"
  - "*.xlsx"
  - "*.pptx"
  - "*.tex"
  - "*.typ"
  - "*.zip"
  - "*.rar"
  - "*.7z"
alwaysApply: false
---
"""

CURSOR_NOTE = """
> ⚠️ **Cursor 环境说明**
>
> 此文件由 `docs/convert_to_mdc.py` 从 `SKILL.md` 自动生成。
> 生成时间: {timestamp}
>
> Cursor 没有 `document-skills@anthropic-agent-skills` 插件。格式转换降级为 Python 库：
> ```bash
> pip install python-docx python-pptx openpyxl pdfplumber pandas
> ```
>
> 详见 [非 Claude Code / OpenCode 环境](README.md#非-claude-code--opencode-环境)。
"""


def convert_skill_to_mdc(source_path: Path, output_path: Path) -> str:
    """将 SKILL.md 转换为 .mdc 格式。"""

    if not source_path.exists():
        print(f"Error: source file not found: {source_path}")
        sys.exit(1)

    content = source_path.read_text(encoding='utf-8')

    # 移除 Claude Code 特有的 /plugin install 指令行，替换为降级说明
    lines = content.split('\n')
    converted_lines = []

    for line in lines:
        # 替换 /plugin install 命令
        if '/plugin install' in line:
            converted_lines.append(
                line.replace('/plugin install', '# Cursor: 无此命令，请用 pip install')
            )
        # 替换 .claude/skills/ 路径引用
        elif '.claude/skills/' in line and 'OpenCode' not in line:
            converted_lines.append(
                re.sub(r'\.claude/skills/', '.cursor/rules/', line)
            )
        # 替换 document-skills 委托为 Python 库调用
        elif '委托 docx skill' in line:
            converted_lines.append(line.replace('委托 docx skill', '使用 python-docx'))
        elif '委托 pdf skill' in line:
            converted_lines.append(line.replace('委托 pdf skill', '使用 pdfplumber/pymupdf'))
        elif '委托 pptx skill' in line:
            converted_lines.append(line.replace('委托 pptx skill', '使用 python-pptx'))
        elif '委托 xlsx skill' in line:
            converted_lines.append(line.replace('委托 xlsx skill', '使用 openpyxl/pandas'))
        elif '使用 docx skill' in line:
            converted_lines.append(line.replace('使用 docx skill', '使用 python-docx'))
        elif '使用 pdf skill' in line or 'pdf skill 导出' in line:
            converted_lines.append(line.replace('使用 pdf skill', '使用 pdfplumber')
                                    .replace('pdf skill 导出', 'pdfplumber 导出'))
        elif '使用 pptx skill' in line:
            converted_lines.append(line.replace('使用 pptx skill', '使用 python-pptx'))
        elif '使用 xlsx skill' in line:
            converted_lines.append(line.replace('使用 xlsx skill', '使用 openpyxl/pandas'))
        else:
            converted_lines.append(line)

    body = '\n'.join(converted_lines)

    # 添加 Cursor 环境说明（在第一个 ## 标题之后）
    cursor_note = CURSOR_NOTE.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    first_h2 = body.find('\n## ')
    if first_h2 > 0:
        body = body[:first_h2 + 1] + cursor_note + '\n' + body[first_h2 + 1:]

    # 组合最终内容
    output = MDC_FRONTMATTER + '\n' + body

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding='utf-8')

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description='将 DocWizard SKILL.md 转换为 Cursor .mdc 格式'
    )
    parser.add_argument(
        '--source', '-s',
        default='SKILL.md',
        help='源 SKILL.md 文件路径（默认: ./SKILL.md）'
    )
    parser.add_argument(
        '--output', '-o',
        default='.cursor/rules/docwizard.mdc',
        help='输出 .mdc 文件路径（默认: ./.cursor/rules/docwizard.mdc）'
    )
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output)

    # 如果是相对路径，相对于当前目录
    if not output.is_absolute():
        output = Path.cwd() / output

    result = convert_skill_to_mdc(source, output)
    print(f"✅ 转换完成: {source.name} → {result}")
    print(f"   将 {result} 放入项目的 .cursor/rules/ 目录即可在 Cursor 中使用 DocWizard。")


if __name__ == '__main__':
    main()