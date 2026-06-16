# CHANGELOG

## v3.0.0 (2026-06-16) — 纯 Claude Code Skill 架构

### 架构重构
- **移除所有外部依赖**：不再需要 pandoc、Chrome/Edge、pdftotext、LaTeX
- **转为纯 Claude Code Skill**：所有格式转换委托给 `document-skills@anthropic-agent-skills` 插件
- `md2docx_pdf.py` 拆分为两个零依赖 helper 脚本：`helpers/render_mermaid.py` + `helpers/black_text.py`
- 删除 `test_converter.py`（27 项 pandoc 依赖测试），新建 `test_helpers.py`

### 新增
- **压缩包解压**：自动检测 .zip/.rar/.7z 并解压，处理其中文档
- **中文学术格式规范**：A4/宋体/黑体/1.5倍行距/三线表/OMML 公式/标题自动编号
- **PPT 生成**：Markdown → PPTX 演示文稿（委托 pptx skill）
- **数据分析**：CSV/XLSX 读取 → 分析 → 报告生成（委托 xlsx skill）
- **代码块语法高亮保留**：转换时保留代码块格式
- **$$...$$ 公式 → OMML**：LaTeX 公式转为可编辑的 Office Math Markup Language

### 删除
- `md2docx_pdf.py`（1245 行，所有 pandoc/Chrome/pdftotext/LaTeX 依赖）
- `test_converter.py`（27 项 pandoc 依赖测试）
- `--setup` 安装向导（不再需要安装外部依赖）
- `--update` 自更新命令（改为 git pull）

### 文档
- SKILL.md 完全重写：7 阶段流水线 + document-skills 委托协议
- README.md 重写：零外部依赖 + 新功能说明
- skill.json 大幅精简：移除 dependency checks，新增 archive/chinese_formatting/delegation 配置节
- task.md 更新：新增压缩包和数据分析选项

---

## v2.0.0 (2026-06-16) — DocWizard 正式命名

### 重命名
- 项目名 `md2docx-pdf` → **DocWizard**
- 仓库 `github.com/cowhorse05/md2doc2pdf` → `github.com/cowhorse05/DocWizard`

### 修复
- **DOCX 蓝色/彩色字体彻底解决**：后处理覆盖所有 XML 文件 + theme1.xml 主题色 + 激进 hex 替换

---

## v1.6.1 (2026-06-16)

### 新增
- **预转换策略**：agent 扫描到 .docx/.pdf 文件时，先 pandoc/pdftotext 转 .md 再读内容

---

## v1.6.0 (2026-06-16) — 图表渲染管线

### 新增
- **Mermaid → PNG 渲染**：mermaid.ink API 在线渲染，零依赖
- `--render-mermaid` / `--no-render-mermaid` CLI 参数

---

## v1.5.0 (2026-06-15~16) — 交互式安装 + 自动执行

### 新增
- `--setup` / `--install`：交互式设置向导
- `--update`：git pull 自动更新
- `SKILL.md`：Agent 操作手册

---

## v1.4.0 (2026-06-15)

### 新增
- 交互式设置向导 `--setup` 基础版本

---

## v1.3.0 (2026-06-13)

### 初始版本
- `.md` / `.docx` / `.pdf` 三向互转
- pandoc + Chrome/Edge 浏览器 PDF 渲染
- LaTeX .tex 编译（可选）
- 中文排版 CSS