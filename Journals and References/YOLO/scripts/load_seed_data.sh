#!/bin/bash
# Load seed data into Smart Office/Home database
# Usage: ./scripts/load_seed_data.sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Database configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-smartoffice}"
DB_USER="${DB_USER:-smartoffice_user}"
DB_PASSWORD="${DB_PASSWORD:-smartoffice_password}"

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SQL_FILE="${SCRIPT_DIR}/seed_data.sql"

echo -e "${BOLD}${BLUE}========================================${NC}"
echo -e "${BOLD}${BLUE}Smart Office/Home Seed Data Loader${NC}"
echo -e "${BOLD}${BLUE}========================================${NC}\n"

# Check if SQL file exists
if [ ! -f "$SQL_FILE" ]; then
    echo -e "${RED}✗ Error: seed_data.sql not found in scripts directory${NC}"
    exit 1
fi

echo -e "${BLUE}ℹ Database: ${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}${NC}"
echo -e "${BLUE}ℹ SQL File: ${SQL_FILE}${NC}\n"

# Check if PostgreSQL is accessible
if ! docker exec smartoffice-postgres pg_isready -U "${DB_USER}" -d "${DB_NAME}" &> /dev/null; then
    echo -e "${RED}✗ Error: Cannot connect to PostgreSQL${NC}"
    echo -e "${YELLOW}  Make sure Docker containers are running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Connected to database${NC}\n"

# Load seed data using docker exec
echo -e "${BOLD}${BLUE}Loading Seed Data...${NC}\n"

if docker exec -i smartoffice-postgres psql -U "${DB_USER}" -d "${DB_NAME}" < "${SQL_FILE}"; then
    echo -e "\n${GREEN}✓ Seed data loaded successfully!${NC}\n"

    # Print login credentials
    echo -e "${BOLD}${BLUE}========================================${NC}"
    echo -e "${BOLD}${BLUE}Default Login Credentials${NC}"
    echo -e "${BOLD}${BLUE}========================================${NC}\n"

    echo -e "${BOLD}Administrator:${NC}"
    echo -e "  Email:    admin@smartoffice.com"
    echo -e "  Password: password123\n"

    echo -e "${BOLD}Security Manager:${NC}"
    echo -e "  Email:    security@smartoffice.com"
    echo -e "  Password: password123\n"

    echo -e "${BOLD}Operator:${NC}"
    echo -e "  Email:    operator@smartoffice.com"
    echo -e "  Password: password123\n"

    echo -e "${YELLOW}Note: Change these passwords in production!${NC}\n"

    exit 0
else
    echo -e "\n${RED}✗ Failed to load seed data${NC}"
    echo -e "${YELLOW}  Check if database tables exist (run migrations first)${NC}"
    exit 1
fi
