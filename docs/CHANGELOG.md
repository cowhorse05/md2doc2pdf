# CHANGELOG

## v2.0.0 (2026-06-16) — DocWizard 正式命名

### 重命名
- 项目名 `md2docx-pdf` → **DocWizard**
- 仓库 `github.com/cowhorse05/md2doc2pdf` → `github.com/cowhorse05/DocWizard`
- Skill 目录 `.claude/skills/md2docx-pdf` → `.claude/skills/DocWizard`

### 修复
- **DOCX 蓝色/彩色字体彻底解决**：后处理覆盖所有 XML 文件 + theme1.xml 主题色 + 激进 hex 替换
- 超链接、标题、正文全部强制纯黑

### 文档
- README 全面重写：图表渲染、黑体策略、设置向导 v2.0
- 新增 `docs/` 目录：TODO / TARGET / CHANGELOG

---

## v1.6.1 (2026-06-16)

### 新增
- **预转换策略**：agent 扫描到 .docx/.pdf 文件时，先 pandoc/pdftotext 转 .md 再读内容
- SKILL.md 上下文策略从"只记文件名"改为"先转 .md 再读"

### 文档
- SKILL.md 新增 Step 1.5：预转换不可读文件
- skill.json context_rules 全面更新

---

## v1.6.0 (2026-06-16) — 图表渲染管线

### 新增
- **`render_mermaid_to_png()`**：mermaid.ink API 在线渲染，零依赖
- **`extract_mermaid_blocks()`**：扫描 .md 中的所有 Mermaid 代码块
- **`render_all_mermaid_in_md()`**：批量渲染 + 替换 `![](xxx.png)` 引用
- **`--render-mermaid`** CLI 参数
- Mermaid 自动检测：检测到代码块自动渲染，无需手动参数
- `--no-render-mermaid` 禁用自动渲染

### 修复
- mermaid.ink 返回 403 → 添加 User-Agent header
- `any_to_pdf()` HTML 在系统临时目录导致图片相对路径断裂 → HTML 写到源文件同目录

### 文档
- SKILL.md 新增「图表渲染管线」完整章节
- skill.json 新增 `diagram_pipeline` 配置节

---

## v1.5.0 (2026-06-15~16) — 交互式安装 + 自动执行

### 新增
- **`--setup` / `--install`**：交互式设置向导，5 步可选依赖安装
- **第 6 步「最后选项」**：安装后问用户"要不要现在扫描目录开始转换?"
- **`--update` / `--upgrade`**：git pull 自动更新
- **`SKILL.md`**：Agent 操作手册，上下文注入入口
- **`auto_scan`**：选 A 后自动加 `-y`，一把梭不逐文件确认
- **`task.md` 只读规则**：task.md 是用户任务指令，agent 永远不修改
- 配置持久化：`.md2pdf_setup.json`

### 修复
- **DOCX 黑色字体 BUG**：`_ensure_reference_docx()` rPrDefault 注入逻辑修复
- **`_force_black_text_in_docx()`**：后处理函数，双重保障
- themeColor/themeShade/themeTint 清除
- 文件被 Word 锁住时降级写到 `_black.docx`

### 文档
- SKILL.md 新增「核心原则：先理解，再执行」
- README 新增设置向导章节

---

## v1.4.0 (2026-06-15)

### 新增
- 交互式设置向导 `--setup` 基础版本
- 5 步依赖检查（Python / pandoc / pdftotext / LaTeX / 浏览器）
- 可选组件安装提示（每个缺失都问 y/N）

---

## v1.3.0 (2026-06-13)

### 初始版本
- `.md` / `.docx` / `.pdf` 三向互转
- pandoc + Chrome/Edge 浏览器 PDF 渲染
- pdftotext PDF 文字提取
- LaTeX .tex 编译（可选）
- 中文排版 CSS
- 参考模板 reference.docx
- 扫描目录交互模式
- `-y` 跳过确认自动转换
- `-f` 单格式输出
- `--drawio` 图表导出支持
- `task.md` 任务模板
