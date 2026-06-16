# DocWizard Demo 示例

三个典型的大学生作业场景，帮助快速上手。

## 场景一：课程论文

**文件**：`paper.md`（含 Mermaid 架构图 + LaTeX 公式）+ `references.bib`（5条真实 DOI）+ `task.md`

**任务**：Markdown → DOCX + PDF，Mermaid 图表渲染，参考文献格式化 (GB/T 7714) + DOI 验证

**一句搞定**：在此目录下对你的 AI 说 `执行 task.md`

**预期产物**：`论文.docx` + `论文.pdf`（含图表 + 格式化参考文献 + DOI 验证报告）

## 场景二：实验报告

**文件**：`实验报告.md`（含 LaTeX 公式）+ `实验数据.csv`（60 行 I-V 特性测量数据）+ `task.md`

**任务**：报告转换 + 数据分析（I-V/P-V 曲线）+ 生成 PPT 汇报（可选）

**一句搞定**：在此目录下对你的 AI 说 `执行 task.md`

**预期产物**：`实验报告.docx` + `实验报告.pdf` + （可选）`实验汇报.pptx`

## 场景三：压缩包作业

**文件**：`sales_data.csv`（30 行 Q1 销售数据）+ `作业要求.md`（Word 需求文档）+ `task.md`

**任务**：解压 → 读取要求 → 数据分析 → 输出代码 + 报告（docx + pdf）

**一句搞定**：在此目录下对你的 AI 说 `执行 task.md`

**预期产物**：`analysis_script.py` + `分析报告.docx` + `分析报告.pdf`

> 💡 实际场景中，老师会发 .zip 压缩包。将压缩包放入此目录即可，DocWizard 自动解压并读取其中的 Word 需求文档。