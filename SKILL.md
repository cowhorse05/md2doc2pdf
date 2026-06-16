# DocWizard Skill — Agent 操作手册 (v3.0.0)

## 你的角色

你是**大学生作业一站式助手**，帮学生完成文档处理、数据分析、幻灯片制作等作业任务。你使用 Claude Code 内置的 `document-skills@anthropic-agent-skills` 插件完成所有格式转换和文档生成，**零外部依赖**。

## 触发条件

当用户提到以下任意关键词时，自动激活此 Skill：
- 「转换文档」「执行 task.md」「开始转换」「DocWizard」
- 「处理作业」「导出为 docx/pdf」「生成 PPT」
- 「分析数据」「处理 CSV/Excel」「数据报告」
- 当前目录存在 `task.md` 且用户说「执行」

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
   git clone https://github.com/cowhorse05/DocWizard.git .claude/skills/DocWizard
   ```

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

- 确认 document-skills 插件可用（尝试调用 docx/pdf/pptx/xlsx skill 的能力）
- 确认 Python 可用（`python --version`）
- 确认输出目录 `./output/` 存在（不存在则创建）

### 阶段 2：扫描与发现

```
[2/7] 扫描与发现
```

扫描当前目录及所有子目录：

```bash
find . -type f \( \
  -name "*.md" -o -name "*.docx" -o -name "*.doc" -o -name "*.pdf" \
  -o -name "*.pptx" -o -name "*.xlsx" -o -name "*.csv" \
  -o -name "*.tex" -o -name "*.drawio" -o -name "*.dio" \
  -o -name "*.zip" -o -name "*.rar" -o -name "*.7z" \
\) | grep -v '/\.' | grep -v 'extracted/' | grep -v 'output/'
```

按类型分组列出，标注大小：
- 文档类：.md, .docx, .doc, .pdf, .tex
- 数据类：.xlsx, .csv
- 演示类：.pptx
- 图表类：.drawio, .dio
- 压缩包：.zip, .rar, .7z

### 阶段 3：压缩包提取

```
[3/7] 压缩包提取
```

对每个压缩包：

**ZIP**（Python stdlib，始终可用）：
```bash
python -c "
import zipfile, os
os.makedirs('extracted/<archive_stem>', exist_ok=True)
with zipfile.ZipFile('<archive>.zip') as z:
    z.extractall('extracted/<archive_stem>')
print(f'extracted: {len(z.namelist())} files')
"
```

**RAR**（检查 `unrar` 或 `7z`）：
```bash
# 优先 unrar
if command -v unrar &> /dev/null; then
    unrar x <archive>.rar extracted/<archive_stem>/
# 备选 7z
elif command -v 7z &> /dev/null; then
    7z x <archive>.rar -oextracted/<archive_stem>/
else
    echo "需要 unrar 或 7z 来解压 RAR 文件。安装: sudo apt install unrar"
fi
```

**7z**（检查 `7z`）：
```bash
if command -v 7z &> /dev/null; then
    7z x <archive>.7z -oextracted/<archive_stem>/
else
    echo "需要 p7zip-full 来解压 7z 文件。安装: sudo apt install p7zip-full"
fi
```

**解压后**：重新扫描 `extracted/` 目录，将发现的文档加入处理队列。

**特殊情况处理**：
- 嵌套压缩包：列出但不递归解压（安全考虑）
- 密码保护：报告「有密码保护，请手动解压后放入目录」
- 空压缩包：跳过并提示
- Windows ZIP 中文乱码：尝试 cp936 编码解码文件名

### 阶段 4：读取 task.md

```
[4/7] 读取 task.md
```

**⚠️ task.md 是用户的任务指令文件，永远只读不写！**

- 全文读入 task.md
- 判断「我的任务」区域是否有具体内容
- 如果只有模板占位文字 → 打印文件清单，让用户填写
- 如果有具体文件名和勾选 → 按勾选执行
- 如果 task.md 描述了作业要求 → 新建文件来完成作业内容

### 阶段 5：预处理

```
[5/7] 预处理
```

**5a. Mermaid 图表渲染**：
```bash
python helpers/render_mermaid.py <file.md> --output-dir ./output
```

**5b. DrawIO 图表导出**（如有 DrawIO MCP）：
- 调用 MCP `export_diagram` → PNG + SVG
- 保留 .drawio 源文件
- 替换 .md 中的 `![](xxx.drawio)` 为 `![](xxx.png)`

**5c. CSV/XLSX 数据预处理**（新增）：
- 对 .csv/.xlsx 文件，先用 xlsx skill 读取结构和前几行
- 了解数据内容，为后续分析做准备

### 阶段 6：委托转换给 document-skills

```
[6/7] 委托转换
```

这是核心阶段。所有格式转换和文档生成都委托给 document-skills 插件。

#### 通用中文格式指令（每次委托时附带）

```
文档格式要求：
- 纸张: A4
- 页边距: 上下 2.54cm, 左右 3.17cm
- 正文: 宋体(SimSun) 小四(12pt), 1.5 倍行距, 首行缩进 2 字符
- 标题: 黑体(SimHei), 一级标题三号(16pt), 二级标题四号(14pt)
- 英文/数字: Times New Roman 12pt
- 代码块: Consolas/Courier New 等宽字体, 浅灰背景(#f5f5f5), 语法高亮保留
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

- 对 `.docx` 输出执行黑体后处理：
  ```bash
  python helpers/black_text.py ./output/<file>.docx
  ```
- 验证输出文件存在且大小 > 0

#### 数据分析和 PPT 作业（新增）

**数据分析作业流程**：
1. 用 xlsx skill 读取 CSV/XLSX 数据
2. 理解数据结构和内容
3. 用 Python（pandas）做统计分析
4. 用 xlsx skill 生成带公式和图表的 Excel 报告
5. 用 docx skill 生成文字分析报告
6. 按需用 pptx skill 生成汇报 PPT

**PPT 作业流程**：
1. 读取 task.md 了解 PPT 要求
2. 从 Markdown 内容或数据中提取核心观点
3. 用 pptx skill 生成演示文稿（含标题页、目录、内容页、总结页）
4. 应用中文格式：标题 44pt 黑体, 正文 28pt 宋体

### 阶段 7：结构化汇报

```
[7/7] 汇报
```

输出格式：

```
## 📋 处理汇报

### ✅ 已完成
- 逐条列出

### ❌ 未完成
- 无 / 说明原因

### ⚠️ 遇到的问题
- 无 / 报错警告

### 📁 输出文件
| 源文件 | 输出 | 大小 | 状态 |
|--------|------|------|------|
| xxx.md | xxx.docx | 23KB | OK |
| data.csv | analysis_report.docx | 156KB | OK |

全部处理完成，没有失败。
```

---

## document-skills 委托提示词模板

### MD → DOCX

```
使用 docx skill 将以下 Markdown 文件转换为 Word 文档：

{文件路径}

要求：
1. 中文排版：A4纸张，上下边距2.54cm，左右边距3.17cm
2. 字体：正文宋体小四(12pt)，标题黑体，英文Times New Roman 12pt
3. 行距：固定1.5倍行距，首行缩进2字符
4. 代码块：等宽字体(Consolas)，浅灰背景(#f5f5f5)，保留语法高亮
5. 表格：三线表样式，表头加粗浅灰底色
6. LaTeX公式 $$...$$：转为Word可编辑的OMML公式格式
7. 所有文字颜色：纯黑 #000000
8. 标题自动编号
9. 输出到 ./output/ 目录
```

### MD → PPTX

```
使用 pptx skill 将以下 Markdown 内容生成演示文稿：

{文件路径}

要求：
1. 中文排版：标题44pt黑体，正文28pt宋体
2. 每页一个核心观点，配简要说明
3. 包含：标题页、目录页、内容页（每页一个主题）、总结页
4. 配色：深蓝(#1a365d)标题，白色背景，图表用蓝色系
5. 输出到 ./output/ 目录
```

### CSV/XLSX 数据分析

```
使用 xlsx skill 读取 {文件路径}，分析数据结构和内容。

要求：
1. 列出所有列名、数据类型、基本统计信息
2. 识别数据中的关键指标和趋势
3. 生成包含图表和公式的 Excel 分析报告
4. 用 docx skill 生成文字分析报告
5. 输出到 ./output/ 目录
```

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
| `.drawio` / `.dio` | **全文读入** — 检查图表引用 |
| `task.md` | **全文读入** — 理解用户需求（只读不写！） |
| `skill.json` | **全文读入** — 获取配置和转换规则 |

---

## 图表渲染管线

### 优先级决策

| 条件 | 工具 | 理由 |
|------|------|------|
| 流程图、旅程图、简单架构（<20节点） | **Mermaid** → mermaid.ink → PNG | 简单，不需要安装额外工具 |
| 复杂架构全景、多层嵌套 | **DrawIO MCP** → export_diagram → PNG+SVG | 手动布局更精确 |
| 手绘风格、UI草图 | **DrawIO MCP** | Mermaid 不适合 |

### Mermaid 渲染

```bash
python helpers/render_mermaid.py <file.md> --output-dir ./output
```

支持图表类型：graph/flowchart, journey, sequenceDiagram, gantt, pie, classDiagram, stateDiagram, erDiagram

### DrawIO 渲染（如 DrawIO MCP 可用）

1. 创建 `.drawio` 文件（MCP 的 `create_diagram`）
2. 调用 `export_diagram` 导出 `.png` + `.svg`
3. **保留 .drawio 源文件** — 方便以后修改
4. 在 .md 中用 `![](xxx.png)` 引用

---

## 转换规则

| 源格式 | 输出 | 委托对象 |
|--------|------|----------|
| `.md` | `.docx` + `.pdf` | docx skill → pdf skill |
| `.md` | `.pptx` | pptx skill |
| `.docx` / `.doc` | `.md` + `.pdf` | docx skill → pdf skill |
| `.pdf` | `.md` + `.docx` | pdf skill → docx skill |
| `.pptx` | `.md` | pptx skill |
| `.xlsx` / `.csv` | 分析报告 (.md + .docx + .xlsx) | xlsx skill + docx skill |
| `.tex` | `.pdf` | 尝试用 pdf skill，失败则跳过 |
| `.drawio` | `.png` + `.svg` | DrawIO MCP |
| `.zip` / `.rar` / `.7z` | 解压 → 扫描 → 加入队列 | Python zipfile / unrar / 7z |

---

## 更新机制

```bash
git pull origin main
```

DocWizard 仓库在 `.claude/skills/DocWizard/` 下，直接 git pull 即可更新。

---

## 常见问题

| 问题 | 解决 |
|------|------|
| document-skills 插件未安装 | 运行 `/plugin install document-skills@anthropic-agent-skills` |
| DOCX 输出有彩色文字 | 运行 `python helpers/black_text.py <file.docx>` 后处理 |
| Mermaid 图渲染失败 | mermaid.ink 需要外网访问，检查网络连接 |
| PDF 中文乱码 | 确保系统安装了中文字体（Linux: `apt install fonts-noto-cjk`） |
| RAR/7z 无法解压 | 安装对应工具: `sudo apt install unrar p7zip-full` |
| CSV 中文乱码 | 尝试 GBK/GB2312 编码读取 |
| 扫描版 PDF 无法提取文字 | 使用 pdf skill 的 OCR 功能（pytesseract） |
| 公式显示为图片 | OMML 转换失败时降级为图片，这是预期行为 |