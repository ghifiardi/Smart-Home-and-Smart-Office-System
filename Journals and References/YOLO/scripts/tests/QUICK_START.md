# Auth Tests Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r scripts/tests/requirements.txt
```

### 2. Start Services
```bash
docker-compose up -d auth-service postgres redis
```

### 3. Load Test Data
```bash
./scripts/load_seed_data.sh
```

### 4. Run Tests
```bash
./scripts/run_auth_tests.sh
```

## 📋 Common Commands

```bash
# Run all tests
./scripts/run_auth_tests.sh all

# Run with verbose output
./scripts/run_auth_tests.sh all -v

# Run only security tests
./scripts/run_auth_tests.sh security

# Run only fast tests
./scripts/run_auth_tests.sh quick

# Generate coverage report
./scripts/run_auth_tests.sh coverage
```

## 🎯 What Gets Tested

### ✅ Integration Tests (30+ tests)
- User registration and validation
- Login with credentials
- JWT token generation and validation
- Protected endpoint access
- User profile management
- Role-based access control
- Password management
- Concurrent access handling

### 🔒 Security Tests (15+ tests)
- Password hashing
- SQL injection protection
- XSS prevention
- Brute force protection
- CSRF protection
- Session security
- JWT security
- Authorization enforcement

## 📊 Expected Results

```
test_auth_integration.py::TestAuthService::test_service_health_check PASSED
test_auth_integration.py::TestAuthService::test_register_new_user PASSED
test_auth_integration.py::TestAuthService::test_login_valid_credentials PASSED
...

========================================
All Tests Passed! ✓
========================================
```

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Service not running | `docker-compose up -d auth-service` |
| Module not found | `pip install -r scripts/tests/requirements.txt` |
| Tests failing | `./scripts/load_seed_data.sh` (reload data) |
| Connection refused | Check if PostgreSQL is up: `docker ps` |

## 📖 Default Test Credentials

```
Admin:
  Email: admin@smartoffice.com
  Password: password123

User:
  Email: john.doe@smartoffice.com
  Password: password123
```

## 🔍 Selective Test Execution

```bash
# Run specific test file
pytest scripts/tests/test_auth_security.py -v

# Run specific test
pytest scripts/tests/test_auth_integration.py::TestAuthService::test_register_new_user -v

# Run tests matching pattern
pytest -k "login" -v

# Run with markers
pytest -m security -v
```

## 📈 Performance Expectations

| Operation | Expected Time |
|-----------|---------------|
| Registration | < 500ms |
| Login | < 2s |
| Token Validation | < 500ms |

## ✨ Next Steps

1. ✅ Tests passing? Great! You're ready to develop
2. ❌ Tests failing? Check the full README.md for detailed troubleshooting
3. 🔧 Want to add tests? See README.md "Writing New Tests" section

---

**Full Documentation:** See `scripts/tests/README.md`
