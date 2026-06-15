# DocWizard

> AI 驱动的作业一站式助手。说一句话，Markdown → Word + PDF 自动完成。图表渲染、智能互转、可选依赖安装。

跨平台，首次运行 `--setup` 进入交互式设置向导，完美支持中文排版。**Mermaid 图表自动渲染为 PNG 嵌入 DOCX，DOCX 字体强制纯黑。**

---

## 快速开始

```bash
git clone https://github.com/cowhorse05/DocWizard.git
cd DocWizard

# 首次使用：交互式设置向导（选择安装可选组件）
python md2docx_pdf.py --setup

# 扫描当前目录，列出所有文档，询问后转换
python md2docx_pdf.py

# 跳过询问，直接全转（Mermaid 图表自动渲染为 PNG）
python md2docx_pdf.py -y

# 扫描指定目录
python md2docx_pdf.py -s ./docs

# 单文件互转
python md2docx_pdf.py 报告.md       # .md  → .docx + .pdf
python md2docx_pdf.py 报告.docx    # .docx → .md + .pdf
python md2docx_pdf.py 报告.pdf     # .pdf  → .md + .docx

# 批量转换
python md2docx_pdf.py -y *.md      # 批量 .md → .docx + .pdf

# 单格式输出（仅 .md 支持）
python md2docx_pdf.py 报告.md -f pdf
```

### 懒人做法（AI 一句话搞定）

把下面这句话发给 Claude Code（或任意 AI 工具），它会自动 clone、逐项问你装不装可选依赖、然后扫描文件夹完成转换：

> 帮我安装 https://github.com/cowhorse05/DocWizard 这个 skill

**AI 会这样一步步来：**

```
① git clone 仓库
② 检查 Python ✓
③ pandoc 没装? → 问你要不要装 [Y/n]
④ pdftotext 没装? → 说明用途，问你要不要装 [y/N]
⑤ LaTeX 没装? → 说明用途 + 警告体积(数百MB~4GB)，问你要不要装 [y/N]
⑥ 浏览器检测 → 没找到就让你手动指定路径或跳过
⑦ 【最后选项】"环境配好了，要不要扫描目录开始转换?"
    → 选 A: 扫描目录，读 task.md，执行转换，输出汇报
    → 选 B: 你先填 task.md，待会说「执行」
    → 选 C: 先不，以后再说
```

**或者直接说：**

> 执行 task.md

clone 下来的仓库带了一个 `task.md` 模板，把你的文件名列进去，勾上要转的格式，然后一句话交给 AI。AI 会：

1. 读 `task.md` 了解需求（只读不写！）
2. 扫描目录，发现 .docx/.pdf 先转 .md 再读内容
3. 按你勾选的要求执行转换
4. 输出结构化汇报：**已完成 / 未完成 / 遇到的问题 / 输出文件清单**
5. 把结果写回 `task.md` 的「执行结果」

图表多的作业加一句 "drawio 也导出" 就行。

### 更新

```bash
# 检查并更新到最新版本
python md2docx_pdf.py --update
```

或者对你的 AI 说：

> 检查 DocWizard 有没有新版本

---

## 图表渲染（Mermaid → PNG → DOCX 嵌入）

**DOCX 不能渲染 Mermaid 代码块。** DocWizard 会自动检测 `.md` 中的 Mermaid 代码块，通过 mermaid.ink 渲染为 PNG 并嵌入文档。默认可处理 3 种图：

| 图表类型 | 用法 | 适用 |
|----------|------|------|
| 架构图/流程图 | `graph TB` / `flowchart LR` | 系统结构、交互流程 |
| 用户旅程地图 | `journey` | 情绪曲线、体验分析 |
| 时序图 | `sequenceDiagram` | 交互时序 |

转换命令照常，无需额外参数：

```bash
python md2docx_pdf.py report.md -y
# → 自动检测 Mermaid → 渲染 PNG → 替换引用 → DOCX + PDF
```

复杂图（>20 节点、架构全景）建议用 DrawIO MCP 绘制，DocWizard 会自动导出 PNG+SVG 并嵌入。

---

## 转换规则

| 源格式 | 输出 | 备注 |
|--------|------|------|
| `.md` | `.docx` + `.pdf` | Mermaid 自动渲染为 PNG → 嵌入 |
| `.docx` / `.doc` | `.md` + `.pdf` | 先转 .md 供 agent 读取 |
| `.pdf` | `.md` + `.docx` | 需 `pdftotext`，先转 .md 供 agent 读取 |
| `.tex` | `.pdf` | 需 xelatex/pdflatex，**可选** |

---

## 设置向导

首次安装后，运行交互式设置向导，**逐项选择**你要装哪些组件：

```bash
python md2docx_pdf.py --setup
```

向导会逐项检查并询问：

```
=== DocWizard 设置向导 ===

[1/6] Python 环境
Python 3.9.0  ✓

[2/6] pandoc (必装，所有格式转换都需要)
pandoc 3.1  ✓

[3/6] pdftotext (可选，PDF → 文字提取)
用途: 把 PDF 转回 .md / .docx
[未安装] 是否安装? [y/N]

[4/6] LaTeX (可选，.tex → PDF 编译)
用途: 编译 .tex 文件为 PDF
⚠ 注意: 安装包较大 (数百MB ~ 4GB)
[未安装] 是否安装? [y/N]

[5/6] 浏览器 (PDF 输出需要)
Chrome ✓

[6/6] 【最后选项】是否现在扫描目录并完成任务?
  环境配好了！要不要现在就扫描当前目录，开始转换文档？
    A. 是，扫描目录并转换
    B. 我先填 task.md，待会说「执行」
    C. 先不，以后再说
```

- **pandoc** → 必装，缺失会强制询问
- **pdftotext** → 可选，需要 PDF 转文字再装
- **LaTeX** → 可选，需要编译 .tex 再装（包很大，考虑清楚）
- **浏览器** → 可选，Windows 自带 Edge 通常自动检测到

跳过的组件以后随时可以补装：`python md2docx_pdf.py --setup`

---

## 依赖安装

首次运行自动检测，缺 pandoc 会询问"是否现在安装"。推荐先跑 `--setup` 一次性搞定。

### pandoc（必装）

| 系统 | 装法 |
|------|------|
| Windows | `winget install pandoc` |
| macOS | `brew install pandoc` |
| Linux | `sudo apt install pandoc` |

### Chrome / Edge（PDF 输出需要，自动搜索常见路径）

Windows 自带 Edge，macOS 和 Linux 装 Chrome 即可。

### pdftotext（PDF → 文本需要，poppler-utils）

| 系统 | 装法 |
|------|------|
| Windows | `winget install xpdfreader.xpdf-tools` |
| macOS | `brew install poppler` |
| Linux | `sudo apt install poppler-utils` |

---

## 命令说明

```
用法: md2docx_pdf.py [文件...] [选项]

不传文件: 扫描当前目录，列出文档，询问后互转
传文件:   直接转换

选项:
  --setup, --install   交互式设置向导，选择安装可选组件
  --update, --upgrade  检查 GitHub 仓库是否有新版本并更新
  --render-mermaid     强制渲染 Mermaid 代码块（默认自动检测）
  --no-render-mermaid  禁止自动渲染 Mermaid
  -s DIR               扫描指定目录
  -y                   跳过确认，直接全转
  -f docx|pdf          仅 .md 有效，限制输出格式
  -o DIR               输出目录，默认同源文件
  --drawio             启用 drawio 图表导出 (需要 drawio MCP)
  --version            看版本
```

---

## 运行效果

```
  DocWizard v2.0.0  https://github.com/cowhorse05/DocWizard
  平台: Windows
  pandoc: pandoc 3.9.0.2
  浏览器: chrome.exe

  扫描目录: .

  检测到 3 个 Mermaid 图表，自动渲染为 PNG...
  [MERMAID] diagram_01 → diagram_01.png (188,881 bytes)
  [MERMAID] journey_02 → journey_02.png (52,912 bytes)
  [MERMAID] diagram_03 → diagram_03.png (55,000 bytes)
  ✓ 已渲染 3 个图表为 PNG

  找到 1 个文档:
    Markdown (.md): 1 个
      图书馆交互设计.md

[MD] 图书馆交互设计.md (11,956 bytes)
  -> DOCX: 图书馆交互设计.docx ... OK (164,000 bytes)
  -> PDF:  图书馆交互设计.pdf ... OK (650,000 bytes)

==================================================
  OK 2   FAIL 0
  全部转换完成!
==================================================
```

---

## PDF 排版

自动注入中文 CSS：

- 标题 h1 蓝色下划线 / h2 灰色下划线
- 表格带边框，表头加粗灰底，隔行变色
- 代码块浅灰背景等宽字体
- 引用蓝色左边框浅蓝背景
- 字体：Microsoft YaHei → SimSun → PingFang SC → Noto Sans SC

---

## DOCX 黑体策略

DocWizard 采用**双重保障**确保 DOCX 中所有文字为纯黑：

1. **reference.docx**：生成时注入黑色默认 run props + 清除所有 themeColor
2. **后处理**：转换完成后打开 DOCX（ZIP 格式），处理**所有 XML 文件**包括主题，激进替换所有 6 位 hex 颜色值为 `000000`

---

## 常见问题

| 问题 | 解决 |
|------|------|
| pandoc 没装 | `--setup` 向导会询问安装，选 y 自动装 |
| DOCX 有蓝色字体 | v2.0.0 已修复 — 后处理覆盖主题色 + 激进黑体替换 |
| Mermaid 图在 DOCX 里是代码 | 自动检测渲染，无需手动操作。如网络问题导致 mermaid.ink 失败，检查外网访问 |
| LaTeX 没装 | 可选，不编译 .tex 就不需要 |
| PDF 中文乱码 | Linux: `apt install fonts-noto-cjk` |
| Permission denied | 关掉 Word 重试 |
| PDF 转出来是乱码 | 扫描版 PDF（图片）无法提取文字 |
| agent 读不了 .docx | v1.6.1+ 自动先转 .md 再读 |

---

## License

MIT — 李裕峰
