# TARGET — DocWizard 项目目标

## 一句话定位

**大学生作业文档从 Markdown 到 Word/PDF 的一键自动化助手。**

## 核心价值

| 维度 | 目标 |
|------|------|
| **零门槛** | 一句话 `帮我安装 DocWizard` → AI agent 自动处理一切 |
| **自动化** | Mermaid 图表自动渲染、DOCX 字体自动纯黑、格式互转自动完成 |
| **高质量** | 中文排版优化、图表清晰嵌入、DOCX 黑体干净输出 |
| **跨平台** | Windows / macOS / Linux 全支持，pandoc + 浏览器引擎 |

## 设计原则

1. **Agent First** — 所有功能优先为 AI agent 使用而设计（SKILL.md、task.md、结构化汇报）
2. **Progressive Enhancement** — 核心功能零依赖（pandoc 除外），高级功能可选安装
3. **Fail Safe** — 每一个环节都有兜底：reference.docx + 后处理双重黑体保障
4. **Read-Only Task** — task.md 是用户的任务指令，agent 只读不写

## 目标用户

| 用户 | 场景 |
|------|------|
| 大学生 | 课程作业 Markdown → docx/pdf 提交 |
| 研究生 | 论文 / 调研报告 格式转换 |
| 教师 | 课件 .md ↔ .docx 互转 |
| 任何人 | 通过 AI agent 一句话完成文档处理 |

## 技术栈

```
Python 3.7+  (主逻辑)
  ├─ pandoc        (格式互转引擎)
  ├─ mermaid.ink   (图表渲染 API)
  ├─ Chrome/Edge   (HTML → PDF 渲染)
  ├─ pdftotext     (PDF → 文本提取，可选)
  ├─ LaTeX         (.tex 编译，可选)
  └─ DrawIO MCP    (复杂图表，可选)
```

## 竞品对比

| 功能 | DocWizard | 纯 pandoc | 在线转换工具 |
|------|-----------|-----------|-------------|
| AI agent 集成 | ✓ | ✗ | ✗ |
| Mermaid → PNG | ✓ 自动 | ✗ | ✗ |
| DOCX 黑体 | ✓ 双重保障 | ✗ | 部分 |
| 可选依赖安装 | ✓ 交互向导 | ✗ | ✗ |
| 预转换读取 | ✓ .docx→.md | ✗ | ✗ |
| 本地离线 | ✓ | ✓ | ✗ |
