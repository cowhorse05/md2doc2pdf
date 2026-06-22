#!/usr/bin/env bash
# DocWizard One-Click Installer (Linux / macOS / WSL)
# Usage: bash install.sh [--yes]
#
# Options:
#   --yes    Skip all prompts, use defaults (recommended for CI/scripting)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

AUTO_YES=false
[[ "${1:-}" == "--yes" ]] && AUTO_YES=true

echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       DocWizard v3.1 — 一键安装          ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Check Python ──────────────────────────────────────────
echo -e "${YELLOW}[1/5]${NC} 检查 Python ..."
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" --version 2>&1)
        echo -e "  ${GREEN}✅${NC} $ver ($cmd)"
        PYTHON="$cmd"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo -e "  ${RED}❌${NC} 未找到 Python 3.7+。请安装 Python: https://python.org/downloads/"
    exit 1
fi

# ── Step 2: Check Git ──────────────────────────────────────────────
echo -e "${YELLOW}[2/5]${NC} 检查 Git ..."
if command -v git &>/dev/null; then
    echo -e "  ${GREEN}✅${NC} $(git --version)"
else
    echo -e "  ${RED}❌${NC} 未找到 Git。请安装 Git: https://git-scm.com/downloads"
    exit 1
fi

# ── Step 3: Detect Platform ────────────────────────────────────────
echo -e "${YELLOW}[3/5]${NC} 检测平台 ..."
OS=$("$PYTHON" -c "import platform; print(platform.system())")
echo -e "  ${GREEN}✅${NC} $OS"

# ── Step 4: Choose Install Directory ───────────────────────────────
echo -e "${YELLOW}[4/5]${NC} 选择安装路径 ..."

# Detect harness
SKILLS_DIR=""
if [ -d ".claude" ] || [ -n "${CLAUDE_CODE:-}" ]; then
    SKILLS_DIR=".claude/skills"
    HARNESS="Claude Code"
elif [ -d ".opencode" ] || [ -n "${OPENCODE:-}" ]; then
    SKILLS_DIR=".opencode/skills"
    HARNESS="OpenCode"
elif [ -d ".codex" ] || [ -n "${CODEX_CLI:-}" ]; then
    SKILLS_DIR=".codex/skills"
    HARNESS="Codex"
elif [ -d ".agents" ]; then
    SKILLS_DIR=".agents/skills"
    HARNESS="Unknown (using .agents/)"
else
    # Default: cross-harness universal path
    SKILLS_DIR=".agents/skills"
    HARNESS="Unknown (using .agents/ cross-harness path)"
fi

INSTALL_PATH="$SKILLS_DIR/DocWizard"
echo -e "  Harness: ${CYAN}$HARNESS${NC}"
echo -e "  安装路径: ${CYAN}$INSTALL_PATH${NC}"

# ── Step 5: Clone & Verify ────────────────────────────────────────
echo -e "${YELLOW}[5/5]${NC} Clone DocWizard ..."

if [ -d "$INSTALL_PATH" ]; then
    echo -e "  ${YELLOW}⚠️${NC}  目录已存在，执行 git pull ..."
    git -C "$INSTALL_PATH" pull origin main
else
    mkdir -p "$(dirname "$INSTALL_PATH")"
    git clone https://github.com/cowhorse05/DocWizard.git "$INSTALL_PATH"
fi

echo ""

# ── Verify ─────────────────────────────────────────────────────────
echo -e "${YELLOW}验证安装 ...${NC}"
FAIL=0

[ -f "$INSTALL_PATH/SKILL.md" ] || { echo -e "  ${RED}❌${NC} SKILL.md 缺失"; FAIL=1; }
[ -f "$INSTALL_PATH/skill.json" ] || { echo -e "  ${RED}❌${NC} skill.json 缺失"; FAIL=1; }
[ -f "$INSTALL_PATH/task.md" ] || { echo -e "  ${RED}❌${NC} task.md 缺失"; FAIL=1; }
[ -f "$INSTALL_PATH/helpers/render_mermaid.py" ] || { echo -e "  ${RED}❌${NC} helpers/render_mermaid.py 缺失"; FAIL=1; }
[ -f "$INSTALL_PATH/helpers/black_text.py" ] || { echo -e "  ${RED}❌${NC} helpers/black_text.py 缺失"; FAIL=1; }
[ -f "$INSTALL_PATH/helpers/verify_refs.py" ] || { echo -e "  ${RED}❌${NC} helpers/verify_refs.py 缺失"; FAIL=1; }

if [ "$FAIL" -eq 0 ]; then
    echo -e "  ${GREEN}✅${NC} 所有核心文件验证通过"
else
    echo -e "  ${RED}❌${NC} 安装不完整，请检查"
    exit 1
fi

# ── Check mermaid.ink ──────────────────────────────────────────────
echo -e "${YELLOW}检测 mermaid.ink 服务 ...${NC}"
"$PYTHON" -c "
import urllib.request
try:
    req = urllib.request.Request('https://mermaid.ink/img/eyJjb2RlIjoiZ3JhcGggVERcbiAgICBBW0hlbGxvXSAtLT4gQntXb3JsZH0ifQ==', headers={'User-Agent': 'DocWizard/3.1'})
    resp = urllib.request.urlopen(req, timeout=10)
    if resp.status == 200 and len(resp.read()) > 100:
        print('  ✅ mermaid.ink 可用（Mermaid 图表渲染正常）')
    else:
        print('  ⚠️  mermaid.ink 响应异常，图表渲染可能受限')
except Exception as e:
    print(f'  ⚠️  mermaid.ink 不可达 ({e})，图表渲染将跳过。可安装 mermaid-cli 作为本地备选。')
"

# ── Check document-skills plugin ───────────────────────────────────
echo ""
echo -e "${YELLOW}检测 document-skills 插件 ...${NC}"
echo -e "  如果你用的是 ${CYAN}Claude Code${NC} 或 ${CYAN}OpenCode${NC}，请在 AI 对话中依次执行:"
echo -e "    ${CYAN}1. /plugin marketplace add anthropics/skills${NC}"
echo -e "    ${CYAN}2. /plugin install document-skills@anthropic-agent-skills${NC}"
echo ""
echo -e "  ${YELLOW}注意：必须先添加 marketplace，否则第二步会报 Marketplace not found。${NC}"
echo ""
echo -e "  如果你用的是 ${CYAN}Codex${NC} 或 ${CYAN}Cursor${NC}，请安装 Python 依赖:"
echo -e "    ${CYAN}pip install python-docx python-pptx openpyxl pdfplumber pandas${NC}"

# ── Done ───────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       ✅ DocWizard 安装完成！             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  安装路径: ${CYAN}$INSTALL_PATH${NC}"
echo -e "  下一步: 在你的 AI 编程助手中说 ${CYAN}「执行 task.md」${NC}"
echo ""
echo -e "  或者: ${CYAN}cd demo/场景名称 && 对你的 AI 说「执行 task.md」${NC} 体验 Demo"
echo ""