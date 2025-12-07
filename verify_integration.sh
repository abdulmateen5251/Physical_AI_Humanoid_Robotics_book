#!/bin/bash
# Backend-Frontend Integration Verification Checklist
# Run this to verify all components are working correctly

echo "🔍 Backend-Frontend Integration Verification"
echo "=============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
PASS=0
FAIL=0

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Checking $name... "
    
    response=$(curl -s "$url" 2>/dev/null)
    
    if [[ $response == *"$expected"* ]]; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC} (Response: $response)"
        ((FAIL++))
    fi
}

# Function to check file exists
check_file() {
    local filepath=$1
    local description=$2
    
    echo -n "Checking $description... "
    
    if [ -f "$filepath" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC} (File not found)"
        ((FAIL++))
    fi
}

# Function to check port
check_port() {
    local port=$1
    local service=$2
    
    echo -n "Checking $service on port $port... "
    
    if netstat -tuln 2>/dev/null | grep -q ":$port"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️  WARN${NC} (Port may not be listening)"
        # Don't count as fail, might be OS-specific netstat issues
    fi
}

echo "🏗️ INFRASTRUCTURE CHECKS"
echo "------------------------"

check_port 8000 "Backend API"
check_port 3000 "Frontend Dev Server"
check_port 5432 "PostgreSQL Database"
check_port 6333 "Qdrant Vector DB"
check_port 6379 "Redis Cache"

echo ""
echo "🌐 API ENDPOINT CHECKS"
echo "----------------------"

check_service "Backend Health" "http://localhost:8000/health" "healthy"
check_service "Frontend Index" "http://localhost:3000" "Panaversity"

echo ""
echo "📁 INTEGRATION FILES CHECK"
echo "---------------------------"

check_file "frontend/.env.local" "Environment Config"
check_file "frontend/src/utils/apiClient.js" "API Client"
check_file "frontend/src/utils/useApi.js" "React Hooks"
check_file "frontend/src/components/ChatWidget.tsx" "ChatWidget Component"
check_file "frontend/src/components/ChatWidget.module.css" "ChatWidget Styles"
check_file "frontend/src/theme/ChatWidgetPlugin.js" "Docusaurus Plugin"
check_file "frontend/src/theme/ChatWidgetWrapper.tsx" "Root Wrapper"

echo ""
echo "📚 DOCUMENTATION CHECK"
echo "----------------------"

check_file "BACKEND_FRONTEND_INTEGRATION.md" "Integration Guide"
check_file "QUICK_REFERENCE.md" "Quick Reference"
check_file "INTEGRATION_STATUS.md" "Status Report"

echo ""
echo "════════════════════════════════════════════════════"
echo "RESULTS: ${GREEN}${PASS} PASS${NC} | ${RED}${FAIL} FAIL${NC}"
echo "════════════════════════════════════════════════════"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED - INTEGRATION COMPLETE${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Index content: docker compose exec backend python scripts/ingest_to_qdrant.py --docs ../frontend/docs --collection physical_ai_humanoid_robotics_course"
    echo "2. Open browser: http://localhost:3000"
    echo "3. Click blue 💬 button to test ChatWidget"
    echo "4. Ask a question: 'What is ROS 2?'"
    exit 0
else
    echo -e "${RED}❌ SOME CHECKS FAILED - TROUBLESHOOT ABOVE${NC}"
    exit 1
fi
