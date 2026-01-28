#!/bin/bash
# ==============================================================================
# Backend API Test Script
# ==============================================================================
# Tests all API endpoints to ensure the backend is working correctly
# ==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_BASE="http://localhost:8000"
SESSION_ID=""

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Insurance Advisor - Backend API Tests    ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Function to check if server is running
check_server() {
    echo -e "${YELLOW}Checking if backend server is running...${NC}"
    if curl -s "$API_BASE/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend server is running${NC}"
        return 0
    else
        echo -e "${RED}✗ Backend server is not running${NC}"
        echo -e "  Please start the backend first: ./scripts/run_backend.sh"
        exit 1
    fi
}

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo ""
    echo -e "${YELLOW}Test: $description${NC}"
    echo -e "  ${method} ${endpoint}"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_BASE$endpoint")
    elif [ "$method" == "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$API_BASE$endpoint")
    elif [ "$method" == "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$API_BASE$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "  ${GREEN}✓ Status: $http_code${NC}"
        echo -e "  Response: $(echo "$body" | head -c 200)..."
        return 0
    else
        echo -e "  ${RED}✗ Status: $http_code${NC}"
        echo -e "  Response: $body"
        return 1
    fi
}

# ==============================================================================
# Run Tests
# ==============================================================================

check_server

echo ""
echo -e "${BLUE}--- Basic Endpoint Tests ---${NC}"

# Test 1: Health Check
test_endpoint "GET" "/health" "" "Health Check"

# Test 2: Chat - Initial Message (creates session)
echo ""
echo -e "${YELLOW}Test: Chat - Initial Message${NC}"
echo -e "  POST /chat"

response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"message": "Hi, I need health insurance for my family"}' \
    "$API_BASE/chat")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo -e "  ${GREEN}✓ Status: $http_code${NC}"
    SESSION_ID=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', ''))" 2>/dev/null || echo "")
    echo -e "  Session ID: $SESSION_ID"
    echo -e "  Response: $(echo "$body" | head -c 300)..."
else
    echo -e "  ${RED}✗ Status: $http_code${NC}"
    echo -e "  Response: $body"
fi

# Test 3: Chat - Follow-up Message (uses session)
if [ -n "$SESSION_ID" ]; then
    echo ""
    echo -e "${YELLOW}Test: Chat - Follow-up Message (with session)${NC}"
    echo -e "  POST /chat"
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"We are 4 members, budget is 20000 per year\", \"session_id\": \"$SESSION_ID\"}" \
        "$API_BASE/chat")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "  ${GREEN}✓ Status: $http_code${NC}"
        echo -e "  Response: $(echo "$body" | head -c 300)..."
    else
        echo -e "  ${RED}✗ Status: $http_code${NC}"
    fi
fi

# Test 4: Get History
if [ -n "$SESSION_ID" ]; then
    test_endpoint "GET" "/history/$SESSION_ID" "" "Get Conversation History"
fi

# Test 5: Guardrail Test - Off-topic
echo ""
echo -e "${YELLOW}Test: Guardrail - Off-topic Message${NC}"
echo -e "  POST /chat"

response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"message": "Give me stock tips for tomorrow"}' \
    "$API_BASE/chat")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    guardrail=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('guardrail_triggered', False))" 2>/dev/null || echo "")
    if [ "$guardrail" == "True" ]; then
        echo -e "  ${GREEN}✓ Guardrail correctly triggered${NC}"
    else
        echo -e "  ${YELLOW}⚠ Guardrail not triggered (may depend on implementation)${NC}"
    fi
    echo -e "  Response: $(echo "$body" | head -c 200)..."
fi

# Test 6: Clear Session
if [ -n "$SESSION_ID" ]; then
    test_endpoint "DELETE" "/session/$SESSION_ID" "" "Clear Session"
fi

# Test 7: Verify Session Cleared
if [ -n "$SESSION_ID" ]; then
    echo ""
    echo -e "${YELLOW}Test: Verify Session Cleared (should return 404)${NC}"
    echo -e "  GET /history/$SESSION_ID"
    
    response=$(curl -s -w "\n%{http_code}" "$API_BASE/history/$SESSION_ID")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" == "404" ]; then
        echo -e "  ${GREEN}✓ Session correctly cleared (404)${NC}"
    else
        echo -e "  ${YELLOW}⚠ Unexpected status: $http_code${NC}"
    fi
fi

# ==============================================================================
# Summary
# ==============================================================================
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}  Backend Tests Complete!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "API Documentation: ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
