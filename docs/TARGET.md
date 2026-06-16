# TARGET — DocWizard 项目目标

## 一句话定位

**大学生作业一站式助手：从文档处理到数据分析到 PPT 生成，一句话完成。**

## 核心价值

| 维度 | 目标 |
|------|------|
| **零门槛** | `/plugin install document-skills` + `git clone DocWizard` → 一句话搞定 |
| **零依赖** | 不需要 pandoc、Chrome、Office — 纯 Claude Code Skill |
| **自动化** | Mermaid 图表渲染、压缩包解压、格式互转、数据分析、PPT 生成 |
| **高质量** | 中文学术排版优化、图表清晰嵌入、DOCX 纯黑输出、OMML 公式 |
| **跨平台** | Windows / macOS / Linux 全支持，无平台特定依赖 |

## 设计原则

1. **Agent First** — 所有功能优先为 AI agent 使用而设计（SKILL.md、task.md、结构化汇报）
2. **Delegate, Don't Implement** — 格式转换委托给 document-skills 插件，DocWizard 只做编排
3. **Zero External Deps** — helper 脚本纯 Python stdlib，不引入新依赖
4. **Fail Safe** — 黑体后处理兜底、OMML 公式降级、RAR/7z 缺失友好提示

## 目标用户

| 用户 | 场景 |
|------|------|
| 大学生 | 课程作业 Markdown → docx/pdf 提交 |
| 研究生 | 论文 / 调研报告 格式转换 + 数据分析 |
| 教师 | 课件 .md ↔ .docx ↔ .pptx 互转 |
| 数据类学生 | CSV/Excel 数据分析 → 报告生成 |
| 任何人 | 通过 AI agent 一句话完成文档处理 |

## 技术栈

```
DocWizard (Claude Code Skill)
  ├─ document-skills 插件 (转换引擎)
  │   ├─ docx skill   (python-docx, docx-js, mammoth, lxml)
  │   ├─ pdf skill    (reportlab, pypdf, pdfplumber, pytesseract)
  │   ├─ pptx skill   (python-pptx)
  │   └─ xlsx skill   (openpyxl, pandas)
  ├─ helpers/ (Python stdlib 零依赖)
  │   ├─ render_mermaid.py  (mermaid.ink API, base64+urllib)
  │   └─ black_text.py      (ZIP/XML 后处理, zipfile+re)
  └─ DrawIO MCP (复杂图表，可选)
```

## 竞品对比

| 功能 | DocWizard v3.0 | DocWizard v2.0 | 纯 pandoc | 在线转换工具 |
|------|---------------|----------------|-----------|-------------|
| AI agent 集成 | ✓ 原生 | ✓ | ✗ | ✗ |
| 零外部依赖 | ✓ | ✗ (pandoc) | ✗ | ✗ |
| Mermaid → PNG | ✓ 自动 | ✓ | ✗ | ✗ |
| 压缩包解压 | ✓ 自动 | ✗ | ✗ | ✗ |
| 中文学术格式 | ✓ 内置 | 部分 | ✗ | 部分 |
| PPT 生成 | ✓ pptx skill | ✗ | ✗ | ✗ |
| 数据分析 | ✓ xlsx skill | ✗ | ✗ | ✗ |
| DOCX 黑体 | ✓ 后处理 | ✓ | ✗ | 部分 |
| 本地离线 | ✓ | ✓ | ✓ | ✗ |