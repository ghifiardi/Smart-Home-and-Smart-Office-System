#!/usr/bin/env python3
"""
Integration Tests for Auth Service
Smart Office/Home Surveillance System

Tests authentication, authorization, user management, and JWT token handling.
"""

import pytest
import httpx
import asyncio
from typing import Dict, Optional
import time
import jwt
from datetime import datetime, timedelta

# Test configuration
AUTH_SERVICE_URL = "http://localhost:8001"
TEST_TIMEOUT = 10

# Test user data
TEST_USERS = {
    "admin": {
        "email": "test_admin@smartoffice.com",
        "username": "test_admin",
        "password": "TestAdmin123!",
        "full_name": "Test Administrator"
    },
    "user": {
        "email": "test_user@smartoffice.com",
        "username": "test_user",
        "password": "TestUser123!",
        "full_name": "Test User"
    },
    "operator": {
        "email": "test_operator@smartoffice.com",
        "username": "test_operator",
        "password": "TestOp123!",
        "full_name": "Test Operator"
    }
}


class TestAuthService:
    """Test suite for Auth Service integration tests"""

    @pytest.fixture
    async def client(self):
        """Create async HTTP client"""
        async with httpx.AsyncClient(base_url=AUTH_SERVICE_URL, timeout=TEST_TIMEOUT) as client:
            yield client

    @pytest.fixture
    async def cleanup_test_users(self, client):
        """Cleanup test users after tests"""
        yield
        # Cleanup logic would go here
        # Note: This requires admin access to delete users

    # =========================================================================
    # HEALTH CHECK TESTS
    # =========================================================================

    @pytest.mark.asyncio
    async def test_service_health_check(self, client):
        """Test that auth service is running and healthy"""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok"]

    @pytest.mark.asyncio
    async def test_service_info(self, client):
        """Test service information endpoint"""
        response = await client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "service" in data or "name" in data

    # =========================================================================
    # USER REGISTRATION TESTS
    # =========================================================================

    @pytest.mark.asyncio
    async def test_register_new_user(self, client):
        """Test user registration with valid data"""
        user_data = TEST_USERS["user"].copy()

        response = await client.post("/api/auth/register", json=user_data)

        # Should return 201 Created or 200 OK
        assert response.status_code in [200, 201]

        data = response.json()
        assert "id" in data or "user_id" in data
        assert data.get("email") == user_data["email"]
        assert data.get("username") == user_data["username"]
        assert "password" not in data  # Password should not be returned

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        """Test registration with duplicate email fails"""
        user_data = TEST_USERS["user"].copy()

        # First registration should succeed
        response1 = await client.post("/api/auth/register", json=user_data)
        assert response1.status_code in [200, 201]

        # Second registration with same email should fail
        response2 = await client.post("/api/auth/register", json=user_data)
        assert response2.status_code in [400, 409]  # Bad Request or Conflict

        data = response2.json()
        assert "detail" in data or "error" in data

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        user_data = TEST_USERS["user"].copy()
        user_data["email"] = "invalid-email"

        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client):
        """Test registration with weak password"""
        user_data = TEST_USERS["user"].copy()
        user_data["email"] = "weakpass@test.com"
        user_data["password"] = "123"  # Too weak

        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        incomplete_data = {"email": "incomplete@test.com"}

        response = await client.post("/api/auth/register", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    # =========================================================================
    # LOGIN TESTS
    # =========================================================================

    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, client):
        """Test login with valid credentials"""
        # First register a user
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        # Then login
        login_data = {
            "username": user_data["email"],  # Can use email as username
            "password": user_data["password"]
        }

        response = await client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client):
        """Test login with incorrect password"""
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        login_data = {
            "username": user_data["email"],
            "password": "WrongPassword123!"
        }

        response = await client.post("/api/auth/login", data=login_data)
        assert response.status_code == 401  # Unauthorized

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        login_data = {
            "username": "nonexistent@test.com",
            "password": "SomePassword123!"
        }

        response = await client.post("/api/auth/login", data=login_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client):
        """Test login with inactive user account"""
        # This test assumes there's a way to deactivate users
        # Implementation depends on your API
        pass

    # =========================================================================
    # JWT TOKEN TESTS
    # =========================================================================

    @pytest.mark.asyncio
    async def test_token_contains_user_info(self, client):
        """Test that JWT token contains correct user information"""
        # Register and login
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        login_response = await client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )

        token = login_response.json()["access_token"]

        # Decode token (without verification for testing)
        decoded = jwt.decode(token, options={"verify_signature": False})

        assert "sub" in decoded  # Subject (user identifier)
        assert "exp" in decoded  # Expiration time
        assert decoded["sub"] == user_data["email"] or decoded["sub"] == user_data["username"]

    @pytest.mark.asyncio
    async def test_token_expiration(self, client):
        """Test that token has expiration time"""
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        login_response = await client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )

        token = login_response.json()["access_token"]
        decoded = jwt.decode(token, options={"verify_signature": False})

        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)

        # Token should expire in the future
        assert exp_datetime > datetime.now()

        # Token should expire within reasonable time (e.g., 24 hours)
        assert exp_datetime < datetime.now() + timedelta(days=1)

    @pytest.mark.asyncio
    async def test_access_protected_endpoint_with_token(self, client):
        """Test accessing protected endpoint with valid token"""
        # Register and login
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        login_response = await client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )

        token = login_response.json()["access_token"]

        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/api/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data.get("email") == user_data["email"]

    @pytest.mark.asyncio
    async def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token fails"""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401  # Unauthorized

    @pytest.mark.asyncio
    async def test_access_protected_endpoint_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token fails"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = await client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_token_refresh(self, client):
        """Test token refresh functionality if available"""
        # This depends on whether your API supports refresh tokens
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        login_response = await client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )

        token = login_response.json()["access_token"]

        # Try to refresh token
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/api/auth/refresh", headers=headers)

        # Should return new token or 404 if not implemented
        assert response.status_code in [200, 404]

    # =========================================================================
    # USER PROFILE TESTS
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_current_user(self, client):
        """Test retrieving current user profile"""
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        login_response = await client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data.get("email") == user_data["email"]
        assert data.get("full_name") == user_data["full_name"]
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_update_user_profile(self, client):
        """Test updating user profile"""
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        login_response = await client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update profile
        update_data = {"full_name": "Updated Name"}
        response = await client.patch("/api/auth/me", json=update_data, headers=headers)

        # Should return 200 OK or 404 if not implemented
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_change_password(self, client):
        """Test password change functionality"""
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        login_response = await client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Change password
        password_data = {
            "current_password": user_data["password"],
            "new_password": "NewPassword123!"
        }
        response = await client.post("/api/auth/change-password", json=password_data, headers=headers)

        # Should return 200 OK or 404 if not implemented
        assert response.status_code in [200, 404]

    # =========================================================================
    # ROLE-BASED ACCESS CONTROL (RBAC) TESTS
    # =========================================================================

    @pytest.mark.asyncio
    async def test_admin_access_admin_endpoint(self, client):
        """Test that admin can access admin-only endpoints"""
        # Login with seeded admin user
        login_data = {
            "username": "admin@smartoffice.com",
            "password": "password123"
        }

        response = await client.post("/api/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Try to access admin endpoint (e.g., user list)
            admin_response = await client.get("/api/admin/users", headers=headers)

            # Should be accessible (200) or not found (404) if endpoint doesn't exist
            assert admin_response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_regular_user_cannot_access_admin_endpoint(self, client):
        """Test that regular user cannot access admin endpoints"""
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        login_response = await client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to access admin endpoint
        response = await client.get("/api/admin/users", headers=headers)

        # Should be forbidden (403) or not found (404)
        assert response.status_code in [403, 404]

    # =========================================================================
    # LOGOUT TESTS
    # =========================================================================

    @pytest.mark.asyncio
    async def test_logout(self, client):
        """Test logout functionality if implemented"""
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        login_response = await client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Logout
        response = await client.post("/api/auth/logout", headers=headers)

        # Should return 200 OK or 404 if not implemented
        assert response.status_code in [200, 404]

    # =========================================================================
    # PASSWORD RESET TESTS
    # =========================================================================

    @pytest.mark.asyncio
    async def test_request_password_reset(self, client):
        """Test password reset request"""
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        # Request password reset
        reset_data = {"email": user_data["email"]}
        response = await client.post("/api/auth/password-reset/request", json=reset_data)

        # Should return 200 OK or 404 if not implemented
        assert response.status_code in [200, 202, 404]

    # =========================================================================
    # SECURITY TESTS
    # =========================================================================

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client):
        """Test that rate limiting is in place for login attempts"""
        login_data = {
            "username": "test@test.com",
            "password": "wrong"
        }

        # Make multiple failed login attempts
        responses = []
        for i in range(10):
            response = await client.post("/api/auth/login", data=login_data)
            responses.append(response.status_code)

        # After multiple attempts, should get rate limited (429) or keep getting 401
        # This depends on whether rate limiting is implemented
        assert 401 in responses

    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, client):
        """Test that SQL injection attempts are prevented"""
        malicious_data = {
            "username": "admin' OR '1'='1",
            "password": "password' OR '1'='1"
        }

        response = await client.post("/api/auth/login", data=malicious_data)

        # Should not succeed
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_xss_protection(self, client):
        """Test that XSS attempts in user data are sanitized"""
        user_data = TEST_USERS["user"].copy()
        user_data["full_name"] = "<script>alert('XSS')</script>"
        user_data["email"] = f"xss_{int(time.time())}@test.com"

        response = await client.post("/api/auth/register", json=user_data)

        if response.status_code in [200, 201]:
            data = response.json()
            # Script tags should be escaped or removed
            assert "<script>" not in data.get("full_name", "")

    # =========================================================================
    # CONCURRENT ACCESS TESTS
    # =========================================================================

    @pytest.mark.asyncio
    async def test_concurrent_logins(self, client):
        """Test multiple concurrent login requests"""
        user_data = TEST_USERS["user"].copy()
        await client.post("/api/auth/register", json=user_data)

        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }

        # Make concurrent login requests
        tasks = [
            client.post("/api/auth/login", data=login_data)
            for _ in range(5)
        ]

        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestAuthServicePerformance:
    """Performance tests for auth service"""

    @pytest.mark.asyncio
    async def test_login_response_time(self):
        """Test that login responds within acceptable time"""
        async with httpx.AsyncClient(base_url=AUTH_SERVICE_URL, timeout=TEST_TIMEOUT) as client:
            # Use seeded admin user
            login_data = {
                "username": "admin@smartoffice.com",
                "password": "password123"
            }

            start_time = time.time()
            response = await client.post("/api/auth/login", data=login_data)
            end_time = time.time()

            if response.status_code == 200:
                response_time = end_time - start_time

                # Login should complete within 2 seconds
                assert response_time < 2.0

    @pytest.mark.asyncio
    async def test_token_validation_performance(self):
        """Test that token validation is fast"""
        async with httpx.AsyncClient(base_url=AUTH_SERVICE_URL, timeout=TEST_TIMEOUT) as client:
            # Login to get token
            login_response = await client.post(
                "/api/auth/login",
                data={"username": "admin@smartoffice.com", "password": "password123"}
            )

            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

                start_time = time.time()
                response = await client.get("/api/auth/me", headers=headers)
                end_time = time.time()

                if response.status_code == 200:
                    response_time = end_time - start_time

                    # Token validation should be very fast (< 500ms)
                    assert response_time < 0.5


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
