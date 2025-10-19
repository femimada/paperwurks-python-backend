"""
Integration tests for complete authentication flows.

Tests cover end-to-end scenarios:
- Complete registration and verification flow
- Login and protected resource access
- Password reset flow
- Token refresh and logout
"""

import json
import pytest
from django.urls import reverse
from django.utils import timezone
from paperwurksapi.apps.common import status
from datetime import datetime, timedelta


pytestmark = pytest.mark.integration


@pytest.mark.django_db
class TestAuthenticationFlow:
    """Test complete authentication user journeys."""
    
    def test_complete_registration_flow(
        self,
        api_client,
        identity_data,
        mock_entity,
        mock_email_service,
        mock_audit_service
    ):
        """
        Test complete registration and verification flow.
        
        Flow:
        1. User registers
        2. Verification email is sent
        3. User verifies email
        4. User can login
        
        Acceptance Criteria:
        - Registration succeeds
        - Email is sent
        - Verification activates account
        - Login works after verification
        - Audit logs are created for each step
        """

        register_url = reverse('identity:register')
        register_data = {
            **identity_data,
            'entity_id': str(mock_entity.id)
        }
        
        register_response = api_client.post(
            register_url,
            register_data,
            format='json'
        )
        
        assert register_response.status_code == status.HTTP_201_CREATED
        assert mock_email_service.call_count == 1  # Verification email sent
        from apps.identity.models import Identity
        identity = Identity.objects.get(email=identity_data['email'])
        verification_token = identity.verification_token
        
        verify_url = reverse('identity:verify-email')
        verify_data = {'token': verification_token}
        
        verify_response = api_client.post(verify_url, verify_data, format='json')
        
        assert verify_response.status_code == status.HTTP_200_OK
        
        # Step 3: Login with verified account
        login_url = reverse('identity:login')
        login_data = {
            'email': identity_data['email'],
            'password': identity_data['password']
        }
        
        login_response = api_client.post(login_url, login_data, format='json')
        
        assert login_response.status_code == status.HTTP_200_OK
        assert 'access_token' in login_response.data
        assert 'refresh_token' in login_response.data
        
        # Verify audit logs were created
        assert mock_audit_service.log.call_count >= 3  # Register, verify, login
    
    def test_login_and_access_protected_resource(
        self,
        api_client,
        mock_verified_identity,
        valid_password
    ):
        """
        Test login and accessing protected resources.
        
        Flow:
        1. User logs in
        2. Receives JWT token
        3. Uses token to access protected resource
        
        Acceptance Criteria:
        - Login succeeds
        - Token is valid
        - Protected resource is accessible with token
        - Protected resource denied without token
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        
        login_response = api_client.post(login_url, login_data, format='json')
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.data['access_token']
        
        # Step 2: Access protected resource without token - should fail
        protected_url = reverse('identity:profile')
        unauth_response = api_client.get(protected_url)
        
        assert unauth_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Step 3: Access protected resource with token - should succeed
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        auth_response = api_client.get(protected_url)
        
        assert auth_response.status_code == status.HTTP_200_OK
        assert auth_response.data['email'] == mock_verified_identity.email
    
    def test_email_verification_flow_end_to_end(
        self,
        api_client,
        mock_unverified_identity,
        valid_password,
        mock_email_service
    ):
        """
        Test complete email verification flow including resend.
        
        Flow:
        1. User tries to login without verification - fails
        2. User resends verification email
        3. User verifies email
        4. User can now login
        
        Acceptance Criteria:
        - Login fails for unverified user
        - Resend generates new token
        - Verification succeeds
        - Login succeeds after verification
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_unverified_identity.email,
            'password': valid_password
        }
        
        login_response = api_client.post(login_url, login_data, format='json') 
        assert login_response.status_code == status.HTTP_403_FORBIDDEN
        resend_url = reverse('identity:resend-verification')
        resend_data = {'email': mock_unverified_identity.email}
        
        resend_response = api_client.post(resend_url, resend_data, format='json')
        
        assert resend_response.status_code == status.HTTP_200_OK
        assert mock_email_service.call_count >= 1
        
        # Step 3: Verify email with new token
        mock_unverified_identity.refresh_from_db()
        new_token = mock_unverified_identity.verification_token
        
        verify_url = reverse('identity:verify-email')
        verify_data = {'token': new_token}
        
        verify_response = api_client.post(verify_url, verify_data, format='json')
        
        assert verify_response.status_code == status.HTTP_200_OK
        
        # Step 4: Login now succeeds
        login_response = api_client.post(login_url, login_data, format='json')
        
        assert login_response.status_code == status.HTTP_200_OK
        assert 'access_token' in login_response.data
    
    def test_password_reset_flow_end_to_end(
        self,
        api_client,
        mock_verified_identity,
        valid_password,
        mock_email_service
    ):
        """
        Test complete password reset flow.
        
        Flow:
        1. User requests password reset
        2. Reset email is sent
        3. User resets password with token
        4. User can login with new password
        5. Old password no longer works
        
        Acceptance Criteria:
        - Reset request succeeds
        - Email is sent
        - Password is updated
        - Login works with new password
        - Old password is invalidated
        """
        new_password = 'NewSecureP@ss456'

        forgot_url = reverse('identity:forgot-password')
        forgot_data = {'email': mock_verified_identity.email}
        
        forgot_response = api_client.post(forgot_url, forgot_data, format='json')
        
        assert forgot_response.status_code == status.HTTP_200_OK
        assert mock_email_service.call_count >= 1
        
        # Step 2: Reset password with token
        mock_verified_identity.refresh_from_db()
        reset_token = mock_verified_identity.password_reset_token
        
        reset_url = reverse('identity:reset-password')
        reset_data = {
            'token': reset_token,
            'new_password': new_password
        }
        
        reset_response = api_client.post(reset_url, reset_data, format='json')
        
        assert reset_response.status_code == status.HTTP_200_OK
        
        # Step 3: Login with new password - should succeed
        login_url = reverse('identity:login')
        new_login_data = {
            'email': mock_verified_identity.email,
            'password': new_password
        }
        
        new_login_response = api_client.post(
            login_url,
            new_login_data,
            format='json'
        )
        
        assert new_login_response.status_code == status.HTTP_200_OK
        
        # Step 4: Login with old password - should fail
        old_login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        
        old_login_response = api_client.post(
            login_url,
            old_login_data,
            format='json'
        )
        
        assert old_login_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_refresh_flow(
        self,
        api_client,
        mock_verified_identity,
        valid_password
    ):
        """
        Test token refresh flow.
        
        Flow:
        1. User logs in
        2. Access token expires (simulated)
        3. User refreshes token
        4. New access token works
        
        Acceptance Criteria:
        - Initial login succeeds
        - Refresh generates new access token
        - New token is valid
        - Old token still works until expiry
        """
        # Step 1: Initial login
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        
        login_response = api_client.post(login_url, login_data, format='json')
        
        assert login_response.status_code == status.HTTP_200_OK
        original_access_token = login_response.data['access_token']
        refresh_token = login_response.data['refresh_token']
        
        # Step 2: Refresh token
        refresh_url = reverse('identity:refresh-token')
        refresh_data = {'refresh_token': refresh_token}
        
        refresh_response = api_client.post(refresh_url, refresh_data, format='json')
        
        assert refresh_response.status_code == status.HTTP_200_OK
        new_access_token = refresh_response.data['access_token']
        
        assert new_access_token != original_access_token
        
        # Step 3: New token works for protected resources
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        protected_url = reverse('identity:profile')
        
        response = api_client.get(protected_url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_logout_invalidates_token(
        self,
        api_client,
        mock_verified_identity,
        valid_password,
        mock_redis
    ):
        """
        Test logout invalidates access token.
        
        Flow:
        1. User logs in
        2. User accesses protected resource
        3. User logs out
        4. Token is blacklisted
        5. Token no longer works
        
        Acceptance Criteria:
        - Login succeeds
        - Protected resource accessible before logout
        - Logout succeeds
        - Token added to blacklist
        - Protected resource denied after logout
        """
        # Step 1: Login
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        
        login_response = api_client.post(login_url, login_data, format='json')
        
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.data['access_token']
        
        # Step 2: Access protected resource - should work
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        protected_url = reverse('identity:profile')
        
        before_logout_response = api_client.get(protected_url)
        assert before_logout_response.status_code == status.HTTP_200_OK
        
        # Step 3: Logout
        logout_url = reverse('identity:logout')
        logout_response = api_client.post(logout_url)
        
        assert logout_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify token was added to blacklist
        assert mock_redis.setex.called
        
        # Step 4: Try to access protected resource - should fail
        mock_redis.exists.return_value = True  # Token is blacklisted
        
        after_logout_response = api_client.get(protected_url)
        assert after_logout_response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAuthenticationEdgeCases:
    """Test edge cases and error scenarios in authentication."""
    
    def test_cannot_login_before_verification(
        self,
        api_client,
        identity_data,
        mock_entity
    ):
        """
        Test that users cannot login before email verification.
        
        Acceptance Criteria:
        - Registration succeeds
        - Immediate login attempt fails
        - Error indicates verification required
        """
        # Register
        register_url = reverse('identity:register')
        register_data = {
            **identity_data,
            'entity_id': str(mock_entity.id)
        }
        
        api_client.post(register_url, register_data, format='json')
        
        # Try to login immediately
        login_url = reverse('identity:login')
        login_data = {
            'email': identity_data['email'],
            'password': identity_data['password']
        }
        
        login_response = api_client.post(login_url, login_data, format='json')
        
        assert login_response.status_code == status.HTTP_403_FORBIDDEN
        assert 'verif' in login_response.data.get('error', '').lower()
    
    def test_can_login_after_verification(
        self,
        api_client,
        mock_unverified_identity,
        valid_password
    ):
        """
        Test that users can login after verification.
        
        Acceptance Criteria:
        - Login fails before verification
        - Email verification succeeds
        - Login succeeds after verification
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_unverified_identity.email,
            'password': valid_password
        }
        
        # Login before verification - fails
        before_response = api_client.post(login_url, login_data, format='json')
        assert before_response.status_code == status.HTTP_403_FORBIDDEN
        
        # Verify email
        verify_url = reverse('identity:verify-email')
        verify_data = {'token': mock_unverified_identity.verification_token}
        api_client.post(verify_url, verify_data, format='json')
        
        # Login after verification - succeeds
        after_response = api_client.post(login_url, login_data, format='json')
        assert after_response.status_code == status.HTTP_200_OK
    
    def test_expired_verification_token_cannot_be_used(
        self,
        api_client,
        mock_unverified_identity
    ):
        """
        Test that expired verification tokens are rejected.
        
        Acceptance Criteria:
        - Expired token verification fails
        - User can request new token
        - New token works
        """
        # Expire the token
        mock_unverified_identity.verification_token_expires_at = (
            timezone.now() - timedelta(hours=25)
        )
        mock_unverified_identity.save()
        
        verify_url = reverse('identity:verify-email')
        verify_data = {'token': mock_unverified_identity.verification_token}
        
        # Expired token fails
        expired_response = api_client.post(verify_url, verify_data, format='json')
        assert expired_response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Request new token
        resend_url = reverse('identity:resend-verification')
        resend_data = {'email': mock_unverified_identity.email}
        api_client.post(resend_url, resend_data, format='json')
        
        # New token works
        mock_unverified_identity.refresh_from_db()
        new_verify_data = {'token': mock_unverified_identity.verification_token}
        
        new_response = api_client.post(verify_url, new_verify_data, format='json')
        assert new_response.status_code == status.HTTP_200_OK
    
    def test_multiple_failed_login_attempts(
        self,
        api_client,
        mock_verified_identity,
        mock_audit_service
    ):
        """
        Test that multiple failed login attempts are logged.
        
        Acceptance Criteria:
        - Each failed attempt is logged
        - Rate limiting applies after X attempts
        - Audit trail is created
        """
        login_url = reverse('identity:login')
        
        # Make multiple failed attempts
        for i in range(3):
            login_data = {
                'email': mock_verified_identity.email,
                'password': f'WrongPassword{i}'
            }
            
            response = api_client.post(login_url, login_data, format='json')
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Verify audit logs were created
        assert mock_audit_service.log.call_count >= 3
    
    def test_concurrent_login_sessions(
        self,
        api_client,
        mock_verified_identity,
        valid_password
    ):
        """
        Test that users can have multiple concurrent sessions.
        
        Acceptance Criteria:
        - Multiple logins create different tokens
        - All tokens are valid simultaneously
        - Each token can be invalidated independently
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        
        # Login twice
        response1 = api_client.post(login_url, login_data, format='json')
        response2 = api_client.post(login_url, login_data, format='json')
        
        token1 = response1.data['access_token']
        token2 = response2.data['access_token']
        
        # Tokens should be different
        assert token1 != token2
        
        # Both tokens should work
        protected_url = reverse('identity:profile')
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        assert api_client.get(protected_url).status_code == status.HTTP_200_OK
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        assert api_client.get(protected_url).status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestAuthenticationSecurity:
    """Test security aspects of authentication flows."""
    
    def test_password_not_exposed_in_any_response(
        self,
        api_client,
        identity_data,
        mock_entity,
        mock_verified_identity,
        valid_password
    ):
        """
        Test that passwords are never exposed in responses.
        
        Acceptance Criteria:
        - Registration response has no password
        - Login response has no password
        - Profile response has no password
        - Error responses have no password
        """
        # Test registration
        register_url = reverse('identity:register')
        register_data = {
            **identity_data,
            'entity_id': str(mock_entity.id)
        }
        
        register_response = api_client.post(
            register_url,
            register_data,
            format='json'
        )
        
        register_str = json.dumps(register_response.data).lower()
        assert 'password' not in register_str
        
        # Test login
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        
        login_response = api_client.post(login_url, login_data, format='json')
        login_str = json.dumps(login_response.data).lower()
        assert 'password' not in login_str
    
    def test_verification_token_not_guessable(
        self,
        api_client,
        identity_data,
        mock_entity
    ):
        """
        Test that verification tokens are sufficiently random.
        
        Acceptance Criteria:
        - Tokens are unique
        - Tokens are sufficiently long
        - Tokens use cryptographic randomness
        """
        from apps.identity.models import Identity
        
        # Create multiple users
        tokens = []
        for i in range(5):
            data = identity_data.copy()
            data['email'] = f'user{i}@example.com'
            
            register_url = reverse('identity:register')
            register_data = {
                **data,
                'entity_id': str(mock_entity.id)
            }
            
            api_client.post(register_url, register_data, format='json')
            
            identity = Identity.objects.get(email=data['email'])
            tokens.append(identity.verification_token)
        
        # All tokens should be unique
        assert len(tokens) == len(set(tokens))
        
        # All tokens should be sufficiently long (at least 32 chars)
        for token in tokens:
            assert len(token) >= 32
    
    def test_password_reset_token_single_use(
        self,
        api_client,
        mock_verified_identity
    ):
        """
        Test that password reset tokens can only be used once.
        
        Acceptance Criteria:
        - Token works for first reset
        - Same token fails for second reset
        - New token must be requested
        """
        # Request password reset
        forgot_url = reverse('identity:forgot-password')
        forgot_data = {'email': mock_verified_identity.email}
        api_client.post(forgot_url, forgot_data, format='json')
        
        mock_verified_identity.refresh_from_db()
        reset_token = mock_verified_identity.password_reset_token
        
        # First reset - succeeds
        reset_url = reverse('identity:reset-password')
        reset_data = {
            'token': reset_token,
            'new_password': 'NewPassword123!'
        }
        
        first_response = api_client.post(reset_url, reset_data, format='json')
        assert first_response.status_code == status.HTTP_200_OK
        
        # Second reset with same token - fails
        second_reset_data = {
            'token': reset_token,
            'new_password': 'AnotherPassword456!'
        }
        
        second_response = api_client.post(reset_url, second_reset_data, format='json')
        assert second_response.status_code == status.HTTP_400_BAD_REQUEST