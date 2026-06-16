# DocWizard

> AI 驱动的作业一站式助手。说一句话，文档处理、数据分析、PPT 生成自动完成。零外部依赖，基于 Claude Code 内置 document-skills。

**v3.1.0** — 多 harness 适配（Claude Code / OpenCode / Codex / Cursor）+ 内容精简。

[English Documentation](README.md)

---

## 快速开始

### 1. 安装 document-skills 插件（Claude Code / OpenCode）

```bash
/plugin install document-skills@anthropic-agent-skills
```

此插件一次安装包含 docx、pdf、pptx、xlsx 四个 Skill。**仅 Claude Code 和 OpenCode 支持**。Codex / Cursor 用户见[降级方案](#非-claude-code--opencode-环境)。

### 2. Clone DocWizard

```bash
# 推荐：跨 harness 通用路径
git clone https://github.com/cowhorse05/DocWizard.git .agents/skills/DocWizard

# 或按 harness 选择：
# Claude Code:  .claude/skills/DocWizard
# OpenCode:     .claude/skills/DocWizard（兼容）或 .opencode/skills/DocWizard
# Codex:        .codex/skills/DocWizard 或 .agents/skills/DocWizard
# Cursor:       需转换为 .cursor/rules/docwizard.mdc 格式
```

### 3. 一句话搞定

把下面这句话发给 AI 编程助手：

> 帮我安装 DocWizard skill

AI 会自动：
1. 检测当前 harness（Claude Code / OpenCode / Codex / Cursor）
2. 检查 document-skills 插件是否可用（降级环境自动切换 Python 库方案）
3. 扫描目录发现文档、数据、压缩包
4. 按 task.md 的勾选执行处理
5. 输出结构化汇报

### 或者直接说：

> 执行 task.md

---

## 支持的文件类型

| 源格式 | 输出 | 说明 |
|--------|------|------|
| `.md` | `.docx` + `.pdf` | Mermaid 图表自动渲染为 PNG 嵌入 |
| `.md` | `.pptx` | Markdown 内容生成演示文稿 |
| `.docx` / `.doc` | `.md` + `.pdf` | 先提取文字供 AI 读取 |
| `.pdf` | `.md` + `.docx` | 文字 + 表格提取 |
| `.pptx` | `.md` | 提取 PPT 文字内容 |
| `.xlsx` / `.csv` | 分析报告 (.md + .docx + .xlsx) | 数据分析 + 图表 + 报告 |
| `.drawio` | `.png` + `.svg` | 图表导出嵌入文档 |
| `.tex` | `.pdf` | 自动检测编译器 (tectonic/xelatex/pdflatex) |
| `.typ` | `.pdf` + `.png` | Typst 新一代排版，增量编译、语法简洁 |
| `.zip` / `.rar` / `.7z` | 自动解压 → 处理其中文档 | 智能识别压缩包内 Word 需求文档 |

---

## 中文学术排版

所有文档输出自动应用以下格式：

- **纸张**：A4
- **页边距**：上下 2.54cm，左右 3.17cm
- **正文**：宋体 小四 (12pt)，1.5 倍行距，首行缩进 2 字符
- **标题**：黑体，一级三号 (16pt)，二级四号 (14pt)，自动编号
- **英文/数字**：Times New Roman 12pt
- **代码块**：等宽字体，浅灰背景，语法高亮保留
- **表格**：三线表样式，表头加粗居中
- **公式**：$$...$$ → OMML 可编辑格式
- **字体颜色**：纯黑 (#000000)

---

## 图表渲染

DOCX 不能渲染 Mermaid 代码块。DocWizard 自动检测 `.md` 中的 Mermaid 代码块，通过 mermaid.ink 渲染为 PNG 并嵌入文档。

支持图表类型：graph/flowchart, journey, sequenceDiagram, gantt, pie, classDiagram, stateDiagram, erDiagram

---

## 扫描版/纯图片 PDF 处理

DocWizard 通过三层策略处理扫描版 PDF：

| 层级 | 方案 | 适用场景 | 准确率 |
|------|------|----------|--------|
| 1 | **document-skills 内置 OCR**（Tesseract） | 清晰的印刷体 PDF | 80-90% |
| 2 | **MinerU Skill**（云端，零安装） | 复杂排版、公式、表格、CJK | 优秀 |
| 3 | **marker-pdf**（本地，高精度） | 离线、隐私敏感场景 | 95%+ |

层级 1 始终可用（需系统安装 `tesseract-ocr` + `poppler-utils`）。层级 2 推荐大多数学生使用，一条命令：
```bash
npx skills add Nebutra/MinerU-Skill
```

层级 3 离线环境：
```bash
pip install marker-pdf[full]
```

Agent 在预处理阶段自动检测 PDF 类型（第一页 < 50 字符判定为扫描版），选择合适层级。

---

## 压缩包处理

自动检测 `.zip`、`.rar`、`.7z` 文件并解压：

- **ZIP**：Python stdlib，始终可用
- **RAR**：需要 `unrar` 或 `7z`
- **7z**：需要 `p7zip-full`

缺失工具时会友好提示安装命令。

---

## LaTeX 编译

自动检测 `.tex` 文件并编译为 PDF。按优先级选择编译器：

| 优先级 | 编译器 | 特点 |
|--------|--------|------|
| 1 | `tectonic` | 自动下载缺失包、零配置，推荐 |
| 2 | `xelatex` | 中文支持最佳 |
| 3 | `pdflatex` | 最普遍 |

无编译器时会友好提示各平台安装命令。

---

## Typst 编译

Typst 是新一代排版系统，语法比 LaTeX 简洁，编译速度极快（增量编译），在大学生中快速流行。

```bash
# 安装（三平台）
winget install --id Typst.Typst   # Windows
brew install typst                # macOS
# Linux: 下载 https://github.com/typst/typst/releases

# 编译
typst compile paper.typ output/paper.pdf
```

`.typ` 文件是纯文本，agent 可直接阅读和理解内容。

---

## 智能场景

**压缩包里有 Word 需求文档？** 解压后自动读取 `.docx`，识别是否为作业要求，是则以此为准执行任务。

**要求提交分析代码？** 自动将分析过程中使用的 Python 代码整理为独立脚本 `analysis_script.py` 输出。

---

## 非 Claude Code / OpenCode 环境

Codex 和 Cursor 没有 `document-skills@anthropic-agent-skills` 插件。格式转换降级为 Python 库：

```bash
pip install python-docx python-pptx openpyxl pdfplumber pandas
```

| 操作 | Claude Code / OpenCode | Codex / Cursor 降级 |
|------|----------------------|---------------------|
| MD → DOCX | docx skill | pandoc 或 python-docx |
| DOCX → MD | docx skill | pandoc 或 python-docx |
| PDF → MD | pdf skill | pdfplumber / pymupdf |
| XLSX/CSV | xlsx skill | openpyxl + pandas |
| PPTX 生成 | pptx skill | python-pptx |
| Mermaid 渲染 | `helpers/render_mermaid.py` | 同左（Python stdlib） |

**Cursor 用户额外步骤**：需将 `SKILL.md` 转换为 `.cursor/rules/docwizard.mdc` 格式（添加 YAML frontmatter）。

---

## 更新

```bash
cd .agents/skills/DocWizard && git pull origin main
```

或者对你的 AI 说：

> 检查 DocWizard 有没有新版本

---

## 常见问题

| 问题 | 解决 |
|------|------|
| document-skills 插件未安装 | `/plugin install document-skills@anthropic-agent-skills` |
| DOCX 有彩色文字 | 自动执行黑体后处理 `helpers/black_text.py` |
| Mermaid 图渲染失败 | mermaid.ink 需要外网访问 |
| PDF 中文乱码 | Linux: `apt install fonts-noto-cjk` |
| RAR/7z 无法解压 | `sudo apt install unrar p7zip-full` |
| CSV 中文乱码 | 自动尝试 GBK 编码 |
| LaTeX 编译失败 | 安装 tectonic: `winget/brew/apt install tectonic` |
| .tex 中文编译报错 | 用 xelatex 替代 pdflatex，或添加 `\usepackage{ctex}` |
| Typst 编译失败 | 安装 typst: `winget/brew install typst` 或 https://github.com/typst/typst/releases |
| 扫描版 PDF 无法提取文字 | 参见[扫描版/纯图片 PDF 处理](#扫描版纯图片-pdf-处理)，推荐 `npx skills add Nebutra/MinerU-Skill` |

---

## 鸣谢

DocWizard 基于以下优秀的 Claude Code 技能和开源项目构建：

| 技能/工具 | 用途 | 来源 |
|-----------|------|------|
| `document-skills` | docx/pdf/pptx/xlsx 文档处理核心引擎 | [anthropics/skills](https://github.com/anthropics/skills) |
| `academic-research-skills` | 学术写作流程参考（规划-执行模式） | [Imbad0202](https://github.com/Imbad0202) |
| `MarkItDown` | 多格式→Markdown 转换思路参考 | [claude-scientific-writer](https://github.com/claude-scientific-writer) |
| mermaid.ink | Mermaid 图表在线渲染 | [mermaid.ink](https://mermaid.ink) |
| Pandoc | 文档转换引擎灵感来源 | [pandoc.org](https://pandoc.org) |
| MinerU | PDF→Markdown 解析方案参考 | GitHub: aliceisjustplaying |
| Docling (IBM) | 高精度表格/公式识别参考 | [DS4SD/docling](https://github.com/DS4SD/docling) |
| python-docx | Word 文档生成方案参考 | [python-docx](https://python-docx.readthedocs.io) |
| DrawIO MCP | 复杂图表绘制与导出 | MCP 集成 |
| `Typst` | 新一代排版系统（.typ → PDF） | [typst.app](https://typst.app) |
| `Typst MCP Server` | Typst 排版 MCP 集成 | MCP 生态 |
| `mcp-pandoc` | Markdown/HTML/LaTeX 转换 MCP | MCP 生态 |
| `awesome-claude-skills` | 1000+ Claude Code 技能库参考 | [ComposioHQ](https://github.com/ComposioHQ/awesome-claude-skills) |
| `CrossRef` / `Semantic Scholar` | 参考文献 DOI 验证 API | [crossref.org](https://crossref.org) |
| `refcheck` MCP | 参考文献自动验证 | MCP 生态 |
| `CheckIfExist` | 批量 BibTeX 多源验证 | GitHub 开源 |
| `VeriBib` | AI 幻觉引用检测 | GitHub 开源 |
| `tectonic` | LaTeX 编译引擎（推荐） | [tectonic-typesetting](https://github.com/tectonic-typesetting/tectonic) |
| `Pdf It` (MCP) | Markdown→专业 PDF（目录/页码/字体嵌入） | MCP 生态 |
| `skill-forge` | Skill 构建元工具 | Claude Code 官方 |
| `format-thesis` | 中文学位论文 Word 一键排版 | [lilanlan11](https://github.com/lilanlan11/format-thesis) |
| `GPT-Researcher` | 自主研究 Agent（MCP 集成） | [assafelovic](https://github.com/assafelovic/gpt-researcher) |
| `STORM` | Stanford 知识策展系统 | [stanford-oval](https://github.com/stanford-oval/storm) |
| `Slidev` | Markdown → 演示文稿 | [slidevjs](https://github.com/slidevjs/slidev) |
| `ydata-profiling` | 自动化 EDA 数据分析报告 | [ydataai](https://github.com/ydataai/ydata-profiling) |
| `office2pdf` | Rust 实现 Office→PDF（零依赖） | [developer0hye](https://github.com/developer0hye/office2pdf) |
| `Marp` | Markdown → PPTX 演示 | [marp-team](https://github.com/marp-team/marp) |
| `gpt-academic` | 中文学术 AI 助手 | [binary-husky](https://github.com/binary-husky/gpt_academic) |
| `D2` | 现代声明式图表语言 | [terrastruct](https://github.com/terrastruct/d2) |
| `Paperlib` | 开源文献管理器 | [Future-Scholars](https://github.com/Future-Scholars/paperlib) |
| `Quarto` | 科学出版系统 | [quarto-dev](https://github.com/quarto-dev/quarto-cli) |
| `Awesome Typst CN` | 中国高校 Typst 论文模板目录 | [qjcg](https://github.com/qjcg/awesome-typst) |
| `Camelot` | PDF 表格提取 | [camelot-dev](https://github.com/camelot-dev/camelot) |
| `MinerU Skill` | Claude Code 扫描 PDF OCR Skill | [Nebutra](https://github.com/Nebutra/MinerU-Skill) |
| `marker-pdf` | 本地高精度 PDF OCR+布局 | [datalab-to](https://github.com/datalab-to/marker-pdf) |

---

## License

MIT — 李裕峰