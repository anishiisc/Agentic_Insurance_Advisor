#!/bin/bash
# ==============================================================================
# Run Both Backend and Frontend
# ==============================================================================
# Starts both servers in background and provides a unified interface
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# PID files for cleanup
BACKEND_PID=""
FRONTEND_PID=""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "  Backend stopped"
    fi
    
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "  Frontend stopped"
    fi
    
    # Kill any remaining processes on our ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}All servers stopped${NC}"
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM EXIT

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Insurance Policy Advisor - Full Stack    ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check for .env file
if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
    echo -e "${YELLOW}Creating backend/.env file...${NC}"
    echo "ANTHROPIC_API_KEY=your-api-key-here" > "$PROJECT_ROOT/backend/.env"
fi

if grep -q "your-api-key-here" "$PROJECT_ROOT/backend/.env"; then
    echo -e "${RED}⚠ WARNING: Please set your ANTHROPIC_API_KEY in backend/.env${NC}"
    echo -e "${YELLOW}  The application will not work without a valid API key.${NC}"
    echo ""
fi

# Start Backend
echo -e "${YELLOW}Starting Backend Server...${NC}"
cd "$PROJECT_ROOT/backend"

if [ ! -d "venv" ]; then
    echo -e "  Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
else
    source venv/bin/activate
fi

uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend starting on http://localhost:8000${NC}"

# Wait for backend to be ready
echo -e "  Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready${NC}"
        break
    fi
    sleep 1
done

# Start Frontend
echo ""
echo -e "${YELLOW}Starting Frontend Server...${NC}"
cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo -e "  Installing npm packages..."
    npm install > /dev/null 2>&1
fi

npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend starting on http://localhost:5173${NC}"

# Wait for frontend to be ready
echo -e "  Waiting for frontend to be ready..."
sleep 3

# Display status
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}  Both Servers Running!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "  Frontend:  ${YELLOW}http://localhost:5173${NC}"
echo -e "  Backend:   ${YELLOW}http://localhost:8000${NC}"
echo -e "  API Docs:  ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "  Press ${RED}Ctrl+C${NC} to stop all servers"
echo ""

# Keep script running
wait
