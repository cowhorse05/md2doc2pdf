# TODO — DocWizard 待办清单

## 近期 (v3.1)

- [ ] 嵌套压缩包递归解压（当前安全策略只检测不递归）
- [ ] 压缩包密码支持（提示用户输入密码后解压）
- [ ] OMML 公式保真度测试（验证 $$...$$ → OMML 转换质量）
- [ ] 更多中文学术模板（毕业论文、实验报告、课程论文）
- [ ] Windows ZIP 中文文件名编码自动修复（GBK → UTF-8）

## 中期 (v3.2+)

- [ ] 批量中文模板：选中模板 → 自动应用格式
- [ ] 内置 Mermaid 本地渲染（mermaid-cli 可选），避免 mermaid.ink 网络依赖
- [ ] PDF 目录/书签自动生成（根据标题层级）
- [ ] 并发处理多个文件（提升大型项目处理速度）
- [ ] 自定义样式配置（用户可通过配置文件覆盖默认中文格式）
- [ ] 参考文献管理集成（Zotero/Mendeley BibTeX → 格式化引用）

## 远期

- [ ] Web UI / 本地 GUI
- [ ] 一键打包：扫描目录 → 处理 → 压缩 zip → 提交
- [ ] 云端 mermaid 渲染 fallback 池（mermaid.ink / kroki / 自建）
- [ ] 支持更多格式：`.odt`、`.rtf`、`.html`、`.epub`
- [ ] CI/CD 集成：GitHub Actions 自动处理
- [ ] 多语言支持（英文文档排版 CSS）

## 已修复的 Bug

- [x] DOCX 蓝色/彩色字体 → v2.0.0 激进黑体后处理
- [x] Mermaid 在 DOCX 中显示为代码 → v1.6.0 自动渲染管线
- [x] PDF 图片路径断裂 → v1.6.0 HTML 写到源文件目录
- [x] agent 读不了 .docx/.pdf → v1.6.1 预转换策略
- [x] task.md 被 agent 修改 → v1.5.0 只读规则
- [x] pandoc/Chrome/pdftotext/LaTeX 外部依赖 → v3.0.0 纯 Skill 架构