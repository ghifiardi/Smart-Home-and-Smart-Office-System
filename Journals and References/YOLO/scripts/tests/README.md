# Auth Service Integration Tests

Comprehensive integration test suite for the Smart Office/Home Surveillance System authentication service.

## 📁 Test Files

```
scripts/tests/
├── README.md                      # This file
├── requirements.txt               # Test dependencies
├── __init__.py                    # Package initialization
├── conftest.py                    # Pytest fixtures and configuration
├── test_auth_integration.py       # Main integration tests
└── test_auth_security.py          # Security-specific tests
```

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
pip install -r scripts/tests/requirements.txt
```

### 2. Ensure Auth Service is Running

```bash
# Start all services
docker-compose up -d

# Or just auth service
docker-compose up -d auth-service postgres redis

# Verify it's running
curl http://localhost:8001/health
```

### 3. Run Tests

```bash
# Run all tests
./scripts/run_auth_tests.sh

# Or use pytest directly
pytest scripts/tests/ --asyncio-mode=auto -v
```

## 🎯 Test Categories

### Integration Tests (`test_auth_integration.py`)

Comprehensive integration tests covering:

- **Health Checks** - Service availability and status
- **User Registration** - Account creation, validation, duplicate handling
- **Login/Logout** - Authentication flows, credential validation
- **JWT Tokens** - Token generation, validation, expiration
- **User Profile** - Profile retrieval and updates
- **RBAC** - Role-based access control
- **Password Management** - Password changes, reset flows
- **Performance** - Response time benchmarks
- **Concurrent Access** - Multiple simultaneous requests

**Total Tests:** 30+ test cases

### Security Tests (`test_auth_security.py`)

Security-focused tests for:

- **Password Security** - Hashing, storage, strength validation
- **Brute Force Protection** - Login attempt limiting
- **Injection Attacks** - SQL, NoSQL, command injection
- **XSS Protection** - Cross-site scripting prevention
- **CSRF Protection** - Cross-site request forgery
- **Session Management** - Session fixation, token rotation
- **Data Exposure** - Sensitive information leakage
- **Authorization Bypass** - Access control enforcement
- **Mass Assignment** - Privilege escalation prevention
- **JWT Security** - Algorithm confusion, none algorithm

**Total Tests:** 15+ security test cases

## 📊 Running Different Test Suites

### Run All Tests

```bash
./scripts/run_auth_tests.sh all
```

### Run Only Integration Tests

```bash
./scripts/run_auth_tests.sh integration
```

### Run Only Security Tests

```bash
./scripts/run_auth_tests.sh security
```

### Run Performance Tests

```bash
./scripts/run_auth_tests.sh performance
```

### Run Quick Tests (Skip Slow Tests)

```bash
./scripts/run_auth_tests.sh quick
```

### Run with Coverage Report

```bash
./scripts/run_auth_tests.sh coverage
```

### Run Specific Test

```bash
pytest scripts/tests/test_auth_integration.py::TestAuthService::test_register_new_user -v
```

### Run Tests in Parallel

```bash
pytest scripts/tests/ -n 4 --asyncio-mode=auto
```

## 🔍 Test Markers

Tests are organized with pytest markers for selective execution:

```bash
# Run only security tests
pytest -m security

# Run only slow tests
pytest -m slow

# Exclude slow tests
pytest -m "not slow"

# Run integration tests
pytest -m integration

# Run performance tests
pytest -m performance
```

## 📝 Test Output Examples

### Successful Test Run

```
========================================
Auth Service Integration Tests
========================================

Test Type: all
Working Directory: /path/to/project

Running All Tests...

test_auth_integration.py::TestAuthService::test_service_health_check PASSED
test_auth_integration.py::TestAuthService::test_register_new_user PASSED
test_auth_integration.py::TestAuthService::test_login_valid_credentials PASSED
test_auth_integration.py::TestAuthService::test_token_contains_user_info PASSED
...

========================================
All Tests Passed! ✓
========================================
```

### Failed Test Run

```
test_auth_integration.py::TestAuthService::test_login_valid_credentials FAILED

FAILED test_auth_integration.py::TestAuthService::test_login_valid_credentials
AssertionError: assert 401 == 200

========================================
Some Tests Failed ✗
========================================
```

## 🧪 Writing New Tests

### Basic Test Structure

```python
import pytest

class TestNewFeature:
    @pytest.mark.asyncio
    async def test_something(self, async_client):
        """Test description"""
        response = await async_client.post("/api/endpoint", json={...})
        assert response.status_code == 200
        assert response.json()["field"] == "expected_value"
```

### Using Fixtures

```python
@pytest.mark.asyncio
async def test_with_auth(self, async_client, admin_token):
    """Test that requires authentication"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get("/api/protected", headers=headers)
    assert response.status_code == 200
```

### Adding Test Markers

```python
@pytest.mark.security
@pytest.mark.slow
@pytest.mark.asyncio
async def test_security_feature(self, async_client):
    """Security test that takes time to run"""
    # Test implementation
```

## 📋 Test Coverage

### Current Coverage Areas

| Area | Coverage | Test Count |
|------|----------|------------|
| User Registration | ✓ High | 6 tests |
| Login/Authentication | ✓ High | 8 tests |
| JWT Token Handling | ✓ High | 7 tests |
| RBAC | ✓ Medium | 3 tests |
| Security | ✓ High | 15 tests |
| Performance | ✓ Low | 2 tests |
| Error Handling | ✓ Medium | 5 tests |

### Generate Coverage Report

```bash
# HTML report
pytest --cov=auth_service --cov-report=html

# Terminal report
pytest --cov=auth_service --cov-report=term

# XML report (for CI/CD)
pytest --cov=auth_service --cov-report=xml
```

## 🔧 Test Configuration

### Environment Variables

```bash
# Auth service URL
export AUTH_SERVICE_URL="http://localhost:8001"

# Database configuration
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="smartoffice"
export DB_USER="smartoffice_user"
export DB_PASSWORD="smartoffice_password"
```

### pytest.ini Configuration

Create `pytest.ini` in project root:

```ini
[pytest]
asyncio_mode = auto
testpaths = scripts/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    integration: integration tests
    security: security tests
    slow: slow running tests
    performance: performance tests
```

## 🐛 Troubleshooting

### Service Not Running

```
Error: Cannot connect to http://localhost:8001

Solution:
docker-compose up -d auth-service postgres redis
```

### Module Not Found

```
ModuleNotFoundError: No module named 'pytest'

Solution:
pip install -r scripts/tests/requirements.txt
```

### Database Connection Failed

```
Error: could not connect to server

Solution:
1. Check if PostgreSQL is running: docker ps
2. Check connection settings in conftest.py
3. Ensure seed data is loaded: ./scripts/load_seed_data.sh
```

### Tests Failing After Seed Data Load

```
Solution:
Some tests expect specific users. Reload seed data:
./scripts/load_seed_data.sh
```

### Async Tests Not Running

```
Error: async def test functions are not natively supported

Solution:
Ensure pytest-asyncio is installed:
pip install pytest-asyncio
```

## 📊 CI/CD Integration

### GitHub Actions Example

```yaml
name: Auth Service Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: timescale/timescaledb:latest-pg15
        env:
          POSTGRES_DB: smartoffice
          POSTGRES_USER: smartoffice_user
          POSTGRES_PASSWORD: smartoffice_password
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r scripts/tests/requirements.txt

      - name: Start auth service
        run: docker-compose up -d auth-service

      - name: Wait for service
        run: sleep 10

      - name: Run tests
        run: ./scripts/run_auth_tests.sh all -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## 📈 Performance Benchmarks

Expected performance metrics:

| Operation | Expected Time | Test |
|-----------|---------------|------|
| User Registration | < 500ms | test_register_new_user |
| Login | < 2s | test_login_response_time |
| Token Validation | < 500ms | test_token_validation_performance |
| Profile Retrieval | < 1s | test_get_current_user |

## 🔐 Security Test Results

Security tests validate:

- ✓ Passwords hashed with bcrypt
- ✓ No plaintext passwords in responses
- ✓ Protection against SQL injection
- ✓ Protection against XSS attacks
- ✓ CSRF protection (token-based)
- ✓ Rate limiting on login attempts
- ✓ Timing attack resistance
- ✓ Session fixation protection
- ✓ Mass assignment protection
- ✓ JWT algorithm validation

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [httpx Documentation](https://www.python-httpx.org/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

## 🤝 Contributing

To add new tests:

1. Create test file: `test_auth_<feature>.py`
2. Import necessary fixtures from `conftest.py`
3. Add appropriate markers (@pytest.mark.*)
4. Follow existing naming conventions
5. Update this README with new test coverage
6. Run tests locally before committing

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review test output for specific error messages
- Check service logs: `docker-compose logs auth-service`
- Verify database connection and seed data

---

**Last Updated:** December 2024
**Test Framework:** pytest 7.4.4
**Python Version:** 3.11+
