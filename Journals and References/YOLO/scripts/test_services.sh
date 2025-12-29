#!/bin/bash
# Simple bash script to test all services
# Usage: ./scripts/test_services.sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Counters
TOTAL=0
PASSED=0
FAILED=0

# Print header
print_header() {
    echo -e "\n${BOLD}${BLUE}========================================${NC}"
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo -e "${BOLD}${BLUE}========================================${NC}\n"
}

# Test service
test_service() {
    local name=$1
    local test_command=$2
    TOTAL=$((TOTAL + 1))

    if eval "$test_command" &> /dev/null; then
        echo -e "${GREEN}✓${NC} ${name}${GREEN} PASS${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} ${name}${RED} FAIL${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Print summary
print_summary() {
    print_header "Test Summary"
    echo "Total Tests:  $TOTAL"
    echo -e "${GREEN}Passed:       $PASSED${NC}"
    echo -e "${RED}Failed:       $FAILED${NC}"

    if [ $FAILED -eq 0 ]; then
        echo -e "\n${BOLD}${GREEN}ALL TESTS PASSED ✓${NC}\n"
        exit 0
    else
        echo -e "\n${BOLD}${RED}SOME TESTS FAILED ✗${NC}\n"
        exit 1
    fi
}

# Main tests
main() {
    print_header "Smart Office Service Health Check"

    print_header "Infrastructure Services"

    # PostgreSQL
    test_service "PostgreSQL" \
        "docker exec smartoffice-postgres pg_isready -U smartoffice_user"

    # Redis
    test_service "Redis" \
        "docker exec smartoffice-redis redis-cli ping | grep -q PONG"

    # MinIO
    test_service "MinIO Storage" \
        "curl -sf http://localhost:9000/minio/health/live"

    test_service "MinIO Console" \
        "curl -sf http://localhost:9001 | grep -q html"

    # EMQX
    test_service "EMQX Dashboard" \
        "curl -sf http://localhost:18083 | grep -q html"

    # Check if MQTT port is listening
    test_service "EMQX MQTT Port" \
        "nc -z localhost 1883"

    print_header "Application Services"

    # Application services
    test_service "Auth Service (8001)" \
        "curl -sf http://localhost:8001 || curl -sf http://localhost:8001/health"

    test_service "Data Service (8002)" \
        "curl -sf http://localhost:8002 || curl -sf http://localhost:8002/health"

    test_service "Detection Service (8003)" \
        "curl -sf http://localhost:8003 || curl -sf http://localhost:8003/health"

    test_service "Device Controller (8004)" \
        "curl -sf http://localhost:8004 || curl -sf http://localhost:8004/health"

    test_service "Rule Engine (8005)" \
        "curl -sf http://localhost:8005 || curl -sf http://localhost:8005/health"

    test_service "Notification Service (8006)" \
        "curl -sf http://localhost:8006 || curl -sf http://localhost:8006/health"

    test_service "Analytics Service (8007)" \
        "curl -sf http://localhost:8007 || curl -sf http://localhost:8007/health"

    print_summary
}

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Run tests
main
