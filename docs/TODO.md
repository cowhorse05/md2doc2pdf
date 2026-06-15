# TODO — DocWizard 待办清单

## 近期 (v2.1)

- [ ] 支持多文件批量处理时保持目录结构
- [ ] `.drawio` 文件自动检测并调 MCP 导出（当前需手动 `--drawio`）
- [ ] DOCX 输出可自定义页边距、页眉页脚
- [ ] 表格样式可配置（斑马纹、边框粗细）

## 中期 (v2.2+)

- [ ] 内置 Mermaid 本地渲染（mermaid-cli 可选依赖），避免 mermaid.ink 网络依赖
- [ ] `.md` 中的 `![](xxx.drawio)` 引用自动替换为渲染后的 PNG
- [ ] PDF 目录/书签自动生成（根据标题层级）
- [ ] 多语言支持（英文文档排版 CSS）
- [ ] 并发转换多个文件

## 远期

- [ ] Web UI / 本地 GUI
- [ ] 一键打包：扫描目录 → 转换 → 压缩 zip → 提交
- [ ] 云端 mermaid 渲染 fallback 池（mermaid.ink / kroki / 自建）
- [ ] 支持更多格式：`.odt`、`.rtf`、`.html`
- [ ] CI/CD 集成：GitHub Actions 自动转换

## 已修复的 Bug

- [x] DOCX 蓝色/彩色字体 → v2.0.0 激进黑体后处理
- [x] Mermaid 在 DOCX 中显示为代码 → v1.6.0 自动渲染管线
- [x] PDF 图片路径断裂 → v1.6.0 HTML 写到源文件目录
- [x] agent 读不了 .docx/.pdf → v1.6.1 预转换策略
- [x] task.md 被 agent 修改 → v1.5.0 只读规则
