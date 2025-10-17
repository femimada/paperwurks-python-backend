"""
API endpoint tests for Authentication endpoints.

Covers:
- US-006: User Registration API
- US-007: User Login API
- US-008: JWT Token Management API
- US-009: Password Reset API
- US-010A: Email Verification API
"""

import pytest
import json
from django.utils import timezone

pytestmark = pytest.mark.api


@pytest.mark.django_db
class TestRegistrationAPI:
    """Test user registration API endpoint (US-006)."""
    
    def test_register_endpoint_returns_201(
        self,
        api_client,
        identity_data,
        mock_entity
    ):
        """
        Test successful registration returns 201 Created.
        
        Acceptance Criteria:
        - Status code is 201
        - Response contains user data
        - Response does not contain password
        """
        url = '/api/identity/register' 
        data = {
            **identity_data,
            'entity_id': str(mock_entity.id)
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert 'id' in response.data
        assert 'email' in response.data
        assert 'password' not in response.data
    
    def test_register_endpoint_validates_required_fields(
        self,
        api_client
    ):
        """
        Test registration validates required fields.
        
        Acceptance Criteria:
        - Status code is 400 for missing fields
        - Error response indicates which fields are required
        """
        url = '/api/identity/register'
        data = {
            'email': 'test@example.com'
            # Missing: password, first_name, last_name
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'password' in response.data or 'errors' in response.data
    
    def test_register_endpoint_returns_400_for_invalid_data(
        self,
        api_client,
        weak_password,
        mock_entity
    ):
        """
        Test registration returns 400 for invalid data.
        
        Acceptance Criteria:
        - Invalid email format returns 400
        - Weak password returns 400
        - Error messages are descriptive
        """
        url = '/api/identity/register'
        
        invalid_email_data = {
            'email': 'invalid-email',
            'password': 'ValidP@ss123',
            'first_name': 'John',
            'last_name': 'Doe',
            'entity_id': str(mock_entity.id)
        }
        
        response = api_client.post(url, invalid_email_data, format='json')
        assert response.status_code == 400
        weak_password_data = {
            'email': 'test@example.com',
            'password': weak_password,
            'first_name': 'John',
            'last_name': 'Doe',
            'entity_id': str(mock_entity.id)
        }
        
        response = api_client.post(url, weak_password_data, format='json')
        assert response.status_code == 400
    
    def test_register_endpoint_returns_409_for_duplicate_email(
        self,
        api_client,
        mock_identity,
        identity_data,
        mock_entity
    ):
        """
        Test registration returns 409 for duplicate email.
        
        Acceptance Criteria:
        - Status code is 409 Conflict
        - Error message indicates email already exists
        """
        url = '/api/identity/register'
        data = {
            'email': mock_identity.email, 
            'password': identity_data['password'],
            'first_name': 'Jane',
            'last_name': 'Doe',
            'entity_id': str(mock_entity.id)
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == 409
        assert 'email' in response.data.get('error', '').lower()
    
    def test_register_endpoint_does_not_expose_password(
        self,
        api_client,
        identity_data,
        mock_entity
    ):
        """
        Test registration response does not expose password.
        
        Acceptance Criteria:
        - Password not in response data
        - Password hash not in response data
        """
        url = '/api/identity/register'
        data = {
            **identity_data,
            'entity_id': str(mock_entity.id)
        }
        response = api_client.post(url, data, format='json')
        response_str = json.dumps(response.data)
        assert 'password' not in response_str.lower()
        assert 'password_hash' not in response_str.lower()


@pytest.mark.django_db
class TestLoginAPI:
    """Test user login API endpoint (US-007)."""
    
    def test_login_endpoint_returns_200_with_valid_credentials(
        self,
        api_client,
        mock_verified_identity,
        valid_password
    ):
        """
        Test successful login returns 200 OK.
        
        Acceptance Criteria:
        - Status code is 200
        - Response contains access and refresh tokens
        - Response contains user data
        """
        url = '/api/identity/login'
        data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == 200
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data
        assert 'user' in response.data
    
    def test_login_endpoint_returns_401_with_invalid_credentials(
        self,
        api_client,
        mock_verified_identity
    ):
        """
        Test login returns 401 with invalid password.
        Acceptance Criteria:
        - Status code is 401 Unauthorized
        - Error message does not reveal if email exists
        """
        url = '/api/identity/login'
        data = {
            'email': mock_verified_identity.email,
            'password': 'WrongPassword123!'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 401
        assert 'invalid credentials' in response.data.get('error', '').lower()
    
    def test_login_endpoint_returns_403_for_unverified_user(
        self,
        api_client,
        mock_unverified_identity,
        valid_password
    ):
        """
        Test login returns 403 for unverified users.
        Acceptance Criteria:
        - Status code is 403 Forbidden
        - Error message indicates email verification required
        """
        url = '/api/identity/login'
        data = {
            'email': mock_unverified_identity.email,
            'password': valid_password
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 403
        assert 'verify' in response.data.get('error', '').lower()
    
    def test_login_endpoint_returns_tokens(
        self,
        api_client,
        mock_verified_identity,
        valid_password
    ):
        """
        Test login returns properly formatted tokens.
        
        Acceptance Criteria:
        - Access token is a valid JWT
        - Refresh token is a valid JWT
        - Token type is Bearer
        - Expiration time is included
        """
        url = '/api/identity/login'
        data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200
        assert response.data['token_type'] == 'Bearer'
        assert 'expires_in' in response.data
        assert len(response.data['access_token']) > 0
        assert len(response.data['refresh_token']) > 0
    
    def test_login_endpoint_does_not_expose_sensitive_data(
        self,
        api_client,
        mock_verified_identity,
        valid_password
    ):
        """
        Test login response does not expose sensitive data.
        
        Acceptance Criteria:
        - Password not in response
        - Password hash not in response
        - Internal IDs properly formatted
        """
        url = '/api/identity/login'
        data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        response = api_client.post(url, data, format='json')
        response_str = json.dumps(response.data)
        assert 'password' not in response_str.lower()
        assert 'password_hash' not in response_str.lower()
        assert 'verification_token' not in response_str.lower()
    
    def test_login_endpoint_rate_limiting(
        self,
        api_client,
        mock_verified_identity
    ):
        """
        Test login endpoint has rate limiting.
        
        Acceptance Criteria:
        - After X failed attempts, returns 429
        - Rate limit applies per IP address
        - Error message indicates rate limit exceeded
        """
        url = '/api/identity/login'
        data = {
            'email': mock_verified_identity.email,
            'password': 'WrongPassword123!'
        }
        for _ in range(5):
            api_client.post(url, data, format='json')
        response = api_client.post(url, data, format='json')
        assert response.status_code == 429


@pytest.mark.django_db
class TestTokenManagementAPI:
    """Test JWT token management API endpoints (US-008)."""
    
    def test_refresh_endpoint_returns_new_token(
        self,
        api_client,
        mock_verified_identity,
        valid_password
    ):
        """
        Test refresh endpoint returns new access token.
        
        Acceptance Criteria:
        - Status code is 200
        - New access token is returned
        - New token is different from original
        """
        login_url = '/api/identity/login'
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        login_response = api_client.post(login_url, login_data, format='json')
        
        original_access_token = login_response.data['access_token']
        refresh_token = login_response.data['refresh_token']
        refresh_url = '/api/identity/refresh'
        refresh_data = {
            'refresh_token': refresh_token
        }
        
        response = api_client.post(refresh_url, refresh_data, format='json')
        assert response.status_code == 200
        assert 'access_token' in response.data
        assert response.data['access_token'] != original_access_token
    
    def test_refresh_endpoint_requires_refresh_token(
        self,
        api_client,
        mock_verified_identity,
        valid_password
    ):
        """
        Test refresh endpoint requires valid refresh token.
        
        Acceptance Criteria:
        - Returns 400 if token not provided
        - Returns 401 if access token used instead
        """
        login_url = '/api/identity/login'
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        login_response = api_client.post(login_url, login_data, format='json')
        access_token = login_response.data['access_token']
        refresh_url = '/api/identity/refresh'
        response = api_client.post(refresh_url, {}, format='json')
        assert response.status_code == 400
        response = api_client.post(
            refresh_url,
            {'refresh_token': access_token},
            format='json'
        )
        assert response.status_code == 401
    
    def test_logout_endpoint_revokes_token(
        self,
        authenticated_client,
        mock_verified_identity
    ):
        """
        Test logout endpoint revokes access token.
        
        Acceptance Criteria:
        - Status code is 204 No Content
        - Token is added to blacklist
        - Token cannot be used after logout
        """
        logout_url = '/api/identity/logout'
        response = authenticated_client.post(logout_url)
        assert response.status_code == 204
        protected_url = '/api/identity/profile'
        protected_response = authenticated_client.get(protected_url)
        
        assert protected_response.status_code == 401
    
    def test_authenticated_request_requires_valid_token(
        self,
        api_client
    ):
        """
        Test protected endpoints require valid token.
        
        Acceptance Criteria:
        - Returns 401 if no token provided
        - Returns 401 if token is malformed
        """
        protected_url = '/api/identity/profile'
        response = api_client.get(protected_url)
        assert response.status_code == 401
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        response = api_client.get(protected_url)
        assert response.status_code == 401
    
    def test_authenticated_request_rejects_expired_token(
        self,
        api_client,
        jwt_payload
    ):
        """
        Test protected endpoints reject expired tokens.
        
        Acceptance Criteria:
        - Returns 401 for expired token
        - Error message indicates token expired
        """
        from paperwurksapi.apps.identity.utils import generate_token
        from datetime import datetime, timedelta
        jwt_payload['exp'] = timezone.now() - timedelta(hours=1)
        expired_token = generate_token(jwt_payload)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {expired_token}')
        protected_url = '/api/identity/profile'
        response = api_client.get(protected_url)
        assert response.status_code == 401
        assert 'expired' in response.data.get('error', '').lower()
    
    def test_authenticated_request_rejects_blacklisted_token(
        self,
        authenticated_client,
        mock_redis
    ):
        """
        Test protected endpoints reject blacklisted tokens.
        
        Acceptance Criteria:
        - Returns 401 for blacklisted token
        - Error message indicates token is invalid
        """
        mock_redis.exists.return_value = True 
        protected_url = '/api/identity/profile'
        response = authenticated_client.get(protected_url)
        assert response.status_code == 401


@pytest.mark.django_db
class TestPasswordResetAPI:
    """Test password reset API endpoints (US-009)."""
    
    def test_forgot_password_endpoint_returns_200(
        self,
        api_client,
        mock_verified_identity
    ):
        """
        Test forgot password endpoint returns 200.
        
        Acceptance Criteria:
        - Status code is 200
        - Success message is returned
        - Response doesn't reveal if email exists
        """
        url = '/api/identity/forgot-password'
        data = {
            'email': mock_verified_identity.email
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 200
        assert 'message' in response.data
    
    def test_forgot_password_endpoint_sends_email(
        self,
        api_client,
        mock_verified_identity,
        mock_email_service
    ):
        """
        Test forgot password sends reset email.
        Acceptance Criteria:
        - Email service is called
        - Email is sent to correct address
        """
        url = '/api/identity/forgot-password'
        data = {
            'email': mock_verified_identity.email
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 200
        mock_email_service.assert_called_once()
    
    def test_reset_password_endpoint_returns_200(
        self,
        api_client,
        password_reset_token
    ):
        """
        Test reset password endpoint returns 200.
        
        Acceptance Criteria:
        - Status code is 200
        - Success message is returned
        """
        url = '/api/identity/reset-password'
        data = {
            'token': password_reset_token,
            'new_password': 'NewSecureP@ss456'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 200
        assert 'message' in response.data
    
    def test_reset_password_endpoint_validates_token(
        self,
        api_client
    ):
        """
        Test reset password validates token.
        
        Acceptance Criteria:
        - Returns 400 for invalid token
        - Returns 400 for expired token
        - Error message is descriptive
        """
        url = '/api/identity/reset-password'
        invalid_data = {
            'token': 'invalid-token-12345',
            'new_password': 'NewSecureP@ss456'
        }
        response = api_client.post(url, invalid_data, format='json')
        assert response.status_code == 400
        assert 'token' in response.data.get('error', '').lower()
    
    def test_reset_password_endpoint_updates_password(
        self,
        api_client,
        password_reset_token,
        mock_verified_identity
    ):
        """
        Test reset password actually updates password.
        Acceptance Criteria:
        - Password is updated
        - User can login with new password
        - Old password no longer works
        """
        new_password = 'NewSecureP@ss456'
        reset_url = '/api/identity/reset-password'
        reset_data = {
            'token': password_reset_token,
            'new_password': new_password
        }
        
        response = api_client.post(reset_url, reset_data, format='json')
        assert response.status_code == 200
        login_url = '/api/identity/login'
        login_data = {
            'email': mock_verified_identity.email,
            'password': new_password
        }
        login_response = api_client.post(login_url, login_data, format='json')
        assert login_response.status_code == 200
        assert 'access_token' in login_response.data


@pytest.mark.django_db
class TestEmailVerificationAPI:
    """Test email verification API endpoints (US-010A)."""
    
    def test_verify_email_endpoint_returns_200(
        self,
        api_client,
        mock_unverified_identity
    ):
        """
        Test verify email endpoint returns 200.
        
        Acceptance Criteria:
        - Status code is 200
        - Success message is returned
        - User is marked as verified
        """
        url = '/api/identity/verify-email'
        data = {
            'token': mock_unverified_identity.verification_token
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 200
        assert 'message' in response.data
        mock_unverified_identity.refresh_from_db()
        assert mock_unverified_identity.is_verified is True
    
    def test_verify_email_endpoint_validates_token(
        self,
        api_client
    ):
        """
        Test verify email validates token.
        
        Acceptance Criteria:
        - Returns 400 for invalid token
        - Returns 400 for expired token
        - Error message is descriptive
        """
        url = '/api/identity/verify-email'
        invalid_data = {
            'token': 'invalid-token-12345'
        }
        response = api_client.post(url, invalid_data, format='json')
        assert response.status_code == 400
        assert 'token' in response.data.get('error', '').lower()
    
    def test_verify_email_endpoint_returns_400_for_expired_token(
        self,
        api_client,
        mock_unverified_identity
    ):
        """
        Test verify email rejects expired tokens.
        
        Acceptance Criteria:
        - Returns 400 for expired token
        - User remains unverified
        - Error indicates token expired
        """
        from datetime import timedelta
        mock_unverified_identity.verification_token_expires_at = (
            timezone.now() - timedelta(hours=25)
        )
        mock_unverified_identity.save()
        
        url = '/api/identity/verify-email'
        data = {
            'token': mock_unverified_identity.verification_token
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'expired' in response.data.get('error', '').lower()
        mock_unverified_identity.refresh_from_db()
        assert mock_unverified_identity.is_verified is False
    
    def test_resend_verification_endpoint_sends_email(
        self,
        api_client,
        mock_unverified_identity,
        mock_email_service
    ):
        """
        Test resend verification sends new email.
        
        Acceptance Criteria:
        - Status code is 200
        - Email service is called
        - New token is generated
        """
        url = '/api/identity/resend-verification'
        data = {
            'email': mock_unverified_identity.email
        }
        
        original_token = mock_unverified_identity.verification_token
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200
        mock_email_service.assert_called_once()
        mock_unverified_identity.refresh_from_db()
        assert mock_unverified_identity.verification_token != original_token
    
    def test_resend_verification_rate_limiting(
        self,
        api_client,
        mock_unverified_identity
    ):
        """
        Test resend verification has rate limiting.
        
        Acceptance Criteria:
        - After X requests, returns 429
        - Rate limit applies per email address
        - Error message indicates rate limit
        """
        url = '/api/identity/resend-verification'
        data = {
            'email': mock_unverified_identity.email
        }
        for _ in range(3):
            api_client.post(url, data, format='json')
        response = api_client.post(url, data, format='json')
        assert response.status_code == 429
        assert 'rate limit' in response.data.get('error', '').lower()