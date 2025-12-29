# Service Testing Scripts

This directory contains scripts to test and verify all Smart Office services.

## Available Scripts

### 1. test_services.sh (Bash Script)

A lightweight bash script that quickly tests all services.

**Usage:**
```bash
./scripts/test_services.sh
```

**Features:**
- Tests all infrastructure services (PostgreSQL, Redis, MinIO, EMQX)
- Tests all application services (Auth, Data, Detection, etc.)
- Color-coded output for easy reading
- Returns exit code 0 if all tests pass, 1 if any fail
- Fast execution (no external dependencies)

**Requirements:**
- Docker running
- curl
- nc (netcat)

---

### 2. test_services.py (Python Script)

A comprehensive Python script with detailed testing and reporting.

**Usage:**
```bash
# Install dependencies first
pip install -r scripts/test_requirements.txt

# Run the tests
python3 scripts/test_services.py
```

**Features:**
- Detailed connection testing with error messages
- Tests database connectivity directly
- Tests MQTT broker connections
- Tests HTTP endpoints with retry logic
- Service integration tests
- Comprehensive test summary with timing
- Color-coded output

**Requirements:**
- Python 3.8+
- Dependencies in `test_requirements.txt`:
  - httpx
  - redis
  - psycopg2-binary
  - paho-mqtt

---

## Services Tested

### Infrastructure Services
1. **PostgreSQL** (Port 5432) - TimescaleDB database
2. **Redis** (Port 6379) - Cache and pub/sub
3. **MinIO** (Ports 9000-9001) - S3-compatible object storage
4. **EMQX** (Ports 1883, 18083) - MQTT broker

### Application Services
1. **Auth Service** (Port 8001) - Authentication and authorization
2. **Data Service** (Port 8002) - Data management
3. **Detection Service** (Port 8003) - Object detection and recognition
4. **Device Controller** (Port 8004) - IoT device management
5. **Rule Engine** (Port 8005) - Business rules automation
6. **Notification Service** (Port 8006) - Alerts and notifications
7. **Analytics Service** (Port 8007) - Data analytics and reporting

---

## Quick Start

### Test Only Infrastructure Services

If application services aren't running yet, test just the infrastructure:

```bash
# Using bash
docker exec smartoffice-postgres pg_isready -U smartoffice_user
docker exec smartoffice-redis redis-cli ping
curl http://localhost:9000/minio/health/live
curl http://localhost:18083 | head

# Or use Python
python3 -c "
import redis
r = redis.Redis(host='localhost', port=6379)
print('Redis:', r.ping())
"
```

### Continuous Testing

Run tests in a loop to monitor service health:

```bash
watch -n 5 ./scripts/test_services.sh
```

---

## Exit Codes

Both scripts return:
- **0** - All tests passed
- **1** - One or more tests failed

This makes them suitable for CI/CD pipelines and automated monitoring.

---

## Example Output

```
========================================
Smart Office Service Health Check
========================================

========================================
Infrastructure Services
========================================

✓ PostgreSQL PASS
✓ Redis PASS
✓ MinIO Storage PASS
✓ MinIO Console PASS
✓ EMQX Dashboard PASS
✓ EMQX MQTT Port PASS

========================================
Application Services
========================================

✓ Auth Service (8001) PASS
✓ Data Service (8002) PASS
...

========================================
Test Summary
========================================

Total Tests:  13
Passed:       13
Failed:       0
Duration:     2.34s

ALL TESTS PASSED ✓
```

---

## Troubleshooting

### Script Permission Denied
```bash
chmod +x scripts/test_services.sh
chmod +x scripts/test_services.py
```

### Python Dependencies Missing
```bash
pip install -r scripts/test_requirements.txt
```

### Service Connection Failed
1. Check if Docker containers are running:
   ```bash
   docker ps
   ```

2. Check container logs:
   ```bash
   docker-compose logs <service-name>
   ```

3. Verify service is healthy:
   ```bash
   docker inspect <container-name> | grep Health
   ```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Test Services
  run: |
    ./scripts/test_services.sh
```

### Docker Compose Health Checks

These scripts complement Docker's built-in health checks by providing:
- Application-level testing
- Integration testing between services
- Human-readable output
- Detailed error reporting

---

## Future Enhancements

Potential additions:
- Performance testing (response time benchmarks)
- Load testing capabilities
- Automated alerting on failures
- Prometheus metrics export
- Test result persistence/history
