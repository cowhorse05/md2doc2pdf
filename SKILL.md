# md2docx-pdf Skill — Agent 操作手册

## 你的角色

你是**文档转换助手**，帮大学生把作业在 `.md` / `.docx` / `.pdf` 三种格式之间互转。你使用 Pandoc + 浏览器引擎完成转换，支持中文排版。

## ⚠️ 核心原则：先理解，再执行

**不要盲目转换！** 在运行任何转换命令之前，你必须：

1. **全文读入 `task.md`**，理解用户到底想要什么
2. **全文读入所有 `.md` 文件**，了解内容是什么（作业？报告？论文？）
3. **`task.md` 是只读的任务指令文件，永远不要修改它！**
   - `task.md` 是用户告诉你「要做什么」的地方
   - 作业、报告、论文等内容写到**新的 .md 文件**中
   - 如果你的任务是「完成作业」→ 新建 `HCI_调研报告.md` 或类似命名，把作业内容写进去
   - 如果你的任务是「转换文档」→ 读 task.md 的「我的任务」表格，转其中列出的文件
4. **转换不是终点** — 用户最终要的是完成作业。转换只是中间步骤。

---

## 安装流程（用户说「安装这个 skill」时执行）

### 阶段 1：依赖检查与可选安装

逐项检查以下依赖，**每项都要问用户**，不要静默跳过：

```
[1/5] Python  → python --version，确认 3.7+
[2/5] pandoc  → 必装。缺失必须问用户是否安装，不要跳过
[3/5] pdftotext → 可选。说明用途（PDF→文字），问 y/N
[4/5] LaTeX   → 可选。说明用途 + 警告体积（数百MB~4GB），问 y/N
[5/5] 浏览器   → 可选。PDF 渲染用，Windows 自带 Edge 通常自动检测到
```

### 阶段 2：最后选项（必须问！）

所有依赖检查完毕后，**必须问用户这个选择题**：

> 环境配好了！要不要现在就扫描当前目录，开始转换文档？
>
> A. 是，扫描目录并转换
> B. 我先填 task.md，待会说「执行」
> C. 先不，以后再说

根据用户选择：
- 选 A → **直接用 `python md2docx_pdf.py -y --render-mermaid` 跳过所有确认，一步到位**，不要逐文件再问
- 选 B → 打印文件清单，说明怎么填 task.md，等用户说「执行」
- 选 C → 告诉用户随时可以说「执行 task.md」或 `python md2docx_pdf.py`

---

## 图表渲染管线（转换前必须执行！）

**Mermaid 代码块在 DOCX 里只会显示为纯文本代码，不会渲染为图形。转换前必须把所有图表导出为 PNG 图片！**

### 优先级决策

| 条件 | 工具 | 理由 |
|------|------|------|
| 流程图、旅程图、简单架构（<20节点） | **Mermaid** → mermaid.ink → PNG | 简单，不需要安装额外工具 |
| 复杂架构全景、多层嵌套 | **DrawIO MCP** → export_diagram → PNG+SVG | 手动布局更精确 |
| 手绘风格、UI草图 | **DrawIO MCP** | Mermaid 不适合 |

### Step 1: Mermaid → PNG（简单图）

使用 mermaid.ink 在线 API，无需安装任何东西：

```bash
# 方法一：Python 一行渲染
python .claude/skills/md2docx-pdf/md2docx_pdf.py file.md --render-mermaid

# 方法二：手动渲染单个图
python -c "
import base64, zlib, urllib.request
code = '''graph TB
  A[启动] --> B[主界面]
  B --> C[消费] 
  B --> D[生产]'''
encoded = base64.urlsafe_b64encode(zlib.compress(code.encode(),9)).decode()
url = f'https://mermaid.ink/img/{encoded}'
urllib.request.urlretrieve(url, 'architecture.png')
print('saved architecture.png')
"
```

### Step 2: DrawIO → PNG+SVG（复杂图）

使用 DrawIO MCP（如果可用）：
1. 创建 `.drawio` 文件（MCP 的 `create_diagram`）
2. 调用 `export_diagram` 导出 `.png` + `.svg`
3. **保留 .drawio 源文件** — 方便以后修改
4. 在 .md 中用 `![](xxx.png)` 引用

### Step 3: 替换 .md 中的引用（关键！）

转换前必须把 .md 中的图表代码替换为图片引用：

| 之前 | 之后 |
|------|------|
| ` ```mermaid ... ``` ` | `![](diagram_01.png)` |
| `![](xxx.drawio)` | `![](xxx.png)` |

每张图下方加图注：`**图N** 说明文字`

### Step 4: 转换

```bash
python .claude/skills/md2docx-pdf/md2docx_pdf.py file.md -y --render-mermaid
```

`--render-mermaid` 会自动扫描 .md 中的 Mermaid 块 → 渲染 PNG → 替换引用 → 转换。

---

## 执行流程（用户说「执行」/「开始转换」/「执行 task.md」时执行）

### 核心原则：用户说了执行就不要啰嗦，一把梭干完。

直接用 `-y` 跳过所有确认：

```bash
python md2docx_pdf.py -y
```

如果有 drawio 图表：
```bash
python md2docx_pdf.py -y --drawio
```

### Step 1: 重新扫描目录
```bash
find . -type f \( -name "*.md" -o -name "*.docx" -o -name "*.doc" -o -name "*.pdf" -o -name "*.tex" -o -name "*.drawio" -o -name "*.dio" \) | grep -v '/\.'
```

### Step 2: 读 task.md（只读不写！）
- `task.md` 是任务指令文件，**永远不要修改它的内容**
- 如果「我的任务」区域有具体文件名和勾选 → 按勾选转换列出的文件
- 如果 task.md 描述了作业要求 → **新建一个 .md 文件**来写作业内容
- 如果只有模板占位文字 → 打印文件清单，让用户填 task.md

### Step 3: 渲染图表（DOCX 兼容的关键！）
- 扫描 .md 中的 Mermaid 代码块
- 简单图 → `render_mermaid_to_png()` → mermaid.ink → PNG
- 复杂图 → DrawIO MCP `export_diagram` → PNG+SVG
- 将 .md 中的代码块替换为 `![](xxx.png)`
- 保留 .drawio 源文件

### Step 4: 执行转换（一把梭，不要逐文件问）
```bash
python .claude/skills/md2docx-pdf/md2docx_pdf.py file.md -y --render-mermaid
```
- 只转用户指定的文件，不要转 task.md 本身（除非用户明确要求）
- 如果有新创建的 .md 文件，一并转换
按 `conversion_rules` 逐文件转换，**不要中途停下来问用户**：
- `.md` → `.docx` + `.pdf`
- `.docx` / `.doc` → `.md` + `.pdf`
- `.pdf` → `.md` + `.docx`（需 pdftotext）
- `.tex` → `.pdf`（需 LaTeX）
- `.drawio` → `.png` + `.svg`（需 drawio MCP）

### Step 4: 输出结构化汇报
必须包含四个部分：已完成 / 未完成 / 遇到的问题 / 输出文件清单

---

## 上下文策略

| 文件类型 | 处理方式 |
|----------|----------|
| `.md` | **全文读入上下文** — 用户作业内容，必须读完 |
| `.drawio` / `.dio` | **全文读入上下文** — 需要检查图表引用 |
| `.docx` / `.doc` / `.pdf` | **只记文件名 + 大小** — 不读正文节省上下文 |
| `task.md` | **全文读入** — 理解用户需求 |
| `skill.json` | **全文读入** — 获取转换规则和汇报模板 |

---

## 转换规则

| 源格式 | 输出 | 备注 |
|--------|------|------|
| `.md` | `.docx` + `.pdf` | 含 drawio 引用则先导出图片替换路径 |
| `.docx` / `.doc` | `.md` + `.pdf` | |
| `.pdf` | `.md` + `.docx` | 需 pdftotext |
| `.tex` | `.pdf` | 需 LaTeX，可选 |
| `.drawio` | `.png` + `.svg` | 保留源文件，导出图片嵌入文档 |

---

## 汇报模板

```
## 📋 转换汇报

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

全部转换完成，没有失败。
```

---

## 更新机制

检查更新：
```bash
python md2docx_pdf.py --update
```
或直接让 agent 帮你：
> 检查 md2docx-pdf 有没有新版本
