# md2docx-pdf

> `.md` ↔ `.docx` ↔ `.pdf` 三向互转。扫描目录，自动检测文档，每个文件转为其余两种格式。

跨平台，首次运行自动检查 pandoc（缺失会询问是否安装），完美支持中文排版。

---

## 快速开始

```bash
git clone https://github.com/cowhorse05/md2doc2pdf.git
cd md2doc2pdf

# 首次使用：交互式设置向导（选择安装可选组件）
python md2docx_pdf.py --setup

# 扫描当前目录，列出所有文档，询问后转换
python md2docx_pdf.py

# 跳过询问，直接全转
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

> 帮我安装 https://github.com/cowhorse05/md2doc2pdf 这个 skill

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

1. 读 `task.md` 了解需求，扫描目录填文件列表
2. 按你勾选的要求执行转换
3. 输出结构化汇报：**已完成 / 未完成 / 遇到的问题 / 输出文件清单**
4. 把结果写回 `task.md`

图表多的作业加一句 "drawio 也导出" 就行。

### 更新 skill

```bash
# 检查并更新到最新版本
python md2docx_pdf.py --update
```

或者对你的 AI 说：

> 检查 md2docx-pdf 有没有新版本

---

## 转换规则

| 源格式 | 输出 |
|--------|------|
| `.md` | `.docx` + `.pdf` |
| `.docx` / `.doc` | `.md` + `.pdf` |
| `.pdf` | `.md` + `.docx`（需 `pdftotext`） |
| `.tex` | `.pdf`（需 xelatex/pdflatex，**可选**） |

---

## 设置向导（首次使用必看）

首次安装后，运行交互式设置向导，**逐项选择**你要装哪些组件：

```bash
python md2docx_pdf.py --setup
```

向导会逐项检查并询问：

```
=== md2docx_pdf 设置向导 ===

[1/5] Python 环境
Python 3.9.0  ✓

[2/5] pandoc (必装，所有格式转换都需要)
pandoc 3.1  ✓

[3/5] pdftotext (可选，PDF → 文字提取)
用途: 把 PDF 转回 .md / .docx
[未安装] 是否安装? [y/N]

[4/5] LaTeX (可选，.tex → PDF 编译)
用途: 编译 .tex 文件为 PDF
⚠ 注意: 安装包较大 (数百MB ~ 4GB)
[未安装] 是否安装? [y/N]

[5/5] 浏览器 (PDF 输出需要)
Chrome ✓
```

- **pandoc** → 必装，缺失会强制询问
- **pdftotext** → 可选，需要 PDF 转文字再装
- **LaTeX** → 可选，需要编译 .tex 再装（包很大，考虑清楚）
- **浏览器** → 可选，Windows 自带 Edge 通常自动检测到

跳过的组件以后随时可以补装：`python md2docx_pdf.py --setup`

---

## 依赖安装

首次运行自动检测，缺 pandoc 会询问"是否现在安装"。推荐先跑 `--setup` 一次性搞定。

### pandoc（必装，三种格式都需要）

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
  --setup, --install  交互式设置向导，选择安装可选组件
  --update, --upgrade 检查 GitHub 仓库是否有新版本并更新
  -s DIR              扫描指定目录
  -y                  跳过确认，直接全转
  -f docx|pdf         仅 .md 有效，限制输出格式
  -o DIR              输出目录，默认同源文件
  --drawio            启用 drawio 图表导出 (需要 drawio MCP)
  --version           看版本
```

---

## 运行效果

```
  md2docx_pdf v1.1.0  https://github.com/cowhorse05/md2doc2pdf
  平台: Windows
  pandoc: pandoc 3.9.0.2
  浏览器: chrome.exe

  扫描目录: .

  找到 3 个文件:
    Markdown (.md): 2 个
      报告.md
      笔记.md
    Word (.docx): 1 个
      附件.docx

  全部转换为其余格式? [Y/n] y

[MD] 报告.md (18,139 bytes)
  -> DOCX: 报告.docx ... OK (23,000 bytes)
  -> PDF:  报告.pdf ... OK (652,383 bytes)

[MD] 笔记.md (8,420 bytes)
  -> DOCX: 笔记.docx ... OK (12,100 bytes)
  -> PDF:  笔记.pdf ... OK (310,500 bytes)

[DOCX] 附件.docx (45,200 bytes)
  -> MD:   附件.md ... OK (6,800 bytes)
  -> PDF:  附件.pdf ... OK (280,000 bytes)

==================================================
  OK 6   FAIL 0
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

## 常见问题

| 问题 | 解决 |
|------|------|
| pandoc 没装 | 工具会询问是否安装，选 y 自动装 |
| LaTeX 没装 | 可选，不编译 .tex 就不需要 |
| PDF 中文乱码 | Linux: `apt install fonts-noto-cjk` |
| Permission denied | 关掉 Word 重试 |
| PDF 转出来是乱码 | 扫描版 PDF（图片）无法提取文字 |

---

## License

MIT — 李裕峰
