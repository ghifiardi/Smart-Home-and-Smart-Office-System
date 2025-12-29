"""
Pytest Configuration and Fixtures
Smart Office/Home Surveillance System Auth Tests
"""

import pytest
import asyncio
import httpx
from typing import Dict, AsyncGenerator
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Test configuration
AUTH_SERVICE_URL = "http://localhost:8001"
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'smartoffice',
    'user': 'smartoffice_user',
    'password': 'smartoffice_password'
}


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client for auth service"""
    async with httpx.AsyncClient(
        base_url=AUTH_SERVICE_URL,
        timeout=10.0
    ) as client:
        yield client


@pytest.fixture
def db_connection():
    """PostgreSQL database connection"""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    yield conn
    conn.close()


@pytest.fixture
async def test_user(async_client):
    """Create a test user for tests"""
    user_data = {
        "email": "pytest_user@test.com",
        "username": "pytest_user",
        "password": "TestPassword123!",
        "full_name": "Pytest Test User"
    }

    # Try to register user
    response = await async_client.post("/api/auth/register", json=user_data)

    # If user already exists or registration succeeded, return user data
    yield user_data

    # Cleanup: Delete test user after tests
    # This requires admin access or a cleanup endpoint


@pytest.fixture
async def admin_token(async_client):
    """Get admin token for privileged operations"""
    login_data = {
        "username": "admin@smartoffice.com",
        "password": "password123"
    }

    response = await async_client.post("/api/auth/login", data=login_data)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        pytest.skip("Admin user not available")


@pytest.fixture
async def user_token(async_client, test_user):
    """Get regular user token"""
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }

    response = await async_client.post("/api/auth/login", data=login_data)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None


@pytest.fixture
def auth_headers(admin_token):
    """Generate authorization headers"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(autouse=True)
async def cleanup_test_users(db_connection):
    """Auto-cleanup test users after each test"""
    yield

    # Cleanup test users created during tests
    cursor = db_connection.cursor()
    try:
        cursor.execute("""
            DELETE FROM users
            WHERE email LIKE 'pytest_%@test.com'
            OR email LIKE 'test_%@smartoffice.com'
        """)
    except Exception as e:
        print(f"Cleanup warning: {e}")
    finally:
        cursor.close()


# Pytest markers
pytest_plugins = ['pytest_asyncio']


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security-related"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
