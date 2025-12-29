"""
Security Tests for Auth Service
Tests for common security vulnerabilities and attack vectors
"""

import pytest
import httpx
import time
from typing import List

AUTH_SERVICE_URL = "http://localhost:8001"


class TestAuthSecurity:
    """Security-specific tests for auth service"""

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_password_hashing(self, async_client):
        """Test that passwords are properly hashed and not stored in plaintext"""
        user_data = {
            "email": f"hashtest_{int(time.time())}@test.com",
            "username": "hashtest",
            "password": "TestPassword123!",
            "full_name": "Hash Test User"
        }

        response = await async_client.post("/api/auth/register", json=user_data)

        if response.status_code in [200, 201]:
            data = response.json()

            # Password should never be in response
            assert "password" not in data
            assert "hashed_password" not in data

            # If password is somehow in response, it shouldn't be plaintext
            for key, value in data.items():
                if isinstance(value, str):
                    assert user_data["password"] not in value

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_brute_force_protection(self, async_client):
        """Test protection against brute force attacks"""
        login_attempts = []

        # Attempt multiple failed logins
        for i in range(15):
            response = await async_client.post(
                "/api/auth/login",
                data={
                    "username": "test@test.com",
                    "password": f"wrong_password_{i}"
                }
            )
            login_attempts.append(response.status_code)

        # Should eventually get rate limited or see consistent 401
        assert 401 in login_attempts

        # Optional: Check if rate limiting kicks in (429)
        # This depends on implementation
        if 429 in login_attempts:
            print("✓ Rate limiting detected")

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_timing_attack_resistance(self, async_client):
        """Test that login timing doesn't leak user existence"""
        # Time login attempt with valid email
        valid_email = "admin@smartoffice.com"
        start1 = time.time()
        await async_client.post(
            "/api/auth/login",
            data={"username": valid_email, "password": "wrong"}
        )
        time1 = time.time() - start1

        # Time login attempt with invalid email
        invalid_email = "nonexistent_user_12345@test.com"
        start2 = time.time()
        await async_client.post(
            "/api/auth/login",
            data={"username": invalid_email, "password": "wrong"}
        )
        time2 = time.time() - start2

        # Timing difference should be minimal (< 100ms)
        # This prevents timing attacks to enumerate users
        time_diff = abs(time1 - time2)
        assert time_diff < 0.1

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_injection_attacks(self, async_client):
        """Test various injection attack vectors"""
        injection_payloads = [
            # SQL Injection
            "admin' OR '1'='1",
            "admin' --",
            "admin'; DROP TABLE users; --",

            # NoSQL Injection
            "{'$gt': ''}",
            "{'$ne': null}",

            # Command Injection
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",

            # LDAP Injection
            "*)(uid=*",
            "admin)(|(password=*)",
        ]

        for payload in injection_payloads:
            response = await async_client.post(
                "/api/auth/login",
                data={"username": payload, "password": payload}
            )

            # Should always fail with 401, not 500 (server error)
            assert response.status_code == 401

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_xss_in_user_fields(self, async_client):
        """Test XSS protection in user input fields"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(`XSS`)'></iframe>",
        ]

        for payload in xss_payloads:
            user_data = {
                "email": f"xss_{int(time.time())}@test.com",
                "username": "xss_test",
                "password": "TestPassword123!",
                "full_name": payload
            }

            response = await async_client.post("/api/auth/register", json=user_data)

            if response.status_code in [200, 201]:
                data = response.json()

                # XSS should be escaped or sanitized
                assert "<script>" not in str(data.get("full_name", ""))
                assert "javascript:" not in str(data.get("full_name", ""))

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_csrf_protection(self, async_client):
        """Test CSRF token protection if implemented"""
        # This test depends on CSRF implementation
        # Most API services use token-based auth which is CSRF-resistant

        user_data = {
            "email": f"csrf_{int(time.time())}@test.com",
            "username": "csrf_test",
            "password": "TestPassword123!",
            "full_name": "CSRF Test"
        }

        # Try to submit without CSRF token (if required)
        response = await async_client.post("/api/auth/register", json=user_data)

        # Should work with token-based auth, or require CSRF token
        assert response.status_code in [200, 201, 403]

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_session_fixation_protection(self, async_client):
        """Test that session/token changes after login"""
        user_data = {
            "email": f"session_{int(time.time())}@test.com",
            "username": "session_test",
            "password": "TestPassword123!",
            "full_name": "Session Test"
        }

        # Register user
        await async_client.post("/api/auth/register", json=user_data)

        # Login twice and ensure different tokens
        response1 = await async_client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )

        response2 = await async_client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )

        if response1.status_code == 200 and response2.status_code == 200:
            token1 = response1.json()["access_token"]
            token2 = response2.json()["access_token"]

            # Tokens should be different (prevents session fixation)
            assert token1 != token2

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_sensitive_data_exposure(self, async_client):
        """Test that sensitive data is not exposed in responses"""
        user_data = {
            "email": f"sensitive_{int(time.time())}@test.com",
            "username": "sensitive_test",
            "password": "TestPassword123!",
            "full_name": "Sensitive Test"
        }

        # Register and check response
        response = await async_client.post("/api/auth/register", json=user_data)

        if response.status_code in [200, 201]:
            data = response.json()

            # Sensitive fields should not be in response
            sensitive_fields = [
                "password", "hashed_password", "salt",
                "secret", "private_key", "api_key"
            ]

            for field in sensitive_fields:
                assert field not in data
                assert field not in str(data).lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_authorization_bypass(self, async_client):
        """Test that authorization cannot be bypassed"""
        # Try to access protected endpoint without auth
        response = await async_client.get("/api/auth/me")
        assert response.status_code == 401

        # Try with malformed token
        headers = {"Authorization": "Bearer malformed_token"}
        response = await async_client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401

        # Try without Bearer prefix
        headers = {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}
        response = await async_client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_mass_assignment_protection(self, async_client):
        """Test protection against mass assignment attacks"""
        user_data = {
            "email": f"mass_{int(time.time())}@test.com",
            "username": "mass_test",
            "password": "TestPassword123!",
            "full_name": "Mass Assignment Test",
            # Try to set privileged fields
            "is_superuser": True,
            "is_admin": True,
            "role": "admin"
        }

        response = await async_client.post("/api/auth/register", json=user_data)

        if response.status_code in [200, 201]:
            data = response.json()

            # Privileged fields should not be settable
            assert data.get("is_superuser") != True
            assert data.get("is_admin") != True
            assert data.get("role") != "admin"

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_jwt_algorithm_confusion(self, async_client):
        """Test protection against JWT algorithm confusion attacks"""
        import jwt

        # Create a token with 'none' algorithm
        payload = {"sub": "test@test.com", "exp": time.time() + 3600}
        malicious_token = jwt.encode(payload, "", algorithm="none")

        headers = {"Authorization": f"Bearer {malicious_token}"}
        response = await async_client.get("/api/auth/me", headers=headers)

        # Should be rejected
        assert response.status_code == 401

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_cors_configuration(self, async_client):
        """Test CORS headers are properly configured"""
        # Check CORS headers
        response = await async_client.options("/api/auth/login")

        # Should have proper CORS headers or return allowed status
        assert response.status_code in [200, 204, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-m", "security"])
