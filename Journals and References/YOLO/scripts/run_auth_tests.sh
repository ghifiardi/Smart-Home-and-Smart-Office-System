#!/bin/bash
# Run Auth Service Integration Tests
# Smart Office/Home Surveillance System

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}========================================${NC}"
echo -e "${BOLD}${BLUE}Auth Service Integration Tests${NC}"
echo -e "${BOLD}${BLUE}========================================${NC}\n"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}✗ pytest is not installed${NC}"
    echo -e "${YELLOW}  Install with: pip install -r scripts/tests/requirements.txt${NC}"
    exit 1
fi

# Check if auth service is running
if ! curl -sf http://localhost:8001/health &> /dev/null && ! curl -sf http://localhost:8001/ &> /dev/null; then
    echo -e "${YELLOW}⚠ Warning: Auth service may not be running${NC}"
    echo -e "${YELLOW}  Start with: docker-compose up -d auth-service${NC}\n"
fi

# Parse arguments
TEST_TYPE="${1:-all}"
VERBOSE=""
if [ "$2" == "-v" ] || [ "$2" == "--verbose" ]; then
    VERBOSE="-v"
fi

echo -e "${BLUE}ℹ Test Type: ${TEST_TYPE}${NC}"
echo -e "${BLUE}ℹ Working Directory: $(pwd)${NC}\n"

# Run tests based on type
case $TEST_TYPE in
    all)
        echo -e "${BOLD}Running All Tests...${NC}\n"
        pytest scripts/tests/test_auth_*.py --asyncio-mode=auto $VERBOSE
        ;;
    integration)
        echo -e "${BOLD}Running Integration Tests...${NC}\n"
        pytest scripts/tests/test_auth_integration.py --asyncio-mode=auto $VERBOSE
        ;;
    security)
        echo -e "${BOLD}Running Security Tests...${NC}\n"
        pytest scripts/tests/test_auth_security.py --asyncio-mode=auto -m security $VERBOSE
        ;;
    performance)
        echo -e "${BOLD}Running Performance Tests...${NC}\n"
        pytest scripts/tests/test_auth_integration.py::TestAuthServicePerformance --asyncio-mode=auto $VERBOSE
        ;;
    quick)
        echo -e "${BOLD}Running Quick Tests (excluding slow tests)...${NC}\n"
        pytest scripts/tests/test_auth_integration.py --asyncio-mode=auto -m "not slow" $VERBOSE
        ;;
    coverage)
        echo -e "${BOLD}Running Tests with Coverage Report...${NC}\n"
        pytest scripts/tests/test_auth_*.py --asyncio-mode=auto --cov=auth_service --cov-report=html --cov-report=term $VERBOSE
        echo -e "\n${GREEN}✓ Coverage report generated in htmlcov/index.html${NC}"
        ;;
    *)
        echo -e "${RED}✗ Unknown test type: $TEST_TYPE${NC}"
        echo -e "${YELLOW}Usage: $0 [all|integration|security|performance|quick|coverage] [-v]${NC}"
        exit 1
        ;;
esac

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${BOLD}${GREEN}========================================${NC}"
    echo -e "${BOLD}${GREEN}All Tests Passed! ✓${NC}"
    echo -e "${BOLD}${GREEN}========================================${NC}\n"
else
    echo -e "\n${BOLD}${RED}========================================${NC}"
    echo -e "${BOLD}${RED}Some Tests Failed ✗${NC}"
    echo -e "${BOLD}${RED}========================================${NC}\n"
fi

exit $EXIT_CODE
