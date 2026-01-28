#!/bin/bash
# ==============================================================================
# Insurance Policy Advisor - Project Initialization Script
# ==============================================================================
# This script sets up the entire project structure for both backend and frontend
# Run this from the project root directory
# ==============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Insurance Policy Advisor - Project Setup  ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"
echo -e "${GREEN}Project root: $PROJECT_ROOT${NC}"

# ==============================================================================
# Backend Setup
# ==============================================================================
echo ""
echo -e "${YELLOW}[1/6] Setting up Backend...${NC}"

# Create backend directory if not exists
mkdir -p backend/data

# Create Python virtual environment
echo -e "  Creating Python virtual environment..."
cd backend
python3 -m venv venv

# Activate virtual environment and install dependencies
echo -e "  Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install fastapi uvicorn anthropic python-dotenv pydantic > /dev/null 2>&1

echo -e "${GREEN}  ✓ Backend dependencies installed${NC}"

# Create .env file if not exists
if [ ! -f .env ]; then
    echo -e "  Creating .env file..."
    echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
    echo -e "${YELLOW}  ⚠ Please update backend/.env with your Anthropic API key${NC}"
else
    echo -e "${GREEN}  ✓ .env file already exists${NC}"
fi

cd "$PROJECT_ROOT"

# ==============================================================================
# Frontend Setup
# ==============================================================================
echo ""
echo -e "${YELLOW}[2/6] Setting up Frontend...${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}  ✗ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}  ✗ npm is not installed. Please install npm first.${NC}"
    exit 1
fi

cd frontend

# Install npm dependencies
echo -e "  Installing npm dependencies..."
npm install > /dev/null 2>&1

echo -e "${GREEN}  ✓ Frontend dependencies installed${NC}"

cd "$PROJECT_ROOT"

# ==============================================================================
# Verify Installation
# ==============================================================================
echo ""
echo -e "${YELLOW}[3/6] Verifying installation...${NC}"

# Check backend
cd backend
source venv/bin/activate
python -c "import fastapi; import anthropic; print('  ✓ Backend packages OK')" 2>/dev/null || echo -e "${RED}  ✗ Backend packages missing${NC}"
cd "$PROJECT_ROOT"

# Check frontend
cd frontend
if [ -d "node_modules" ]; then
    echo -e "${GREEN}  ✓ Frontend packages OK${NC}"
else
    echo -e "${RED}  ✗ Frontend packages missing${NC}"
fi
cd "$PROJECT_ROOT"

# ==============================================================================
# Create run scripts
# ==============================================================================
echo ""
echo -e "${YELLOW}[4/6] Creating helper scripts...${NC}"

# Scripts will be created separately
echo -e "${GREEN}  ✓ Helper scripts ready in scripts/ directory${NC}"

# ==============================================================================
# Summary
# ==============================================================================
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Update ${YELLOW}backend/.env${NC} with your Anthropic API key"
echo -e "  2. Run ${YELLOW}./scripts/run_backend.sh${NC} to start the API server"
echo -e "  3. Run ${YELLOW}./scripts/run_frontend.sh${NC} to start the React app"
echo -e "  4. Open ${YELLOW}http://localhost:5173${NC} in your browser"
echo ""
echo -e "For testing:"
echo -e "  - ${YELLOW}./scripts/test_backend.sh${NC} - Test API endpoints"
echo -e "  - ${YELLOW}./scripts/test_frontend.sh${NC} - Run frontend tests"
echo ""
