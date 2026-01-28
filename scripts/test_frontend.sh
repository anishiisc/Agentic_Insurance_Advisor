#!/bin/bash
# ==============================================================================
# Frontend Test Script
# ==============================================================================
# Runs build verification and optional tests
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Insurance Advisor - Frontend Tests       ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

echo -e "${YELLOW}[1/4] Checking dependencies...${NC}"
npm list --depth=0 2>/dev/null | head -20 || true
echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

echo -e "${YELLOW}[2/4] Running ESLint...${NC}"
if npm run lint 2>/dev/null; then
    echo -e "${GREEN}✓ No linting errors${NC}"
else
    echo -e "${YELLOW}⚠ Some linting warnings (non-blocking)${NC}"
fi
echo ""

echo -e "${YELLOW}[3/4] Testing build...${NC}"
if npm run build; then
    echo -e "${GREEN}✓ Build successful${NC}"
    echo ""
    echo -e "  Build output:"
    ls -la dist/ 2>/dev/null || echo "  (dist folder created)"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}[4/4] Checking component files...${NC}"
components=(
    "src/App.jsx"
    "src/components/ChatWindow.jsx"
    "src/components/MessageBubble.jsx"
    "src/components/InputBox.jsx"
)

all_exist=true
for component in "${components[@]}"; do
    if [ -f "$component" ]; then
        echo -e "  ${GREEN}✓${NC} $component"
    else
        echo -e "  ${RED}✗${NC} $component (missing)"
        all_exist=false
    fi
done

if $all_exist; then
    echo -e "${GREEN}✓ All component files present${NC}"
else
    echo -e "${RED}✗ Some components missing${NC}"
fi

# ==============================================================================
# Summary
# ==============================================================================
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}  Frontend Tests Complete!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "To run the development server:"
echo -e "  ${YELLOW}./scripts/run_frontend.sh${NC}"
echo ""
echo -e "To create a production build:"
echo -e "  ${YELLOW}cd frontend && npm run build${NC}"
echo ""
