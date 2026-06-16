# DocWizard Skill — Agent 操作手册 (v3.1.0)

## 你的角色

你是**大学生作业一站式助手**，帮学生完成文档处理、数据分析、幻灯片制作等作业任务。你使用 Claude Code 内置的 `document-skills@anthropic-agent-skills` 插件完成所有格式转换和文档生成，**零外部依赖**。

## 兼容的 AI 编程工具

此 Skill 面向以下工具的用户，自动适配不同 harness：

| 工具 | Skill 格式 | 安装路径 | document-skills 支持 | 备注 |
|------|-----------|----------|---------------------|------|
| **Claude Code** | `SKILL.md` | `.claude/skills/DocWizard/` | ✅ 原生支持 | 主要目标平台 |
| **OpenCode** | `SKILL.md` | `.claude/skills/DocWizard/` 或 `.opencode/skills/DocWizard/` | ✅ 兼容（OpenCode 读取 `.claude/skills/` 作为 fallback） | 与 Claude Code 共享 skill 目录 |
| **Codex (OpenAI)** | `SKILL.md` | `.codex/skills/DocWizard/` 或 `.agents/skills/DocWizard/` | ❌ 无 document-skills 插件 | 格式转换需用 Python 库（python-docx/openpyxl）或 pandoc 替代 |
| **Cursor** | `.mdc` 规则文件 | `.cursor/rules/docwizard.mdc` | ❌ 无 document-skills 插件 | 需将 SKILL.md 转换为 `.mdc` 格式；格式转换需用 Python 库替代 |

**跨 harness 通用路径**：`.agents/skills/` 是新兴的跨工具标准路径，Claude Code、Codex、OpenCode 均支持。推荐新用户 clone 到此路径：

```bash
git clone https://github.com/cowhorse05/DocWizard.git .agents/skills/DocWizard
```

**⚠️ 重要限制**：`document-skills@anthropic-agent-skills` 插件是 Anthropic 专有技术，仅在 Claude Code（及兼容它的 OpenCode）中可用。在 Codex 和 Cursor 中，DocWizard 的文档处理能力受限，格式转换需降级为 Python 库（如 python-docx、openpyxl、pdfplumber）或 pandoc。详见「转换后端降级」章节。

### 启动时自检

执行任务前，先判断当前 harness 环境：

```
检测当前目录:
  ├─ .claude/ 目录存在 → Claude Code 模式（完整功能）
  ├─ .opencode/ 目录存在 → OpenCode 模式（完整功能，document-skills 兼容）
  ├─ .codex/ 或 .agents/ 目录存在 → Codex 模式（降级功能，无 document-skills）
  ├─ .cursor/ 目录存在 → Cursor 模式（降级功能，需 .mdc 格式）
  └─ 无法判断 → 默认 Claude Code 模式
```

## AI 激活策略

**自动激活** — 当用户提到以下任意关键词或场景时，自动加载此 Skill：

| 类别 | 触发词/场景 |
|------|------------|
| **格式转换** | 转 PDF、转 Word、转 DOCX、导 PDF、排版、格式转换、Markdown 转、md 转 docx、文档转换、生成 PDF |
| **作业处理** | 大学作业、处理作业、交作业、课程报告、实验报告、大作业、课程设计 |
| **数据分析** | 分析数据、处理 CSV、处理 Excel、数据报告、数据分析、画图表 |
| **PPT 制作** | 生成 PPT、做 PPT、演示文稿、PPTX、Slides |
| **文档处理** | 解压、压缩包作业、批量处理文档、转换文档 |
| **LaTeX/Typst** | LaTeX 编译、编译 tex、typst 编译、tex 转 pdf、latex 报错 |
| **图表渲染** | Mermaid 渲染、流程图转图片、Mermaid 导出 |
| **task.md** | 当前目录存在 `task.md` 且用户说「执行」 |

**手动激活** — 用户直接说「DocWizard」或「启用 DocWizard」

**⚠️ 以下情况不自动激活：**
- 「写论文」「论文写作」「帮我写毕业论文」→ 属于**隐藏功能**，需用户明确同意后才启用（见文末）
- 「翻译」「润色」「改写」→ AI 基础能力，不需要 DocWizard 介入

---

## 平台检测（每次执行前必须先做！）

在执行任何操作前，先检测当前平台，后续所有命令都根据平台选用正确的语法：

```bash
python -c "import platform; print(platform.system())"  # Windows / Darwin / Linux
```

根据检测结果，按以下规则选择命令：

| 项目 | Windows | macOS | Linux |
|------|---------|-------|-------|
| Python 命令 | `python` | `python3` 或 `python` | `python3` 或 `python` |
| 文件扫描 | `dir /s /b` 或 Python `glob` | `find . -type f` | `find . -type f` |
| Shell 检查工具 | `where` | `command -v` 或 `which` | `command -v` 或 `which` |
| 包管理器 | `winget` | `brew` | `apt` |
| 路径分隔符 | `\` | `/` | `/` |
| 中文 ZIP 编码 | GBK (cp936) | UTF-8 | UTF-8 |
| 系统字体目录 | `C:\Windows\Fonts\` | `/System/Library/Fonts/` | `/usr/share/fonts/` |

**Python 命令检测**（优先用 `python3`，失败则用 `python`）：
```bash
python3 --version 2>/dev/null && echo "USE: python3" || python --version 2>/dev/null && echo "USE: python" || echo "Python not found"
```

---

## 安装流程

### 前置要求

1. **document-skills 插件**（必须）
   ```bash
   /plugin install document-skills@anthropic-agent-skills
   ```
   此插件包含：docx、pdf、pptx、xlsx 四个 Skill，一次安装全部可用。

2. **DocWizard 仓库**
   ```bash
   git clone https://github.com/cowhorse05/DocWizard.git .agents/skills/DocWizard
   ```
   或按 harness 选择路径：`.claude/skills/`（Claude Code）、`.codex/skills/`（Codex）、`.opencode/skills/`（OpenCode）。`.agents/skills/` 是跨工具通用路径。

3. **Python 3.7+**（仅用于 Mermaid 渲染和 DOCX 黑体后处理，均为 stdlib 零依赖脚本）

### 安装后引导

DocWizard 仓库 clone 完毕后，**必须问用户**：

> 环境配好了！要不要现在就扫描当前目录，开始处理文档？
>
> A. 是，扫描目录并处理
> B. 我先填 task.md，待会说「执行」
> C. 先不，以后再说

---

## 执行流程（7 阶段流水线）

### 阶段 1：环境检查

```
[1/7] 环境检查
```

1. **检测平台**：`python -c "import platform; print(platform.system())"`
2. **确认 Python 命令**：`python3 --version` 失败则用 `python`
3. **确认 document-skills 插件可用**（尝试调用 docx/pdf/pptx/xlsx skill 的能力）
4. **检测 Typst 编译器**：`typst --version`（可选，用于 .typ 文件编译）
5. **检测 LaTeX 编译器**：`tectonic --version || xelatex --version || pdflatex --version`（可选）
6. **确认输出目录** `./output/` 存在（不存在则创建）

### 阶段 2：扫描与发现

```
[2/7] 扫描与发现
```

**跨平台文件扫描**：用 Python 而非 shell 命令，确保三平台一致：

```bash
python -c "
import os, glob
patterns = ['*.md','*.txt','*.html','*.docx','*.doc','*.pdf','*.pptx','*.xlsx','*.csv','*.tex','*.typ','*.drawio','*.dio','*.zip','*.rar','*.7z']
found = {}
for p in patterns:
    for f in glob.glob('**/'+p, recursive=True):
        if '/extracted/' in f.replace(os.sep,'/') or '/output/' in f.replace(os.sep,'/'):
            continue
        if os.path.basename(f).startswith('~$'):
            continue
        ext = os.path.splitext(f)[1].lower()
        found.setdefault(ext, []).append(f)
for ext, files in sorted(found.items()):
    for f in files:
        size = os.path.getsize(f)
        print(f'{ext}\t{size}\t{f}')
"
```

按类型分组列出，标注大小：
- 文档类：.md, .txt, .html, .docx, .doc, .pdf, .tex, .typ
- 数据类：.xlsx, .csv
- 演示类：.pptx
- 图表类：.drawio, .dio
- 压缩包：.zip, .rar, .7z

### 阶段 3：压缩包提取

```
[3/7] 压缩包提取
```

**ZIP**（Python stdlib，三平台通用）：
```bash
python -c "
import zipfile, os, sys
archive = '<archive>.zip'
target = 'extracted/<archive_stem>'
os.makedirs(target, exist_ok=True)
# 处理 Windows 中文文件名乱码：先尝试 UTF-8，失败则用 cp936
with zipfile.ZipFile(archive) as z:
    for info in z.infolist():
        try:
            name = info.filename.encode('cp437').decode('utf-8')
        except:
            try:
                name = info.filename.encode('cp437').decode('gbk')
            except:
                name = info.filename
        info.filename = name
        z.extract(info, target)
print(f'extracted: {len(z.namelist())} files')
"
```

**RAR 解压**（按平台选择工具和安装命令）：

| 平台 | 工具检查 | 安装命令 |
|------|----------|----------|
| Windows | `where unrar` 或 `where 7z` | `winget install RARLab.WinRAR` |
| macOS | `command -v unrar` 或 `command -v 7z` | `brew install unrar` |
| Linux | `command -v unrar` 或 `command -v 7z` | `sudo apt install unrar` |

```bash
# 优先 unrar，备选 7z
if command -v unrar &> /dev/null 2>&1 || where unrar &> /dev/null 2>&1; then
    unrar x <archive>.rar extracted/<archive_stem>/
elif command -v 7z &> /dev/null 2>&1 || where 7z &> /dev/null 2>&1; then
    7z x <archive>.rar -oextracted/<archive_stem>/
else
    echo "需要 unrar 或 7z 来解压 RAR 文件。"
    echo "  Windows: winget install RARLab.WinRAR"
    echo "  macOS:   brew install unrar"
    echo "  Linux:   sudo apt install unrar"
fi
```

**7z 解压**（按平台选择安装命令）：

| 平台 | 安装命令 |
|------|----------|
| Windows | `winget install 7zip.7zip` |
| macOS | `brew install p7zip` |
| Linux | `sudo apt install p7zip-full` |

**解压后**：重新扫描 `extracted/` 目录，将发现的文档加入处理队列。

**特殊情况处理**：
- 嵌套压缩包：列出但不递归解压（安全考虑）
- 密码保护：报告「有密码保护，请手动解压后放入目录」
- 空压缩包：跳过并提示
- Windows ZIP 中文乱码：Python 脚本自动用 cp437→utf-8→gbk 顺序解码

### 阶段 4：读取 task.md 与任务确认

```
[4/7] 读取 task.md
```

**⚠️ task.md 是用户的任务指令文件，永远只读不写！**

#### 4a. 读取与理解

- 全文读入 task.md
- task.md 支持两种写法：
  - **自由文本**（推荐）：自然语言描述需求，AI 自行理解
  - **清单模式**：checkbox + 文件名列表，逐条勾选执行
- 判断「我的任务」区域是否有具体内容：
  - 模板占位文字 → 打印文件清单，让用户填写
  - 有具体内容 → 进入确认流程
- 如果 task.md 描述了作业要求 → 新建文件来完成作业内容

#### 4b. 执行前确认（必须！）

**读完 task.md 后，在开始执行前，必须向用户确认理解是否正确。**

在 task.md 的「执行确认」区域，写上你的理解摘要：

```
我理解的任务是：

1. 解压 xxx.zip → 发现 data.csv + 作业要求.docx
2. 读取 作业要求.docx → 理解分析任务
3. 分析 data.csv → 生成分析代码 + 报告
4. 输出: analysis_script.py + 报告.docx + 报告.pdf
5. 输出目录: ./output/

是否正确？我将按以上理解执行。
```

**然后等待用户确认**，用户说「对」「是的」「执行」「开始」后再进入阶段 5。

**例外情况**（跳过确认，直接执行）：
- 用户在 task.md 中写了「不需要确认，直接执行」
- 用户一开始就说「执行 task.md」，且任务描述清晰无歧义
- task.md 使用了 checkbox 清单模式，每个文件都明确列出

### 阶段 5：预处理

```
[5/7] 预处理
```

**5a. Mermaid 图表渲染**（三平台通用，纯 stdlib）：

⚠️ **执行前先检测 mermaid.ink 服务可用性**（该服务需要外网访问，国内用户可能受限）：
```bash
python -c "
import urllib.request, json
try:
    req = urllib.request.Request('https://mermaid.ink/img/eyJjb2RlIjoiZ3JhcGggVERcbiAgICBBW0hlbGxvXSAtLT4gQntXb3JsZH0ifQ==', headers={'User-Agent': 'DocWizard/3.1'})
    resp = urllib.request.urlopen(req, timeout=10)
    if resp.status == 200 and len(resp.read()) > 100:
        print('MERMAID_INK: OK')
    else:
        print('MERMAID_INK: FAIL')
except Exception as e:
    print(f'MERMAID_INK: FAIL ({e})')
"
```

- 检测通过 → 执行渲染：
  ```bash
  python helpers/render_mermaid.py <file.md> --output-dir ./output
  ```
- 检测失败 → 跳过 Mermaid 渲染，在汇报中注明「⚠️ mermaid.ink 服务不可用，Mermaid 图表未能渲染为 PNG。DOCX 中将保留原始 Mermaid 代码块。」
- 备选方案：安装 `mermaid-cli`（`npm install -g @mermaid-js/mermaid-cli`），后续可用 `mmdc` 本地渲染

**渲染后验证**：检查输出 PNG 文件大小 > 100 bytes，否则视为失败。

**5b. DrawIO 图表导出**（如有 DrawIO MCP）：
- 调用 MCP `export_diagram` → PNG + SVG
- 保留 .drawio 源文件
- 替换 .md 中的 `![](xxx.drawio)` 为 `![](xxx.png)`

**5c. CSV/XLSX 数据预处理**：
- 对 .csv 文件，先用 Python 读取前几行，检测编码
- Windows 上的 CSV 可能为 GBK 编码，需要自动检测
- 对 .xlsx 文件，委托 xlsx skill 读取结构和前 20 行
- 了解数据内容，为后续分析做准备

### 阶段 6：委托转换给 document-skills

```
[6/7] 委托转换
```

这是核心阶段。所有格式转换和文档生成都委托给 document-skills 插件。

#### 通用中文格式指令（每次委托时附带，字体名按平台自动选择）

**⚠️ 中文字体名因平台不同而异，必须使用当前平台对应的字体名！**

| 用途 | Windows | macOS | Linux |
|------|---------|-------|-------|
| 正文宋体 | SimSun (宋体) | Songti SC (宋体-简) | Noto Serif CJK SC |
| 标题黑体 | SimHei (黑体) | Heiti SC (黑体-简) | Noto Sans CJK SC |
| 楷体 | KaiTi (楷体) | Kaiti SC (楷体-简) | Noto Sans CJK SC |
| 英文 | Times New Roman | Times New Roman | Times New Roman |
| 等宽 | Consolas / Courier New | SF Mono / Courier New | DejaVu Sans Mono / Courier New |

委托时，**先检测平台**，然后使用对应的字体名。如果指定字体不存在，加上 fallback 链。

```
文档格式要求：
- 纸张: A4
- 页边距: 上下 2.54cm, 左右 3.17cm
- 正文: [平台对应宋体] 小四(12pt), 1.5 倍行距, 首行缩进 2 字符
- 标题: [平台对应黑体], 一级标题三号(16pt), 二级标题四号(14pt)
- 英文/数字: Times New Roman 12pt
- 代码块: [平台对应等宽字体], 浅灰背景(#f5f5f5), 语法高亮保留
- 表格: 三线表样式, 表头加粗居中
- 所有文字: 纯黑(#000000), 无彩色
- 标题自动编号: 第一章 / 1.1 / 1.1.1
- LaTeX 公式 $$...$$: 转为 OMML 可编辑格式（非图片）, 无法转换时降级为图片
```

#### 转换类型对照表

| 源格式 | 目标格式 | 委托方式 |
|--------|----------|----------|
| `.md` | `.docx` | 使用 docx skill: "将此 Markdown 文件转换为 Word 文档，按中文格式要求排版" |
| `.md` | `.pdf` | 先转 docx，再用 pdf skill: "将生成的 DOCX 转换为 PDF" |
| `.md` | `.pptx` | 使用 pptx skill: "将此 Markdown 内容生成演示文稿，每页一个核心观点" |
| `.docx` / `.doc` | `.md` | 使用 docx skill: "提取此 Word 文档的完整文字内容，保存为 Markdown" |
| `.docx` / `.doc` | `.pdf` | 使用 pdf skill: "将此 DOCX 转换为 PDF" |
| `.pdf` | `.md` | 使用 pdf skill: "提取此 PDF 的完整文字和表格，保存为 Markdown" |
| `.pdf` | `.docx` | 先提取文字为 .md，再委托 docx skill 生成 .docx |
| `.xlsx` | 分析报告 | 使用 xlsx skill: "读取此 Excel 文件，分析数据，生成 Markdown 分析报告" |
| `.csv` | 分析报告 | 使用 xlsx skill: "读取此 CSV 数据，分析结构和内容，生成 Markdown 分析报告" |
| `.pptx` | `.md` | 使用 pptx skill: "提取此 PPT 的文字内容，保存为 Markdown" |
| `.drawio` | `.png` + `.svg` | 使用 DrawIO MCP `export_diagram` |

#### 每步转换后

- 对 `.docx` 输出执行黑体后处理（三平台通用）：
  ```bash
  python helpers/black_text.py ./output/<file>.docx
  ```
- 验证输出文件存在且大小 > 0

#### 数据分析和 PPT 作业

**数据分析作业流程**：
1. 用 Python 检测 CSV 编码（UTF-8 / GBK / GB2312）
2. 用 xlsx skill 读取 CSV/XLSX 数据
3. 理解数据结构和内容
4. 用 Python（pandas，如可用）做统计分析
5. 用 xlsx skill 生成带公式和图表的 Excel 报告
6. 用 docx skill 生成文字分析报告
7. 按需用 pptx skill 生成汇报 PPT

**CSV 编码自动检测**（Windows 上 CSV 常为 GBK）：
```python
import sys
with open('file.csv', 'rb') as f:
    raw = f.read(3)
# BOM 检测
if raw.startswith(b'\xef\xbb\xbf'):
    enc = 'utf-8-sig'
else:
    # 尝试 UTF-8，失败则用 GBK
    try:
        open('file.csv', encoding='utf-8').read()
        enc = 'utf-8'
    except:
        enc = 'gbk'
print(f'CSV encoding: {enc}')
```

**PPT 作业流程**：
1. 读取 task.md 了解 PPT 要求
2. 从 Markdown 内容或数据中提取核心观点
3. 用 pptx skill 生成演示文稿（含标题页、目录、内容页、总结页）
4. 应用中文格式（按平台选择字体）：标题 44pt 黑体, 正文 28pt 宋体

### 阶段 7：结构化汇报

```
[7/7] 汇报
```

输出格式：

```
## 处理汇报

### 已完成
- 逐条列出

### 未完成
- 无 / 说明原因

### 遇到的问题
- 无 / 报错警告

### 输出文件
| 源文件 | 输出 | 大小 | 状态 |
|--------|------|------|------|
| xxx.md | xxx.docx | 23KB | OK |
| data.csv | analysis_report.docx | 156KB | OK |

全部处理完成，没有失败。
```

---

## 转换后端降级（非 Claude Code / OpenCode 环境）

在 Codex 或 Cursor 中，`document-skills@anthropic-agent-skills` 插件不可用。此时格式转换降级为以下方案：

| 操作 | Claude Code / OpenCode | Codex / Cursor 降级 |
|------|----------------------|---------------------|
| MD → DOCX | docx skill | `pandoc input.md -o output.docx --reference-doc=template.docx` 或 python-docx |
| MD → PDF | docx skill → pdf skill | `pandoc input.md -o output.pdf --pdf-engine=weasyprint` |
| DOCX → MD | docx skill 提取文字 | `pandoc input.docx -o output.md` |
| PDF → MD | pdf skill 提取文字 | `pdfplumber` 或 `pymupdf` 提取文字 |
| XLSX/CSV 分析 | xlsx skill | `openpyxl` + `pandas` 读取和分析 |
| PPTX 生成 | pptx skill | `python-pptx` 手动构建幻灯片 |
| DOCX 黑体后处理 | `python helpers/black_text.py` | 同左（Python stdlib，始终可用） |
| Mermaid 渲染 | `python helpers/render_mermaid.py` | 同左（Python stdlib，始终可用） |

**降级环境前置准备**（Codex / Cursor 用户）：
```bash
pip install python-docx python-pptx openpyxl pdfplumber pandas
# 可选：pandoc 提供更完整的格式转换
# https://pandoc.org/installing.html
```

**检测逻辑**：在阶段 1 环境检查时，通过 harness 检测结果自动选择后端。Claude Code 和 OpenCode 使用 document-skills 插件，Codex 和 Cursor 使用降级方案。

---

## document-skills 委托提示词模板

### MD → DOCX

```
使用 docx skill 将 {文件路径} 转换为 Word 文档。
按 Stage 6 中文格式要求排版（A4/页边距/字体/行距/代码块/三线表/OMML公式/纯黑/自动编号），
平台字体从 skill.json platforms.<os>.fonts 获取。输出到 ./output/。
```

### MD → PPTX

```
使用 pptx skill 将 {文件路径} 生成演示文稿。
标题44pt{平台对应黑体}，正文28pt{平台对应宋体}，每页一个核心观点。
包含标题页/目录页/内容页/总结页，配色深蓝(#1a365d)白底。输出到 ./output/。
```

### CSV/XLSX 数据分析

```
使用 xlsx skill 读取 {文件路径}，分析数据结构和内容。
列出列名/数据类型/统计信息，识别关键指标和趋势，生成含图表的分析报告。
用 docx skill 生成文字报告。输出到 ./output/。
```

### .tex → PDF（LaTeX 编译）

**编译器检测**（按优先级）：

| 编译器 | 优势 | Windows | macOS | Linux |
|--------|------|---------|-------|-------|
| `tectonic` | 自动下载缺失包、多遍编译、零配置 | `winget install tectonic` | `brew install tectonic` | `apt install tectonic` 或下载二进制 |
| `xelatex` | 中文支持好 | MiKTeX/Win自带 | MacTeX 自带 | `apt install texlive-xetex` |
| `pdflatex` | 最普遍 | MiKTeX/Win自带 | MacTeX 自带 | `apt install texlive-latex-base` |

**检测命令**：
```bash
# 按优先级检测
python -c "
import shutil
for cmd in ['tectonic', 'xelatex', 'pdflatex']:
    if shutil.which(cmd):
        print(f'LATEX: {cmd}')
        break
else:
    print('LATEX: not found')
"
```

**编译命令**（按检测到的编译器选择）：
```bash
# tectonic（推荐，自动处理交叉引用和 BibTeX）
tectonic -X compile <file>.tex -o ./output/

# xelatex（中文支持最佳）
xelatex -interaction=nonstopmode -output-directory=./output <file>.tex

# pdflatex
pdflatex -interaction=nonstopmode -output-directory=./output <file>.tex
```

**编译后清理**：删除 `.aux`、`.log`、`.out`、`.toc`、`.synctex.gz` 等辅助文件。

**如果所有编译器都未安装**：
```
当前系统未检测到 LaTeX 编译器。推荐安装 tectonic（最轻量，自动管理依赖）：

  Windows: winget install tectonic
  macOS:   brew install tectonic
  Linux:   从 https://github.com/tectonic-typesetting/tectonic/releases 下载 AppImage

或者安装完整 TeX Live：

  Windows: winget install MiKTeX.MiKTeX
  macOS:   brew install --cask mactex  (约 4GB)
  Linux:   sudo apt install texlive-xetex texlive-latex-extra

跳过 .tex 文件的编译。其他格式转换继续。
```

**LaTeX 委托提示词模板**（当编译器可用时）：

```
使用 {tectonic/xelatex/pdflatex} 将以下 .tex 文件编译为 PDF：

{文件路径}

要求：
1. 当前平台: {Windows/macOS/Linux}
2. 编译器: {检测到的编译器}
3. 中文支持: 如使用 xelatex，确保 \usepackage{ctex} 或 \usepackage{xeCJK}
4. 输出到 ./output/ 目录
5. 编译后清理辅助文件 (.aux, .log 等)
```

---

## Typst 编译支持

Typst 是新一代排版系统，语法比 LaTeX 简洁，编译速度极快（增量编译），在大学生中快速流行。DocWizard 支持 `.typ` 文件的读取和编译。

### 编译器检测

```bash
typst --version 2>/dev/null && echo "TYPST: available" || echo "TYPST: not found"
```

### 安装（按平台）

| 平台 | 安装命令 |
|------|----------|
| Windows | `winget install --id Typst.Typst` |
| macOS | `brew install typst` |
| Linux | 下载二进制: https://github.com/typst/typst/releases |

### 编译命令

```bash
# 编译为 PDF
typst compile <file>.typ ./output/<file>.pdf

# 编译为 PNG（逐页）
typst compile <file>.typ ./output/<file>.png

# 监听模式（增量编译，适合写作时实时预览）
typst watch <file>.typ ./output/<file>.pdf
```

### 读取 .typ 文件内容

`.typ` 文件是纯文本格式，agent 可以直接全文读入理解内容。Typst 语法与 Markdown 类似，包含：
- `= 标题` / `== 二级标题`（标题层级）
- `#figure()` 图表引用
- `$...$` / `$ ... $` 行内/块级公式
- `#bibliography("refs.bib")` 参考文献

### 委托提示词模板

```
当前系统已安装 Typst 编译器。将以下 .typ 文件编译为 PDF：

{文件路径}

要求：
1. 当前平台: {Windows/macOS/Linux}
2. 编译器: typst
3. 如果 .typ 文件引用了 .bib 文件，确保编译时能访问到
4. 输出到 ./output/ 目录
5. 如果用户需要，同时生成 PNG 预览
```

---

## PDF 解析增强（含纯图片/扫描版 PDF）

document-skills 的 pdf skill 内置了 Tesseract OCR 回退：当标准文本提取（pypdf/pdfplumber）无结果时，自动将每页转为图片后调用 Tesseract 识别。但这对于复杂排版、公式、表格的扫描件效果有限。

### 三层策略

| 层级 | 方案 | 适用场景 | 准确率 | 依赖 |
|------|------|----------|--------|------|
| **1** | document-skills 内置 OCR（Tesseract） | 清晰的印刷体 PDF | 80-90% | `tesseract-ocr` + `poppler-utils`（系统包） |
| **2** | MinerU Skill（云端，零安装） | 复杂排版、公式、表格、CJK | 优秀 | `npx skills add Nebutra/MinerU-Skill` |
| **3** | marker-pdf（本地，高精度） | 离线、隐私敏感 | 95%+ | `pip install marker-pdf[full]`（需 PyTorch） |

**⚠️ 重要限制**：Tesseract 和 marker-pdf 主要处理**文字**提取。对于扫描件中的**表格结构**（单元格边界、合并单元格）和**图片区域**（图表、照片），基础 OCR 会丢失结构信息，将表格输出为混乱的纯文本。

### 表格与图片增强（层级 4）

当扫描 PDF 包含**复杂表格**或**重要图片/图表**时，使用以下工具保留结构化信息：

| 工具 | 类型 | 表格输出 | 图片处理 | 安装 |
|------|------|----------|----------|------|
| **Chandra OCR** | 开源本地 | HTML/Markdown/JSON（保留单元格结构） | 提取图片+标题+位置 | `pip install chandra-ocr` |
| **Surya OCR** | 开源本地 | HTML/Markdown（表格边框检测） | 布局分析识别图片区域 | `pip install surya-ocr` |
| **LlamaParse** | 云端免费 | Markdown 表格（VLM 识别） | 图表语义理解 | `pip install llama-cloud`（1K页/天免费） |
| **SmolDocling** | 开源本地 | DocTags→HTML/Markdown（256M 参数） | 图表分类+标题链接 | `pip install docling`（含 smoldocling） |

**推荐策略**：
- 开源场景：优先 **Chandra OCR**（表格+图片+全文结构，88% 表格准确率，Apache 2.0）
- 入门场景：优先 **Surya OCR**（纯 Python，CPU 可用，90+ 语言）
- 高精度场景：**LlamaParse** 云端（VLM 驱动，1K 页/天免费）
- 轻量场景：**SmolDocling**（256M 参数，0.35s/页，<1GB 显存）

**层级 1 限制**：无布局保留、无公式识别、无表格结构提取、手写体几乎不可用（30-55%）。仅适合干净的印刷文档。

**层级 2 推荐用于大多数学生场景**：一条命令安装，无需本地 GPU，公式→LaTeX、表格→HTML、布局保留为 Markdown。

**层级 3 适合离线/隐私场景**：完全本地运行，多语言支持（90+），保留文档结构，支持 GPU 加速。

### 自动检测与选择

```
检测 PDF 类型:
  ├─ 文字型 PDF（第一页 > 50 字符）
  │   → 使用 pdf skill 提取文字和表格
  │
  ├─ 扫描版/图片型 PDF（第一页 < 50 字符）
  │   ├─ 检测 MinerU Skill 是否可用（npx skills list）
  │   │   → 可用: 委托给 MinerU 做 OCR 提取
  │   │   → 不可用: 检测 Tesseract 是否安装
  │   │       → 已安装: 使用 document-skills 内置 OCR（层级 1）
  │   │       → 未安装: 提示用户安装 MinerU 或 Tesseract
  │   │
  │   ├─ 检测是否需要保留表格/图片结构（文档含表格或图表）
  │   │   → 检测 chandra-ocr 是否安装（pip list | grep chandra）
  │   │   → 已安装: 使用 Chandra OCR 提取（保留表格 HTML + 图片结构）
  │   │   → 未安装: 检测 surya-ocr 是否安装
  │   │       → 已安装: 使用 Surya OCR 提取
  │   │       → 未安装: 提示安装（pip install chandra-ocr 或 pip install surya-ocr）
  │   │   → 云端备选: pip install llama-parse（1K页/天免费，VLM 驱动）
  │   │
  │   └─ 离线环境: 提示安装 marker-pdf（文字）或 chandra-ocr（表格+图片）
  │
  └─ 需要合并/拆分/加密操作
      → 检测 pdf-toolkit-mcp 是否可用
      → 可用: 委托给 pdf-toolkit-mcp
      → 不可用: 用 Python pypdf 做基础操作
```

**PDF 类型自动检测**：
```python
# 快速检测 PDF 是否为扫描版（无文字层）
import sys
try:
    import pdfplumber
    with pdfplumber.open('file.pdf') as pdf:
        text = pdf.pages[0].extract_text() or ''
        if len(text.strip()) < 50:
            print('SCANNED: PDF 可能是扫描版，建议使用 OCR')
        else:
            print(f'TEXT: 第一页有 {len(text)} 个字符')
except ImportError:
    print('UNKNOWN: 无法检测，使用 pdf skill 默认方式')
```

---

## Markdown→Word 公式增强

当文档包含大量 LaTeX 数学公式时，可引入专门的公式转换 Skill。

### 推荐 Skill

| Skill | 功能 | 安装 |
|-------|------|------|
| `@clipg/w2w` | Markdown→Word，LaTeX 公式→Word 原生 OMML 公式 | `/plugin install @clipg/w2w` |

### 使用策略

```
检测 .md 中的公式密度:
  ├─ 少量公式 (< 5个 $$...$$)
  │   → 使用 document-skills docx skill 默认转换
  │   → OMML 转换失败时降级为图片
  │
  └─ 大量公式 (≥ 5个 $$...$$) 或数学/物理作业
      → 检测 @clipg/w2w 是否可用
      → 可用: 委托给 w2w 做公式→OMML 转换
      → 不可用: 提示用户安装 @clipg/w2w，暂用 docx skill
```

**公式密度检测**：
```bash
grep -c '\$\$' <file.md>
```

---

## 参考文献管理

支持从 `.bib` 文件生成格式化参考文献列表，支持常用引用格式。

### ⚠️ 参考文献防造假策略（必须遵守！）

**AI 生成参考文献存在严重的"造假"风险**——模型会编造看起来真实但根本不存在的论文。DocWizard 采用多层防护：

#### 第一层：来源约束

```
参考文献只能来自以下来源:
  1. 用户提供的 .bib 文件（最可靠）
  2. 用户手写在 Markdown 中的参考文献
  3. 用户明确提到的论文标题/作者/DOI

绝对禁止:
  ❌ AI 凭空编造参考文献
  ❌ AI 根据"常识"补充不存在的论文
  ❌ 生成 DOI 后不验证就直接使用
```

#### 第二层：DOI 验证

对每一条参考文献，如果有 DOI，必须验证：

```python
import urllib.request, json
def verify_doi(doi):
    """通过 CrossRef API 验证 DOI 是否存在"""
    url = f'https://api.crossref.org/works/{doi}'
    req = urllib.request.Request(url, headers={'User-Agent': 'DocWizard/3.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data['status'] == 'ok'
    except:
        return False
```

#### 第三层：多源交叉验证

| 验证源 | API | 适用领域 |
|--------|-----|----------|
| CrossRef | `api.crossref.org/works/{doi}` | 全学科 DOI 验证 |
| Semantic Scholar | `api.semanticscholar.org/graph/v1/paper/search?query={title}` | 论文标题搜索 |
| DBLP | `dblp.org/search/publ/api?q={title}` | 计算机科学 |
| arXiv | `export.arxiv.org/api/query?search_query={title}` | 预印本 |

#### 第四层：验证报告

输出文档末尾附加验证报告：

```
## 参考文献验证报告

| 序号 | 引用 | 验证状态 | 来源 |
|------|------|----------|------|
| [1] | Zhang et al. (2023) | ✅ DOI 验证通过 | user.bib |
| [2] | Li & Wang (2022) | ✅ Semantic Scholar 确认 | user.bib |
| [3] | Chen et al. (2024) | ⚠️ 未找到 DOI，人工确认 | Markdown 手写 |
```

**如果参考文献验证失败率 > 20%**：停止输出，向用户报告问题，要求用户提供正确的参考文献。

#### 可集成的外部工具

| 工具 | 用途 | 集成方式 |
|------|------|----------|
| `refcheck` MCP | 自动验证参考文献 | 安装: 搜索 refcheck MCP server |
| `CheckIfExist` | 批量 BibTeX 验证 (Crossref/Semantic Scholar/OpenAlex) | GitHub 开源工具 |
| `VeriBib` | Semantic Scholar API 检测 AI 幻觉引用 | GitHub 开源工具 |

### 触发条件

- 目录中存在 `.bib` 文件
- task.md 中提到「参考文献」「引用格式」「bibliography」
- Markdown 中有 `[@citation_key]` 或 `\cite{key}` 引用标记

### 支持的引用格式

| 格式 | 适用场景 | 示例 |
|------|----------|------|
| GB/T 7714 | 中国高校论文 | 张三, 李四. 人机交互设计原理[M]. 北京: 清华大学出版社, 2023. |
| APA 7th | 心理学、教育学 | Zhang, S., & Li, S. (2023). *Human-Computer Interaction Design*. Tsinghua University Press. |
| MLA 9th | 人文社科 | Zhang, San, and Si Li. *Human-Computer Interaction Design*. Tsinghua University Press, 2023. |

### 处理流程

```
发现 .bib 文件:
  1. 读取 .bib 内容
  2. 检测 task.md 中指定的引用格式（默认 GB/T 7714）
  3. 解析 BibTeX 条目 (article, book, inproceedings, etc.)
  4. 按指定格式生成参考文献列表
  5. 追加到输出文档末尾
  6. 保留 .bib 源文件
```

**BibTeX 解析**（Python 示例）：
```python
import re
def parse_bibtex(path):
    entries = []
    with open(path) as f:
        content = f.read()
    for match in re.finditer(r'@(\w+)\{(\w+),\s*(.+?)\}', content, re.DOTALL):
        etype, key, fields = match.group(1), match.group(2), match.group(3)
        entry = {'type': etype, 'key': key}
        for fm in re.finditer(r'(\w+)\s*=\s*[{"](.+?)[}"]', fields):
            entry[fm.group(1).lower()] = fm.group(2)
        entries.append(entry)
    return entries
```

**注意**：此功能面向**作业级别的参考文献处理**（课程论文、实验报告），不涉及：
- 论文级别的文献综述
- 7 维审稿模拟
- 预印本平台提交
- 期刊格式适配

如果用户需要完整的学术论文写作辅助，建议额外安装 `academic-paper-skills`。

---

## 课程设计报告 — 模板填充工作流

**场景**：学生代码写完了，但课程设计报告没写。老师给了 DOCX 或 LaTeX 模板，需要根据已有代码完成报告。

### 触发条件

- 目录中存在老师给的模板文件（`template.docx` / `模板.docx` / `template.tex`）
- 目录中存在代码文件（`src/` / `*.py` / `*.java` / `*.cpp` 等）
- task.md 提到「课程设计」「课程报告」「根据模板」「填充报告」

### 工作流

1. **读取模板，理解结构**：DOCX 模板 → docx skill 提取文字 → 分析占位符/章节/页眉页脚；LaTeX 模板 → 全文读入 → 分析 `\section{}`/`\title{}`/`\input{}` 结构
2. **读取代码，理解项目**：扫描 `src/` → 理解功能/架构/关键实现 → 提取关键代码片段和运行方法
3. **按模板逐章生成**：封面 → 摘要 → 引言 → 系统设计(Mermaid 架构图) → 详细实现 → 测试与分析 → 总结 → 参考文献 → 附录。每章确认后推进下一章
4. **填入模板 + 输出**：保持原格式/页眉页脚/水印 → black_text.py → pdf skill 导出 PDF。LaTeX 模板则保持 .tex 结构填充 → tectonic/xelatex 编译。输出：课程设计报告.docx + 课程设计报告.pdf

### 关键原则

1. **尊重模板**：不改变老师给的模板结构、页眉页脚、水印
2. **代码驱动**：报告内容基于实际代码生成，不是凭空编造
3. **逐章确认**：每章生成后给用户看一眼，避免方向跑偏
4. **图表自动**：从代码自动提取架构生成 Mermaid 图
5. **保留代码**：源码目录不做任何修改

---

## 上下文策略

### 核心原则：agent 必须能读懂所有文件

**agent 无法直接读取 .docx/.doc/.pdf/.pptx/.xlsx（二进制格式）。扫描到这些文件时，必须先提取文字再读！**

### 预读取流程

| 文件类型 | 处理方式 |
|----------|----------|
| `.md` | **全文读入** — 用户作业内容，必须读完 |
| `.docx` / `.doc` | **委托 docx skill 提取文字 → 全文读入** |
| `.pdf` | **委托 pdf skill 提取文字和表格 → 全文读入** |
| `.pptx` | **委托 pptx skill 提取文字 → 全文读入** |
| `.xlsx` / `.csv` | **委托 xlsx skill 读取结构和前20行 → 了解数据内容** |
| `.tex` / `.typ` | **全文读入** — 纯文本格式，可直接理解内容 |
| `.drawio` / `.dio` | **全文读入** — 检查图表引用 |
| `task.md` | **全文读入** — 理解用户需求（只读不写！） |
| `skill.json` | **全文读入** — 获取配置和转换规则 |

---

## 图表渲染管线

### 优先级决策

| 条件 | 工具 | 理由 |
|------|------|------|
| 流程图、旅程图、简单架构（<20节点） | **Mermaid** → mermaid.ink → PNG | 三平台通用，零依赖 |
| 复杂架构全景、多层嵌套 | **DrawIO MCP** → export_diagram → PNG+SVG | 手动布局更精确 |
| 手绘风格、UI草图 | **DrawIO MCP** | Mermaid 不适合 |

### Mermaid 渲染

**方式一：mermaid.ink 在线渲染（默认，零依赖）**：
```bash
python helpers/render_mermaid.py <file.md> --output-dir ./output
```

**方式二：mermaid-cli 本地渲染（可选，离线稳定）**：
检测 `mmdc` 命令是否可用：
```bash
# 检测
command -v mmdc &> /dev/null && echo "mermaid-cli available" || echo "not found"

# 安装（需要 Node.js）
npm install -g @mermaid-js/mermaid-cli

# 使用
mmdc -i <file>.mmd -o <output>.png -s 2
```

**渲染优先级**：
1. 先尝试 mermaid.ink 在线渲染（零依赖，始终可用）
2. 如果 mermaid.ink 网络不通（超时/403），且检测到 `mmdc` → 切换到本地渲染
3. 渲染失败时报告并跳过该图表，继续处理其他文档

**渲染后验证**：检查 PNG 文件大小 > 100 bytes，否则视为失败。

支持图表类型：graph/flowchart, journey, sequenceDiagram, gantt, pie, classDiagram, stateDiagram, erDiagram

### DrawIO 渲染（如 DrawIO MCP 可用）

1. 创建 `.drawio` 文件（MCP 的 `create_diagram`）
2. 调用 `export_diagram` 导出 `.png` + `.svg`
3. **保留 .drawio 源文件** — 方便以后修改
4. 在 .md 中用 `![](xxx.png)` 引用

---

## 智能场景识别（新增）

### 场景：压缩包内有 Word 需求文档

当解压压缩包后发现 `.docx` 文件时，自动识别是否为**作业要求文档**：

1. 解压后，委托 docx skill 提取 `.docx` 的全部文字
2. 判断内容是否为作业要求（包含「任务」「要求」「分析」「请」等关键词）
3. 如果是作业要求 → **以此为准**执行任务，优先级等同于 task.md
4. 如果只是普通文档 → 加入转换队列

### 场景：要求提交分析代码

当 task.md 或 Word 需求文档中提到「提交代码」「附上代码」「分析脚本」时：

1. 将分析过程中使用的 Python 代码整理为独立脚本
2. 添加注释和说明
3. 保存为 `analysis_script.py` 到 `./output/` 目录
4. 在汇报中列出该文件

---

## 更新机制

```bash
git pull origin main
```

DocWizard 仓库在你的 skills 目录下（`.agents/skills/DocWizard/`、`.claude/skills/DocWizard/` 等），直接 git pull 即可更新。

---

## 常见问题

| 问题 | 平台 | 解决 |
|------|------|------|
| document-skills 插件未安装 | Claude Code / OpenCode | `/plugin install document-skills@anthropic-agent-skills` |
| document-skills 不可用 | Codex / Cursor | 此插件为 Anthropic 专有。降级方案：pip install python-docx python-pptx openpyxl pdfplumber |
| DOCX 输出有彩色文字 | 全部 | `python helpers/black_text.py <file.docx>` |
| Mermaid 图渲染失败 | 全部 | mermaid.ink 需要外网访问 |
| PDF 中文乱码 | Linux | `sudo apt install fonts-noto-cjk` |
| PDF 中文乱码 | macOS | 确保 PingFang SC / Songti SC 可用 |
| PDF 中文乱码 | Windows | 确保 SimSun / SimHei 字体存在 |
| RAR/7z 无法解压 | 全部 | 参见 Stage 3 压缩包提取章节的安装命令（按平台自动选择） |
| CSV 中文乱码 | Windows | 自动检测 GBK 编码（cp936） |
| 扫描版 PDF 无法提取文字 | 全部 | 使用 pdf skill 的 OCR 功能 |
| Windows ZIP 中文文件名乱码 | Windows | Python 脚本自动 cp437→utf-8→gbk 解码 |
| 公式显示为图片 | 全部 | OMML 转换失败时降级为图片 |

---

## 隐藏功能：论文写作辅助

> **⚠️ 此功能默认关闭，不会自动触发。**
>
> 论文是长程任务，写作周期长、修改困难。如果每次对话都激活论文写作，会让 Skill 变得臃肿，干扰日常作业处理。
>
> 此功能面向使用 Claude Code / Codex / OpenCode / Cursor 等 AI 编程工具的学生群体。

### 启用条件

**只有用户明确说出以下关键词之一时，才进入论文写作模式：**

```
「写论文」「论文写作」「帮我写论文」「毕业论文」「开题报告」
「启用论文模式」「论文辅助」「学术写作」
```

**听到这些关键词后，必须先确认：**

> 你确定要启用论文写作辅助吗？
>
> ⚠️ 重要提示：
> 1. 论文写作是长程任务，建议分章节逐章进行
> 2. 所有生成的参考文献必须经过验证（防造假策略始终生效）
> 3. AI 生成的内容仅作参考，最终内容需你自行审核
> 4. 此功能会消耗较多 token，耗时较长
>
> 是否继续？[Y/n]

用户说「是」「Y」「继续」后才进入论文写作流程。

### 论文写作流程

论文写作是**分阶段、分章节**的长程任务，不支持一次性生成全文。

#### 阶段 A：前期准备

```
1. 了解论文主题和研究方向
2. 如果用户提供了参考文献 (.bib)，解析并验证
3. 如果用户提供了提纲，按提纲执行；否则先讨论提纲
4. 确定论文结构（章节划分）
5. 确认引用格式（默认 GB/T 7714）
```

#### 阶段 B：逐章写作（核心流程）

```
对每一章，执行以下子流程：

1. 讨论本章目标: 用户说明本章要写什么
2. 生成初稿: AI 生成该章节的初稿
3. 用户审阅: 用户指出需要修改的地方
4. 修改迭代: AI 根据反馈修改（最多 3 轮）
5. 用户确认: 用户说「这章可以了」→ 进入下一章

章节不会自动推进，必须等用户确认后才进入下一章。
```

#### 阶段 C：整体打磨

```
1. 全文通读 → 检查章节间逻辑连贯性
2. 参考文献验证 → 运行 verify_refs.py
3. 格式统一 → 标题编号、图表编号、引用格式
4. 生成摘要 → 根据全文内容生成中英文摘要
```

#### 阶段 D：输出

```
1. 生成完整 .md 文件
2. 转换为 .docx（按中文学术格式）
3. 转换为 .pdf
4. 附加参考文献验证报告
5. 输出到 ./output/ 目录
```

### 论文写作约束

| 约束 | 说明 |
|------|------|
| 逐章推进 | 一章确认后才开始下一章，不自动跳转 |
| 引用验证 | 所有参考文献必须通过 DOI/CrossRef 验证 |
| 用户主导 | 每章由用户确认方向，AI 不替用户做学术判断 |
| 降级输出 | 如果用户中途想退出，可说「退出论文模式」，已写内容保留 |
| 不自动保存 | 每章确认后用户自行保存，避免覆盖问题 |

### 论文写作与其他功能的关系

| 论文写作中可用 | 论文写作中不可用 |
|---------------|-----------------|
| 参考文献验证 (verify_refs.py) | 自动扫描目录全量转换 |
| Mermaid 图表渲染 | 压缩包批量解压 |
| 单文件格式转换 (按需) | task.md 自动化流程 |
| 参考文献格式化 | 数据分析报告 |

论文写作模式下，DocWizard 的其他自动功能被抑制，只保留手动调用的辅助工具。

### 退出论文模式

用户说「退出论文模式」「结束论文」「论文写完了」即可退出。

退出后：
- 已生成的章节内容保留
- 恢复正常的 DocWizard 自动功能
- 用户可继续使用格式转换功能输出最终版本