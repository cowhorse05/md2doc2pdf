# DocWizard

> AI-powered one-stop homework assistant. One sentence — document processing, data analysis, slide generation, all done automatically. Zero external dependencies, powered by Claude Code's built-in `document-skills`.

**v3.1.0** — Multi-harness support (Claude Code / OpenCode / Codex / Cursor) + streamlined content.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)](https://github.com/cowhorse05/DocWizard)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

[中文文档](README.zh.md)

---

## Quick Start

### 1. Install the document-skills plugin (Claude Code / OpenCode)

```bash
/plugin install document-skills@anthropic-agent-skills
```

This single plugin includes four skills: docx, pdf, pptx, xlsx. **Claude Code and OpenCode only.** Codex / Cursor users see [fallback guide](#non-claude-code--opencode-environments).

### 2. Clone DocWizard

```bash
# Recommended: cross-harness universal path
git clone https://github.com/cowhorse05/DocWizard.git .agents/skills/DocWizard

# Or per harness:
# Claude Code:  .claude/skills/DocWizard
# OpenCode:     .claude/skills/DocWizard (compatible) or .opencode/skills/DocWizard
# Codex:        .codex/skills/DocWizard or .agents/skills/DocWizard
# Cursor:       Convert to .cursor/rules/docwizard.mdc format
```

### 3. One Sentence

Send this to your AI coding assistant:

> Install DocWizard skill for me

The AI will automatically:
1. Detect your harness (Claude Code / OpenCode / Codex / Cursor)
2. Check document-skills plugin availability (auto-fallback to Python libraries on degraded environments)
3. Scan the directory for documents, data, and archives
4. Execute per `task.md` checkboxes
5. Output a structured report

### Or just say:

> Execute task.md

---

## Supported File Types

| Source | Output | Notes |
|--------|--------|-------|
| `.md` | `.docx` + `.pdf` | Mermaid diagrams auto-rendered as PNG |
| `.md` | `.pptx` | Markdown content → presentation slides |
| `.docx` / `.doc` | `.md` + `.pdf` | Extract text for AI reading |
| `.pdf` | `.md` + `.docx` | Text + table extraction (OCR fallback for scanned PDFs) |
| `.pptx` | `.md` | Extract slide text content |
| `.xlsx` / `.csv` | Analysis report (.md + .docx + .xlsx) | Data analysis + charts + report |
| `.drawio` | `.png` + `.svg` | Diagram export for embedding |
| `.tex` | `.pdf` | Auto-detect compiler (tectonic/xelatex/pdflatex) |
| `.typ` | `.pdf` + `.png` | Typst — next-gen typesetting, incremental compilation |
| `.zip` / `.rar` / `.7z` | Auto-extract → process contents | Smart detection of assignment requirements in archives |

---

## Chinese Academic Formatting

All document output automatically applies:

- **Paper**: A4
- **Margins**: top/bottom 2.54cm, left/right 3.17cm
- **Body**: SimSun (宋体) 12pt, 1.5× line spacing, 2-char first-line indent
- **Headings**: SimHei (黑体), Level 1: 16pt, Level 2: 14pt, auto-numbered
- **English/Numerals**: Times New Roman 12pt
- **Code blocks**: Monospace font, light gray background (#f5f5f5), syntax highlighting preserved
- **Tables**: Three-line table style (academic convention), bold centered headers
- **Formulas**: `$$...$$` → editable OMML format (falls back to images on failure)
- **Text color**: Pure black (#000000)

Font names are platform-aware (SimSun/SimHei on Windows, Songti SC/Heiti SC on macOS, Noto CJK on Linux).

---

## Diagram Rendering

Mermaid code blocks cannot render in DOCX. DocWizard auto-detects Mermaid blocks in `.md` files, renders them via mermaid.ink as PNG, and embeds them in the output document.

Supported types: graph/flowchart, journey, sequenceDiagram, gantt, pie, classDiagram, stateDiagram, erDiagram

---

## Scanned & Image-Based PDFs

DocWizard handles scanned/image-based PDFs through a tiered strategy:

| Tier | Method | Best For | Accuracy |
|------|--------|----------|----------|
| 1 | **document-skills built-in OCR** (Tesseract) | Clean printed text PDFs | 80-90% |
| 2 | **MinerU Skill** (cloud, zero-install) | Complex layouts, formulas, tables, CJK | Excellent |
| 3 | **marker-pdf** (local, high accuracy) | Offline, privacy-sensitive documents | 95%+ |

**Tier 1** is always available (requires `tesseract-ocr` + `poppler-utils` system packages). **Tier 2** is recommended for most student use — one command install:
```bash
npx skills add Nebutra/MinerU-Skill
```

**Tier 3** for offline/private use:
```bash
pip install marker-pdf[full]
```

The agent auto-detects PDF type in Stage 5 (preprocessing) and selects the appropriate tier. If the first page has < 50 characters of extractable text, the PDF is treated as scanned.

---

## Archive Extraction

Auto-detects `.zip`, `.rar`, `.7z` files and extracts:

- **ZIP**: Python stdlib, always available (auto-handles Windows GBK filename encoding)
- **RAR**: Requires `unrar` or `7z`
- **7z**: Requires `p7zip-full`

Missing tools get friendly install prompts per platform.

---

## LaTeX Compilation

Auto-detects `.tex` files and compiles to PDF. Compiler priority:

| Priority | Compiler | Strength |
|----------|----------|----------|
| 1 | `tectonic` | Auto-downloads missing packages, zero-config |
| 2 | `xelatex` | Best Chinese support |
| 3 | `pdflatex` | Most ubiquitous |

Friendly install prompts when no compiler is found.

---

## Typst Compilation

Typst is a next-generation typesetting system with simpler syntax than LaTeX and blazing-fast incremental compilation. Rapidly gaining popularity among students.

```bash
# Install (all platforms)
winget install --id Typst.Typst   # Windows
brew install typst                # macOS
# Linux: download from https://github.com/typst/typst/releases

# Compile
typst compile paper.typ output/paper.pdf
```

`.typ` files are plain text — the agent can read and understand them directly.

---

## Smart Scenarios

**Word requirement doc inside a ZIP?** Auto-extracts `.docx` from archives, checks if it's an assignment requirement (keywords: "task", "requirement", "analyze", "please"), and uses it as the task instruction if so.

**Submit analysis code?** Auto-collects Python code used during analysis into a standalone `analysis_script.py` in `./output/`.

---

## Non-Claude-Code / OpenCode Environments

Codex and Cursor lack the `document-skills@anthropic-agent-skills` plugin. Format conversion falls back to Python libraries:

```bash
pip install python-docx python-pptx openpyxl pdfplumber pandas
```

| Operation | Claude Code / OpenCode | Codex / Cursor Fallback |
|-----------|----------------------|------------------------|
| MD → DOCX | docx skill | pandoc or python-docx |
| DOCX → MD | docx skill | pandoc or python-docx |
| PDF → MD | pdf skill | pdfplumber / pymupdf |
| XLSX/CSV | xlsx skill | openpyxl + pandas |
| PPTX | pptx skill | python-pptx |
| Mermaid | `helpers/render_mermaid.py` | Same (Python stdlib) |

**Cursor users**: Convert `SKILL.md` to `.cursor/rules/docwizard.mdc` format (add YAML frontmatter).

---

## Harness Compatibility

| Harness | Status | document-skills | Notes |
|---------|--------|----------------|-------|
| **Claude Code** | Full | ✅ Native | Primary target |
| **OpenCode** | Full | ✅ Compatible | Reads `.claude/skills/` as fallback |
| **Codex (OpenAI)** | Degraded | ❌ | Python library fallback |
| **Cursor** | Degraded | ❌ | Needs `.mdc` format conversion |

Recommended universal path: `.agents/skills/DocWizard/` (supported by Claude Code, Codex, and OpenCode).

---

## Updating

```bash
cd .agents/skills/DocWizard && git pull origin main
```

Or tell your AI:

> Check if DocWizard has a new version

---

## FAQ

| Problem | Platform | Solution |
|---------|----------|----------|
| document-skills plugin not installed | Claude Code / OpenCode | `/plugin install document-skills@anthropic-agent-skills` |
| document-skills unavailable | Codex / Cursor | `pip install python-docx python-pptx openpyxl pdfplumber` |
| DOCX has colored text | All | `python helpers/black_text.py <file.docx>` |
| Mermaid rendering fails | All | mermaid.ink requires internet access |
| PDF Chinese garbled text | Linux | `sudo apt install fonts-noto-cjk` |
| PDF Chinese garbled text | macOS | Ensure PingFang SC / Songti SC available |
| PDF Chinese garbled text | Windows | Ensure SimSun / SimHei fonts exist |
| RAR/7z extraction fails | All | See Stage 3 extraction section for platform-specific install commands |
| CSV Chinese garbled text | Windows | Auto-detects GBK encoding (cp936) |
| Scanned PDF text extraction fails | All | See [Scanned & Image-Based PDFs](#scanned--image-based-pdfs) |
| Windows ZIP filename garbled | Windows | Auto cp437→utf-8→gbk decoding |
| Formulas appear as images | All | OMML conversion fallback (office2pdf can help) |

---

## Acknowledgments

DocWizard builds upon these excellent Claude Code skills and open-source projects:

| Skill / Tool | Purpose | Source |
|-------------|---------|--------|
| `document-skills` | Core docx/pdf/pptx/xlsx processing engine | [anthropics/skills](https://github.com/anthropics/skills) |
| `academic-research-skills` | Academic writing workflow reference (plan-execute pattern) | [Imbad0202](https://github.com/Imbad0202) |
| `MarkItDown` | Multi-format → Markdown conversion reference | [claude-scientific-writer](https://github.com/claude-scientific-writer) |
| mermaid.ink | Online Mermaid diagram rendering | [mermaid.ink](https://mermaid.ink) |
| Pandoc | Document conversion engine inspiration | [pandoc.org](https://pandoc.org) |
| MinerU | High-precision PDF/Office → Markdown parsing | [opendatalab/MinerU](https://github.com/opendatalab/MinerU) |
| Docling (IBM) | High-accuracy table/formula recognition | [DS4SD/docling](https://github.com/DS4SD/docling) |
| python-docx | Word document generation | [python-docx](https://python-docx.readthedocs.io) |
| DrawIO MCP | Complex diagram rendering & export | MCP Integration |
| `Typst` | Next-gen typesetting (.typ → PDF) | [typst.app](https://typst.app) |
| `Typst MCP Server` | Typst typesetting MCP integration | MCP Ecosystem |
| `mcp-pandoc` | Markdown/HTML/LaTeX conversion MCP | MCP Ecosystem |
| `awesome-claude-skills` | 1000+ Claude Code skills library reference | [ComposioHQ](https://github.com/ComposioHQ/awesome-claude-skills) |
| `CrossRef` / `Semantic Scholar` | Reference DOI verification APIs | [crossref.org](https://crossref.org) |
| `refcheck` MCP | Automatic reference verification | MCP Ecosystem |
| `CheckIfExist` | Batch BibTeX multi-source verification | GitHub Open Source |
| `VeriBib` | AI hallucinated citation detection | GitHub Open Source |
| `tectonic` | LaTeX compilation engine (recommended) | [tectonic-typesetting](https://github.com/tectonic-typesetting/tectonic) |
| `Pdf It` (MCP) | Markdown→Professional PDF (TOC/page numbers/font embedding) | MCP Ecosystem |
| `skill-forge` | Skill authoring meta-tool | Claude Code Official |
| `format-thesis` | Chinese thesis Word formatting | [lilanlan11](https://github.com/lilanlan11/format-thesis) |
| `GPT-Researcher` | Autonomous research agent (MCP) | [assafelovic](https://github.com/assafelovic/gpt-researcher) |
| `STORM` | Stanford knowledge curation system | [stanford-oval](https://github.com/stanford-oval/storm) |
| `Slidev` | Markdown→Presentation slides | [slidevjs](https://github.com/slidevjs/slidev) |
| `ydata-profiling` | Automated EDA reports | [ydataai](https://github.com/ydataai/ydata-profiling) |
| `office2pdf` | Rust-based Office→PDF (zero deps) | [developer0hye](https://github.com/developer0hye/office2pdf) |
| `Marp` | Markdown→PPTX presentations | [marp-team](https://github.com/marp-team/marp) |
| `gpt-academic` | Chinese academic AI assistant | [binary-husky](https://github.com/binary-husky/gpt_academic) |
| `D2` | Modern declarative diagramming | [terrastruct](https://github.com/terrastruct/d2) |
| `Paperlib` | Open-source reference manager | [Future-Scholars](https://github.com/Future-Scholars/paperlib) |
| `Quarto` | Scientific publishing system | [quarto-dev](https://github.com/quarto-dev/quarto-cli) |
| `Awesome Typst CN` | Chinese university Typst templates | [qjcg](https://github.com/qjcg/awesome-typst) |
| `Camelot` | PDF table extraction | [camelot-dev](https://github.com/camelot-dev/camelot) |
| `Chandra OCR` | Scanned table+image structured extraction | [datalab-to](https://github.com/datalab-to/chandra-ocr) |
| `Surya OCR` | Multilingual OCR + table detection + layout | [VikParuchuri](https://github.com/VikParuchuri/surya) |
| `LlamaParse` | VLM-powered document parsing (tables+charts) | [LlamaIndex](https://www.llamaindex.ai/llamaparse) |
| `SmolDocling` | 256M lightweight document parsing VLM | [DS4SD](https://github.com/DS4SD/docling) |
| `GLM-OCR` | 0.9B open-source OCR, OmniDocBench #1 (94.62) | [zai-org](https://github.com/zai-org/GLM-OCR) |
| `PyMuPDF4LLM` | CPU-only LLM-ready PDF extraction, 10x speed | [pymupdf](https://github.com/pymupdf/pymupdf4llm) |
| `planning-with-files` | Persistent cross-session task planning (13K+ stars) | [OthmanAdi](https://github.com/OthmanAdi/planning-with-files) |
| `deep-researcher` | Google Scholar → literature matrix → BibTeX | [jackswl](https://github.com/jackswl/deep-researcher) |
| `PapersFlow MCP` | 474M+ papers, citation graph, systematic review | [PapersFlow](https://doxa.papersflow.ai/mcp) |
| `PPTAgent` | ACL 2026, agentic PowerPoint generation + evaluation | ACL 2026 |
| `anki-mcp-server` | Natural language → Anki flashcards via MCP | [ankimcp](https://github.com/ankimcp/anki-mcp-server) |
| `Handoff` | Claude Code session compression for continuation | Matt Pocock |

---

## Contributing

Contributions are welcome! DocWizard aims to save students from tedious homework formatting.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your changes are cross-platform (Windows/macOS/Linux) and, where applicable, cross-harness (Claude Code/OpenCode/Codex/Cursor).

### Project Structure

```
DocWizard/
├── SKILL.md              # Agent operation manual (main entry point)
├── skill.json            # Configuration & metadata
├── task.md               # User task template
├── helpers/
│   ├── render_mermaid.py # Mermaid → PNG renderer (stdlib only)
│   ├── black_text.py     # DOCX black text post-processor
│   ├── verify_refs.py    # Reference DOI/title verifier
│   └── __init__.py
├── test_helpers.py       # Helper script tests
├── setup.py              # One-click cross-platform installer
├── docs/
│   ├── CHANGELOG.md
│   ├── TARGET.md
│   └── TODO.md
└── demo/                 # Demo scenarios
```

---

## License

MIT — [李裕峰](https://github.com/cowhorse05)