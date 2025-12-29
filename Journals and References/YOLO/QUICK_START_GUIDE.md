# Smart Office/Home Surveillance System - Quick Start Guide

Complete setup guide with examples for getting your surveillance system running in under 15 minutes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Start Infrastructure Services](#start-infrastructure-services)
4. [Load Seed Data](#load-seed-data)
5. [Start Application Services](#start-application-services)
6. [Verify Services](#verify-services)
7. [Run Tests](#run-tests)
8. [Test API Endpoints](#test-api-endpoints)
9. [Common Issues](#common-issues)

---

## Prerequisites

Before starting, ensure you have:

- Docker Desktop installed and running
- Docker Compose v2.0+
- Python 3.11+
- Git
- 8GB+ RAM available
- 20GB+ free disk space

### Verify Prerequisites

```bash
# Check Docker
docker --version
# Expected: Docker version 24.0.0 or higher

# Check Docker Compose
docker-compose --version
# Expected: Docker Compose version v2.20.0 or higher

# Check Python
python3 --version
# Expected: Python 3.11.0 or higher

# Verify Docker is running
docker ps
# Expected: Should show running containers or empty list (not an error)
```

**Expected Output:**
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

---

## Initial Setup

### 1. Clone Repository (if not already done)

```bash
cd "/Users/raditio.ghifiardigmail.com/Journals and References/YOLO"
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Expected Output:**
```
Collecting fastapi==0.109.0
  Downloading fastapi-0.109.0-py3-none-any.whl
Collecting uvicorn[standard]==0.27.0
  Downloading uvicorn-0.27.0-py3-none-any.whl
...
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 ...
```

### 3. Install Test Dependencies

```bash
pip install -r scripts/tests/requirements.txt
```

**Expected Output:**
```
Collecting pytest==7.4.4
  Downloading pytest-7.4.4-py3-none-any.whl
Collecting pytest-asyncio==0.23.3
  Downloading pytest_asyncio-0.23.3-py3-none-any.whl
...
Successfully installed pytest-7.4.4 pytest-asyncio-0.23.3 ...
```

---

## Start Infrastructure Services

Infrastructure services must start first (PostgreSQL, Redis, MinIO, EMQX).

### 1. Navigate to Surveillance System Directory

```bash
cd surveillance-system
```

### 2. Start Infrastructure Services

```bash
docker-compose up -d postgres redis minio emqx
```

**Expected Output:**
```
[+] Running 4/4
 ✔ Container smartoffice-postgres  Started   2.1s
 ✔ Container smartoffice-redis     Started   1.8s
 ✔ Container smartoffice-minio     Started   2.3s
 ✔ Container smartoffice-emqx      Started   2.5s
```

### 3. Verify Infrastructure Services

```bash
docker-compose ps
```

**Expected Output:**
```
NAME                    IMAGE                              STATUS         PORTS
smartoffice-emqx        emqx/emqx:5.3.0                   Up 30 seconds  0.0.0.0:1883->1883/tcp, 0.0.0.0:18083->18083/tcp
smartoffice-minio       minio/minio:latest                Up 30 seconds  0.0.0.0:9000-9001->9000-9001/tcp
smartoffice-postgres    timescale/timescaledb:latest-pg15 Up 30 seconds  0.0.0.0:5432->5432/tcp
smartoffice-redis       redis:7-alpine                    Up 30 seconds  0.0.0.0:6379->6379/tcp
```

### 4. Wait for Services to be Healthy (30-60 seconds)

```bash
# Check PostgreSQL
docker exec smartoffice-postgres pg_isready -U smartoffice_user
```

**Expected Output:**
```
/var/run/postgresql:5432 - accepting connections
```

```bash
# Check Redis
docker exec smartoffice-redis redis-cli ping
```

**Expected Output:**
```
PONG
```

---

## Load Seed Data

Load sample data for testing (users, sites, cameras, sensors, etc.).

### 1. Run Database Migrations (if not already done)

```bash
# Navigate to project root
cd ..

# Run migrations (from auth-service)
docker exec smartoffice-auth-service alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, create users table
INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, create sites table
...
```

### 2. Load Seed Data

```bash
./scripts/load_seed_data.sh
```

**Expected Output:**
```
========================================
Database Seed Data Loader
========================================

Loading seed data into database...

Database: smartoffice
User: smartoffice_user
SQL File: scripts/seed_data.sql

----------------------------------------
Loading Data...
----------------------------------------

CREATE EXTENSION
CREATE EXTENSION
INSERT 0 7    -- 7 users inserted
INSERT 0 4    -- 4 sites inserted
INSERT 0 9    -- 9 zones inserted
INSERT 0 10   -- 10 cameras inserted
INSERT 0 4    -- 4 access devices inserted
INSERT 0 5    -- 5 sensors inserted
INSERT 0 7    -- 7 registered persons inserted
INSERT 0 5    -- 5 automation rules inserted

========================================
Seed Data Loaded Successfully! ✓
========================================

Default Test Credentials:
  Admin: admin@smartoffice.com / password123
  User: john.doe@smartoffice.com / password123
```

### 3. Verify Data Loaded

```bash
docker exec -it smartoffice-postgres psql -U smartoffice_user -d smartoffice -c "SELECT COUNT(*) FROM users;"
```

**Expected Output:**
```
 count
-------
     7
(1 row)
```

---

## Start Application Services

Now start the microservices (auth, data, detection, etc.).

### 1. Build and Start Auth Service

```bash
cd surveillance-system
docker-compose up -d auth-service
```

**Expected Output:**
```
[+] Building 45.2s (12/12) FINISHED
[+] Running 1/1
 ✔ Container smartoffice-auth-service  Started   1.2s
```

### 2. Verify Auth Service

```bash
curl http://localhost:8001/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0",
  "timestamp": "2024-12-29T10:30:00Z"
}
```

### 3. Start Remaining Services (Optional)

```bash
docker-compose up -d
```

**Expected Output:**
```
[+] Running 8/8
 ✔ Container smartoffice-postgres          Running   0.0s
 ✔ Container smartoffice-redis             Running   0.0s
 ✔ Container smartoffice-minio             Running   0.0s
 ✔ Container smartoffice-emqx              Running   0.0s
 ✔ Container smartoffice-auth-service      Running   0.0s
 ✔ Container smartoffice-data-service      Started   2.3s
 ✔ Container smartoffice-detection-service Started   2.8s
 ✔ Container smartoffice-device-controller Started   2.5s
```

---

## Verify Services

Use the automated testing scripts to verify all services.

### 1. Run Service Health Check Script

```bash
cd ..
./scripts/test_services.sh
```

**Expected Output:**
```
========================================
Smart Office Service Health Checks
========================================

Testing Infrastructure Services...
----------------------------------------
✓ PostgreSQL                     PASS
✓ Redis                          PASS
✓ MinIO                          PASS
✓ EMQX MQTT Broker               PASS

Testing Application Services...
----------------------------------------
✓ Auth Service (HTTP)            PASS
✓ Auth Service (Health)          PASS
✓ Data Service                   PASS
✓ Detection Service              PASS

========================================
Overall Status: ALL SERVICES HEALTHY ✓
========================================
Total: 8/8 tests passed
```

### 2. Run Detailed Python Tests

```bash
python3 scripts/test_services.py
```

**Expected Output:**
```
================================================================================
Smart Office/Home Surveillance System - Service Tests
================================================================================

[1/8] Testing PostgreSQL Connection...
  Host: localhost:5432
  Database: smartoffice
  Result: ✓ PASS - Connection successful

[2/8] Testing Redis Connection...
  Host: localhost:6379
  Result: ✓ PASS - Redis responding

[3/8] Testing MinIO S3 Service...
  Endpoint: localhost:9000
  Result: ✓ PASS - MinIO accessible

[4/8] Testing EMQX MQTT Broker...
  Broker: localhost:1883
  Result: ✓ PASS - MQTT connection successful

[5/8] Testing Auth Service HTTP...
  URL: http://localhost:8001
  Result: ✓ PASS - Service responding

[6/8] Testing Auth Service Health Endpoint...
  URL: http://localhost:8001/health
  Response: {"status":"healthy","service":"auth-service"}
  Result: ✓ PASS - Health check successful

[7/8] Testing Data Service...
  URL: http://localhost:8002/health
  Result: ✓ PASS - Service healthy

[8/8] Testing Detection Service...
  URL: http://localhost:8003/health
  Result: ✓ PASS - Service healthy

================================================================================
TEST SUMMARY
================================================================================
Total Tests: 8
Passed: 8
Failed: 0
Success Rate: 100.0%

Overall Status: ✓ ALL TESTS PASSED
================================================================================
```

---

## Run Tests

Run comprehensive integration and security tests for the auth service.

### 1. Quick Test Run

```bash
./scripts/run_auth_tests.sh quick
```

**Expected Output:**
```
========================================
Auth Service Integration Tests
========================================

Test Type: quick
Working Directory: /Users/raditio.ghifiardigmail.com/Journals and References/YOLO

Running Quick Tests (excluding slow tests)...

test_auth_integration.py::TestAuthService::test_service_health_check PASSED
test_auth_integration.py::TestAuthService::test_register_new_user PASSED
test_auth_integration.py::TestAuthService::test_login_valid_credentials PASSED
test_auth_integration.py::TestAuthService::test_login_invalid_credentials PASSED
test_auth_integration.py::TestAuthService::test_token_contains_user_info PASSED
test_auth_integration.py::TestAuthService::test_token_expiration PASSED
test_auth_integration.py::TestAuthService::test_protected_endpoint_access PASSED
test_auth_integration.py::TestAuthService::test_get_current_user PASSED
test_auth_integration.py::TestAuthService::test_logout PASSED

========================================
All Tests Passed! ✓
========================================
```

### 2. Run Security Tests

```bash
./scripts/run_auth_tests.sh security
```

**Expected Output:**
```
========================================
Auth Service Integration Tests
========================================

Test Type: security
Working Directory: /Users/raditio.ghifiardigmail.com/Journals and References/YOLO

Running Security Tests...

test_auth_security.py::TestAuthSecurity::test_password_hashing PASSED
test_auth_security.py::TestAuthSecurity::test_brute_force_protection PASSED
test_auth_security.py::TestAuthSecurity::test_timing_attack_resistance PASSED
test_auth_security.py::TestAuthSecurity::test_injection_attacks PASSED
test_auth_security.py::TestAuthSecurity::test_xss_in_user_fields PASSED
test_auth_security.py::TestAuthSecurity::test_csrf_protection PASSED
test_auth_security.py::TestAuthSecurity::test_session_fixation_protection PASSED
test_auth_security.py::TestAuthSecurity::test_sensitive_data_exposure PASSED
test_auth_security.py::TestAuthSecurity::test_authorization_bypass PASSED
test_auth_security.py::TestAuthSecurity::test_mass_assignment_protection PASSED
test_auth_security.py::TestAuthSecurity::test_jwt_algorithm_confusion PASSED
test_auth_security.py::TestAuthSecurity::test_cors_configuration PASSED

========================================
All Tests Passed! ✓
========================================
```

### 3. Run All Tests with Verbose Output

```bash
./scripts/run_auth_tests.sh all -v
```

**Expected Output:**
```
========================================
Auth Service Integration Tests
========================================

Running All Tests...

test_auth_integration.py::TestAuthService::test_service_health_check PASSED
test_auth_integration.py::TestAuthService::test_register_new_user PASSED
  - Registered user: test_1703856000@example.com
  - User ID: 550e8400-e29b-41d4-a716-446655440000
test_auth_integration.py::TestAuthService::test_login_valid_credentials PASSED
  - Login successful for: admin@smartoffice.com
  - Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
...

================================ 45 passed in 12.34s ================================
```

---

## Test API Endpoints

Test the REST API endpoints manually using curl.

### 1. Test Health Endpoint

```bash
curl http://localhost:8001/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0",
  "timestamp": "2024-12-29T10:45:00Z"
}
```

### 2. Register a New User

```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.user@example.com",
    "username": "testuser",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }'
```

**Expected Output:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test.user@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-12-29T10:46:00Z"
}
```

### 3. Login and Get Token

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@smartoffice.com&password=password123"
```

**Expected Output:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBzbWFydG9mZmljZS5jb20iLCJleHAiOjE3MDM4NTk2MDAsImlhdCI6MTcwMzg1NjAwMH0.abc123def456ghi789",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 4. Access Protected Endpoint

```bash
# First, save the token from previous command
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use token to access protected endpoint
curl http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Output:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "email": "admin@smartoffice.com",
  "username": "admin",
  "full_name": "System Administrator",
  "is_active": true,
  "is_superuser": true,
  "created_at": "2024-12-29T08:00:00Z"
}
```

### 5. List Cameras (Data Service)

```bash
curl http://localhost:8002/api/cameras \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Output:**
```json
{
  "cameras": [
    {
      "id": "cam-001",
      "name": "Main Entrance - Floor 1",
      "location": "HQ Building - Jakarta",
      "status": "active",
      "stream_url": "rtsp://192.168.1.101:554/stream1",
      "is_active": true
    },
    {
      "id": "cam-002",
      "name": "Lobby Camera 1",
      "location": "HQ Building - Jakarta",
      "status": "active",
      "stream_url": "rtsp://192.168.1.102:554/stream1",
      "is_active": true
    }
  ],
  "total": 10
}
```

### 6. Get Detection Events

```bash
curl http://localhost:8003/api/detections/recent \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Output:**
```json
{
  "detections": [
    {
      "id": "det-001",
      "camera_id": "cam-001",
      "timestamp": "2024-12-29T10:30:15Z",
      "type": "person",
      "confidence": 0.95,
      "bbox": [100, 150, 200, 400],
      "image_url": "http://localhost:9000/detections/det-001.jpg"
    }
  ],
  "total": 15
}
```

---

## Common Issues

### Issue 1: Services Not Starting

**Symptom:**
```
Error response from daemon: Cannot start container
```

**Solution:**
```bash
# Check Docker is running
docker ps

# Restart Docker Desktop
# Then try again:
docker-compose down
docker-compose up -d postgres redis minio emqx
```

---

### Issue 2: Port Already in Use

**Symptom:**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Find process using port (example: 8001)
lsof -i :8001

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
# Change: "8001:8000" to "8002:8000"
```

---

### Issue 3: Database Connection Failed

**Symptom:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check PostgreSQL logs
docker logs smartoffice-postgres

# Restart PostgreSQL
docker-compose restart postgres

# Wait 30 seconds for it to be ready
docker exec smartoffice-postgres pg_isready -U smartoffice_user
```

---

### Issue 4: Seed Data Load Fails

**Symptom:**
```
ERROR: relation "users" does not exist
```

**Solution:**
```bash
# Run migrations first
docker exec smartoffice-auth-service alembic upgrade head

# Then reload seed data
./scripts/load_seed_data.sh
```

---

### Issue 5: Tests Failing

**Symptom:**
```
ERROR: Cannot connect to http://localhost:8001
```

**Solution:**
```bash
# Verify auth service is running
docker ps | grep auth-service

# Check service health
curl http://localhost:8001/health

# If not running, start it
docker-compose up -d auth-service

# Wait 10 seconds, then run tests again
./scripts/run_auth_tests.sh quick
```

---

### Issue 6: Module Not Found During Tests

**Symptom:**
```
ModuleNotFoundError: No module named 'pytest'
```

**Solution:**
```bash
# Install test dependencies
pip install -r scripts/tests/requirements.txt

# Verify installation
pytest --version
```

---

## Quick Command Reference

### Essential Commands

```bash
# Start infrastructure
docker-compose up -d postgres redis minio emqx

# Load seed data
./scripts/load_seed_data.sh

# Start all services
docker-compose up -d

# Run health checks
./scripts/test_services.sh

# Run auth tests
./scripts/run_auth_tests.sh all

# View logs
docker-compose logs -f auth-service

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

### Default Credentials

```
Admin User:
  Email: admin@smartoffice.com
  Password: password123

Regular User:
  Email: john.doe@smartoffice.com
  Password: password123

Security User:
  Email: security@smartoffice.com
  Password: password123
```

### Service URLs

```
Auth Service:       http://localhost:8001
Data Service:       http://localhost:8002
Detection Service:  http://localhost:8003
Device Controller:  http://localhost:8004
Rule Engine:        http://localhost:8005
Notifications:      http://localhost:8006
Analytics:          http://localhost:8007

PostgreSQL:         localhost:5432
Redis:              localhost:6379
MinIO Console:      http://localhost:9001
EMQX Dashboard:     http://localhost:18083
```

---

## Next Steps

After completing this quick start:

1. **Explore the API** - Check API documentation at http://localhost:8001/docs
2. **Customize Configuration** - Edit `surveillance-system/.env` for your environment
3. **Add Your Cameras** - Use the Data Service API to register your RTSP cameras
4. **Configure Alerts** - Set up automation rules through the Rule Engine
5. **Monitor Performance** - Access the Analytics Service dashboard
6. **Review Logs** - Check service logs with `docker-compose logs -f`

---

## Support

For detailed documentation:
- **Testing Guide**: `scripts/tests/README.md`
- **Seed Data Guide**: `scripts/SEED_DATA_README.md`
- **Service Testing**: `scripts/README.md`

For issues:
- Check service logs: `docker-compose logs <service-name>`
- Review database state: `docker exec -it smartoffice-postgres psql -U smartoffice_user -d smartoffice`
- Restart services: `docker-compose restart <service-name>`

---

**Last Updated:** December 29, 2024
**Version:** 1.0.0
**Estimated Setup Time:** 10-15 minutes
