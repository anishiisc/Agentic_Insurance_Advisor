#!/bin/bash
# ==============================================================================
# Run Backend Server
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Insurance Advisor Backend...${NC}"
echo ""

cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Running setup...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo -e "Creating template .env file..."
    echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
    echo -e "${YELLOW}Please update .env with your Anthropic API key${NC}"
fi

# Check if API key is set
if grep -q "your-api-key-here" .env; then
    echo -e "${YELLOW}⚠ Warning: Please set your ANTHROPIC_API_KEY in backend/.env${NC}"
    echo ""
fi

echo -e "${GREEN}Starting FastAPI server on http://localhost:8000${NC}"
echo -e "${GREEN}API Documentation: http://localhost:8000/docs${NC}"
echo ""

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
