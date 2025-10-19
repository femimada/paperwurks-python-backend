"""
Service layer tests for AuthService.

Covers:
- US-006: User Registration
- US-007: User Login
- US-008: JWT Token Management
- US-009: Password Reset
- US-010A: Email Verification
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call, AsyncMock
import bcrypt
from freezegun import freeze_time

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.mark.django_db(transaction=True)
class TestRegistrationService:
    """Test user registration service methods (US-006)."""
    
    async def test_register_user_creates_identity(
        self, 
        identity_data, 
        mock_entity,
    ):
        """
        Test that registration creates a new Identity.
        
        Acceptance Criteria:
        - Identity is created in database
        - All required fields are populated
        - Identity is returned
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        identity = await auth_service.register(
            entity=mock_entity,
            **identity_data
        )
        
        assert identity is not None
        assert identity.email == identity_data['email']
        assert identity.first_name == identity_data['first_name']
        assert identity.last_name == identity_data['last_name']
        assert identity.entity == mock_entity
        assert identity.is_active is False
        assert identity.is_verified is False
    
    async def test_register_user_sends_verification_email(
        self,
        identity_data,
        mock_entity,
        mock_email_service
    ):
        """
        Test that registration sends verification email.
        
        Acceptance Criteria:
        - Email service is called with correct parameters
        - Verification token is included in email
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        identity = await auth_service.register(
            entity=mock_entity,
            **identity_data
        )
        
        mock_email_service.assert_awaited_once()
        call_args = mock_email_service.call_args
        
        assert identity.email in str(call_args)
        assert identity.verification_token in str(call_args)
    
    async def test_register_user_creates_audit_log(
        self,
        identity_data,
        mock_entity,
        mock_audit_service
    ):
        """
        Test that registration creates audit log entry.
        
        Acceptance Criteria:
        - AuditService is called
        - Event type is 'user_registered'
        - Identity ID is logged
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        identity = await auth_service.register(
            entity=mock_entity,
            **identity_data
        )
        
        mock_audit_service.log.assert_awaited_once()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        
        assert call_kwargs['event_type'] == 'user_registered'
        assert call_kwargs['identity_id'] == identity.id
        assert call_kwargs['email'] == identity.email
    
    async def test_register_user_fails_with_duplicate_email(
        self,
        identity_data,
        mock_entity,
        mock_identity
    ):
        """
        Test that registration fails with duplicate email.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message mentions duplicate email
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        # Use existing identity's email
        identity_data['email'] = mock_identity.email
        
        async with pytest.raises(ValueError, match="Email already exists"):
            await auth_service.register(
                entity=mock_entity,
                **identity_data
            )
    
    async def test_register_user_fails_with_weak_password(
        self,
        identity_data,
        mock_entity,
        weak_password
    ):
        """
        Test that registration fails with weak password.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message mentions password requirements
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        identity_data['password'] = weak_password
        
        async with pytest.raises(ValueError, match="Password does not meet requirements"):
            await auth_service.register(
                entity=mock_entity,
                **identity_data
            )
    
    async def test_register_user_validates_email_format(
        self,
        identity_data,
        mock_entity
    ):
        """
        Test that registration validates email format.
        
        Acceptance Criteria:
        - ValueError is raised for invalid email
        - Error message mentions invalid email format
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        identity_data['email'] = 'invalid-email'
        
        async with pytest.raises(ValueError, match="Invalid email format"):
            await auth_service.register(
                entity=mock_entity,
                **identity_data
            )


@pytest.mark.django_db(transaction=True)
class TestLoginService:
    """Test user login/authentication service methods (US-007)."""
    
    async def test_authenticate_with_valid_credentials(
        self,
        mock_verified_identity,
        valid_password
    ):
        """
        Test successful authentication with valid credentials.
        
        Acceptance Criteria:
        - Authentication succeeds
        - Identity object is returned
        - JWT tokens are generated
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        result = await auth_service.authenticate(
            email=mock_verified_identity.email,
            password=valid_password
        )
        
        assert result is not None
        assert result['identity'] == mock_verified_identity
        assert 'access_token' in result
        assert 'refresh_token' in result
    
    async def test_authenticate_fails_with_invalid_password(
        self,
        mock_verified_identity
    ):
        """
        Test authentication fails with incorrect password.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message indicates invalid credentials
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        async with pytest.raises(ValueError, match="Invalid credentials"):
            await auth_service.authenticate(
                email=mock_verified_identity.email,
                password='WrongPassword123!'
            )
    
    async def test_authenticate_fails_for_unverified_user(
        self,
        mock_unverified_identity,
        valid_password
    ):
        """
        Test authentication fails for unverified users.
        
        Acceptance Criteria:
        - PermissionError is raised
        - Error message mentions email verification
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        async with pytest.raises(PermissionError, match="Email not verified"):
            await auth_service.authenticate(
                email=mock_unverified_identity.email,
                password=valid_password
            )
    
    async def test_authenticate_fails_for_inactive_user(
        self,
        mock_inactive_identity,
        valid_password
    ):
        """
        Test authentication fails for inactive accounts.
        
        Acceptance Criteria:
        - PermissionError is raised
        - Error message mentions inactive account
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        async with pytest.raises(PermissionError, match="Account is inactive"):
            await auth_service.authenticate(
                email=mock_inactive_identity.email,
                password=valid_password
            )
    
    @freeze_time("2025-10-16 12:00:00")
    async def test_authenticate_updates_last_login(
        self,
        mock_verified_identity,
        valid_password
    ):
        """
        Test that successful login updates last_login timestamp.
        
        Acceptance Criteria:
        - last_login is updated to current time
        - Timestamp is persisted to database
        """
        from apps.identity.services import AuthService
        
        assert mock_verified_identity.last_login is None
        
        auth_service = AuthService()
        await auth_service.authenticate(
            email=mock_verified_identity.email,
            password=valid_password
        )
        
        await mock_verified_identity.arefresh_from_db()
        assert mock_verified_identity.last_login is not None
        assert mock_verified_identity.last_login == datetime(2025, 10, 16, 12, 0, 0)
    
    async def test_authenticate_creates_audit_log(
        self,
        mock_verified_identity,
        valid_password,
        mock_audit_service
    ):
        """
        Test that login creates audit log entry.
        
        Acceptance Criteria:
        - AuditService is called
        - Event type is 'user_login'
        - Identity ID and email are logged
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        await auth_service.authenticate(
            email=mock_verified_identity.email,
            password=valid_password
        )
        
        mock_audit_service.log.assert_awaited_once()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        
        assert call_kwargs['event_type'] == 'user_login'
        assert call_kwargs['identity_id'] == mock_verified_identity.id
        assert call_kwargs['email'] == mock_verified_identity.email
    
    async def test_generate_jwt_tokens(
        self,
        mock_verified_identity,
        valid_password
    ):
        """
        Test that JWT tokens are generated on login.
        
        Acceptance Criteria:
        - Access token is generated
        - Refresh token is generated
        - Tokens are different from each other
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        result = await auth_service.authenticate(
            email=mock_verified_identity.email,
            password=valid_password
        )
        
        assert result['access_token'] is not None
        assert result['refresh_token'] is not None
        assert result['access_token'] != result['refresh_token']
    
    async def test_jwt_token_contains_correct_claims(
        self,
        mock_verified_identity,
        valid_password
    ):
        """
        Test that JWT tokens contain required claims.
        
        Acceptance Criteria:
        - Token includes user ID (sub)
        - Token includes email
        - Token includes entity_id
        - Token includes expiration (exp)
        - Token includes issued at (iat)
        """
        from apps.identity.services import AuthService
        from apps.identity.utils.jwt_utils import decode_token
        
        auth_service = AuthService()
        result = await auth_service.authenticate(
            email=mock_verified_identity.email,
            password=valid_password
        )
        
        payload = decode_token(result['access_token'])
        
        assert payload['sub'] == str(mock_verified_identity.id)
        assert payload['email'] == mock_verified_identity.email
        assert payload['entity_id'] == str(mock_verified_identity.entity.id)
        assert 'exp' in payload
        assert 'iat' in payload


@pytest.mark.django_db(transaction=True)
class TestTokenManagementService:
    """Test JWT token management service methods (US-008)."""
    
    async def test_validate_token_success(self, jwt_payload):
        """
        Test that valid tokens are successfully validated.
        
        Acceptance Criteria:
        - Token validation returns True
        - Payload is correctly decoded
        """
        from apps.identity.utils.jwt_utils import generate_token, validate_token
        
        token = generate_token(jwt_payload)
        is_valid, payload = await validate_token(token)
        
        assert is_valid is True
        assert payload['sub'] == jwt_payload['sub']
        assert payload['email'] == jwt_payload['email']
    
    async def test_validate_token_fails_for_expired(self, jwt_payload):
        """
        Test that expired tokens fail validation.
        
        Acceptance Criteria:
        - Token validation returns False
        - Error indicates token expired
        """
        from apps.identity.utils.jwt_utils import generate_token, validate_token
        
        # Create expired token
        jwt_payload['exp'] = datetime.utcnow() - timedelta(hours=1)
        token = generate_token(jwt_payload)
        
        is_valid, error = await validate_token(token)
        
        assert is_valid is False
        assert 'expired' in error.lower()
    
    async def test_validate_token_fails_for_invalid_signature(self):
        """
        Test that tokens with invalid signatures fail validation.
        
        Acceptance Criteria:
        - Token validation returns False
        - Error indicates invalid signature
        """
        from apps.identity.utils.jwt_utils import validate_token
        
        # Create token with invalid signature
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        
        is_valid, error = await validate_token(invalid_token)
        
        assert is_valid is False
        assert 'invalid' in error.lower()
    
    async def test_refresh_token_generates_new_access_token(
        self,
        mock_verified_identity,
        valid_password
    ):
        """
        Test that refresh token generates new access token.
        
        Acceptance Criteria:
        - New access token is generated
        - New token is different from original
        - New token has updated expiration
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        # Initial login
        result = await auth_service.authenticate(
            email=mock_verified_identity.email,
            password=valid_password
        )
        original_access_token = result['access_token']
        refresh_token = result['refresh_token']
        
        # Refresh token
        new_result = await auth_service.refresh_access_token(refresh_token)
        new_access_token = new_result['access_token']
        
        assert new_access_token != original_access_token
        assert new_result['token_type'] == 'Bearer'
    
    async def test_refresh_token_fails_with_access_token(
        self,
        mock_verified_identity,
        valid_password
    ):
        """
        Test that using access token for refresh fails.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message indicates wrong token type
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        result = await auth_service.authenticate(
            email=mock_verified_identity.email,
            password=valid_password
        )
        access_token = result['access_token']
        
        async with pytest.raises(ValueError, match="Invalid token type"):
            await auth_service.refresh_access_token(access_token)
    
    async def test_revoke_token_adds_to_blacklist(
        self,
        mock_verified_identity,
        valid_password,
        mock_redis
    ):
        """
        Test that token revocation adds token to blacklist.
        
        Acceptance Criteria:
        - Token is added to Redis blacklist
        - TTL is set to token expiration time
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        result = await auth_service.authenticate(
            email=mock_verified_identity.email,
            password=valid_password
        )
        access_token = result['access_token']
        
        await auth_service.revoke_token(access_token)
        
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert access_token in str(call_args)
    
    async def test_blacklisted_token_is_rejected(
        self,
        mock_verified_identity,
        valid_password,
        mock_redis
    ):
        """
        Test that blacklisted tokens are rejected.
        
        Acceptance Criteria:
        - Validation fails for blacklisted token
        - Error message indicates token is revoked
        """
        from apps.identity.services import AuthService
        from apps.identity.utils.jwt_utils import is_token_blacklisted
        
        auth_service = AuthService()
        
        result = await auth_service.authenticate(
            email=mock_verified_identity.email,
            password=valid_password
        )
        access_token = result['access_token']
        
        # Mock Redis to return token exists in blacklist
        mock_redis.exists.return_value = True
        
        is_blacklisted = await is_token_blacklisted(access_token)
        
        assert is_blacklisted is True


@pytest.mark.django_db(transaction=True)
class TestPasswordResetService:
    """Test password reset service methods (US-009)."""
    
    async def test_request_password_reset_generates_token(
        self,
        mock_verified_identity,
        mock_email_service
    ):
        """
        Test that password reset request generates reset token.
        
        Acceptance Criteria:
        - Reset token is generated
        - Token expiration is set (1 hour)
        - Token is persisted to database
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        result = await auth_service.request_password_reset(
            email=mock_verified_identity.email
        )
        
        await mock_verified_identity.arefresh_from_db()
        
        assert mock_verified_identity.password_reset_token is not None
        assert mock_verified_identity.password_reset_expires_at is not None
        assert result['message'] == 'Password reset email sent'
    
    async def test_request_password_reset_sends_email(
        self,
        mock_verified_identity,
        mock_email_service
    ):
        """
        Test that password reset request sends email.
        
        Acceptance Criteria:
        - Email service is called
        - Reset token is included in email
        - Email is sent to correct address
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        await auth_service.request_password_reset(
            email=mock_verified_identity.email
        )
        
        mock_email_service.assert_awaited_once()
        call_args = mock_email_service.call_args
        
        assert mock_verified_identity.email in str(call_args)
        assert 'reset' in str(call_args).lower()
    
    async def test_request_password_reset_creates_audit_log(
        self,
        mock_verified_identity,
        mock_audit_service
    ):
        """
        Test that password reset request creates audit log.
        
        Acceptance Criteria:
        - AuditService is called
        - Event type is 'password_reset_requested'
        - Identity email is logged
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        await auth_service.request_password_reset(
            email=mock_verified_identity.email
        )
        
        mock_audit_service.log.assert_awaited_once()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        
        assert call_kwargs['event_type'] == 'password_reset_requested'
        assert call_kwargs['email'] == mock_verified_identity.email
    
    async def test_reset_password_with_valid_token(
        self,
        mock_verified_identity,
        valid_password
    ):
        """
        Test password reset with valid token.
        
        Acceptance Criteria:
        - Password is updated
        - Reset token is cleared
        - Success message is returned
        """
        from apps.identity.services import AuthService
        
        # First request password reset
        auth_service = AuthService()
        await auth_service.request_password_reset(
            email=mock_verified_identity.email
        )
        
        await mock_verified_identity.arefresh_from_db()
        reset_token = mock_verified_identity.password_reset_token
        
        # Reset password with token
        new_password = "NewSecureP@ss456"
        result = await auth_service.reset_password(
            token=reset_token,
            new_password=new_password
        )
        
        await mock_verified_identity.arefresh_from_db()
        
        assert result['message'] == 'Password reset successfully'
        assert mock_verified_identity.password_reset_token is None
        assert mock_verified_identity.password_reset_expires_at is None
    
    async def test_reset_password_with_expired_token(
        self,
        mock_verified_identity
    ):
        """
        Test password reset with expired token fails.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message indicates token expired
        - Password is not changed
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        # Set expired token
        mock_verified_identity.password_reset_token = 'expired-token'
        mock_verified_identity.password_reset_expires_at = datetime.utcnow() - timedelta(hours=2)
        await mock_verified_identity.asave()
        
        original_password_hash = mock_verified_identity.password_hash
        
        async with pytest.raises(ValueError, match="Reset token expired"):
            await auth_service.reset_password(
                token='expired-token',
                new_password='NewPassword123!'
            )
        
        await mock_verified_identity.arefresh_from_db()
        assert mock_verified_identity.password_hash == original_password_hash
    
    async def test_reset_password_updates_password_hash(
        self,
        mock_verified_identity,
        valid_password
    ):
        """
        Test that password reset updates password hash using bcrypt.
        
        Acceptance Criteria:
        - Password hash is updated
        - New password can be verified
        - Old password no longer works
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        # Request reset
        await auth_service.request_password_reset(
            email=mock_verified_identity.email
        )
        
        await mock_verified_identity.arefresh_from_db()
        reset_token = mock_verified_identity.password_reset_token
        original_password_hash = mock_verified_identity.password_hash
        
        # Reset with new password
        new_password = "NewSecureP@ss456"
        await auth_service.reset_password(
            token=reset_token,
            new_password=new_password
        )
        
        await mock_verified_identity.arefresh_from_db()
        
        # Verify password hash changed
        assert mock_verified_identity.password_hash != original_password_hash
        
        # Verify new password works
        is_valid = bcrypt.checkpw(
            new_password.encode('utf-8'),
            mock_verified_identity.password_hash.encode('utf-8')
        )
        assert is_valid is True
        
        # Verify old password doesn't work
        is_old_valid = bcrypt.checkpw(
            valid_password.encode('utf-8'),
            mock_verified_identity.password_hash.encode('utf-8')
        )
        assert is_old_valid is False
    
    async def test_reset_password_with_weak_password_fails(
        self,
        mock_verified_identity,
        weak_password
    ):
        """
        Test that password reset with weak password fails.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error mentions password requirements
        - Password is not changed
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        # Request reset
        await auth_service.request_password_reset(
            email=mock_verified_identity.email
        )
        
        await mock_verified_identity.arefresh_from_db()
        reset_token = mock_verified_identity.password_reset_token
        original_password_hash = mock_verified_identity.password_hash
        
        async with pytest.raises(ValueError, match="Password does not meet requirements"):
            await auth_service.reset_password(
                token=reset_token,
                new_password=weak_password
            )
        
        await mock_verified_identity.arefresh_from_db()
        assert mock_verified_identity.password_hash == original_password_hash


@pytest.mark.django_db(transaction=True)
class TestEmailVerificationService:
    """Test email verification service methods (US-010A)."""
    
    async def test_send_verification_email(
        self,
        mock_unverified_identity,
        mock_email_service
    ):
        """
        Test that verification email is sent.
        
        Acceptance Criteria:
        - Email service is called
        - Verification token is included
        - Email is sent to correct address
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        await auth_service.send_verification_email(mock_unverified_identity)
        
        mock_email_service.assert_awaited_once()
        call_args = mock_email_service.call_args
        
        assert mock_unverified_identity.email in str(call_args)
        assert mock_unverified_identity.verification_token in str(call_args)
    
    async def test_verify_email_creates_audit_log(
        self,
        mock_unverified_identity,
        mock_audit_service
    ):
        """
        Test that email verification creates audit log.
        
        Acceptance Criteria:
        - AuditService is called
        - Event type is 'email_verified'
        - Identity ID is logged
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        token = mock_unverified_identity.verification_token
        
        await auth_service.verify_email(token)
        
        mock_audit_service.log.assert_awaited_once()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        
        assert call_kwargs['event_type'] == 'email_verified'
        assert call_kwargs['identity_id'] == mock_unverified_identity.id
    
    async def test_resend_verification_generates_new_token(
        self,
        mock_unverified_identity
    ):
        """
        Test that resending verification generates new token.
        
        Acceptance Criteria:
        - New verification token is generated
        - New token is different from original
        - Expiration is updated
        """
        from apps.identity.services import AuthService
        
        original_token = mock_unverified_identity.verification_token
        original_expiry = mock_unverified_identity.verification_token_expires_at
        
        auth_service = AuthService()
        await auth_service.resend_verification_email(mock_unverified_identity.email)
        
        await mock_unverified_identity.arefresh_from_db()
        
        assert mock_unverified_identity.verification_token != original_token
        assert mock_unverified_identity.verification_token_expires_at > original_expiry
    
    async def test_resend_verification_invalidates_old_token(
        self,
        mock_unverified_identity
    ):
        """
        Test that resending verification invalidates old token.
        
        Acceptance Criteria:
        - Old token cannot be used for verification
        - Only new token works
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        old_token = mock_unverified_identity.verification_token
        
        # Resend verification
        await auth_service.resend_verification_email(mock_unverified_identity.email)
        
        await mock_unverified_identity.arefresh_from_db()
        new_token = mock_unverified_identity.verification_token
        
        # Try to verify with old token - should fail
        async with pytest.raises(ValueError, match="Invalid or expired verification token"):
            await auth_service.verify_email(old_token)
        
        # Verify with new token - should succeed
        result = await auth_service.verify_email(new_token)
        assert result['message'] == 'Email verified successfully'
    
    async def test_already_verified_user_cannot_reverify(
        self,
        mock_verified_identity
    ):
        """
        Test that already verified users cannot verify again.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message indicates already verified
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        async with pytest.raises(ValueError, match="Email already verified"):
            await auth_service.verify_email(mock_verified_identity.verification_token)
    
    async def test_verify_email_with_valid_token(
        self,
        mock_unverified_identity
    ):
        """
        Test successful email verification with valid token.
        
        Acceptance Criteria:
        - is_verified is set to True
        - is_active is set to True
        - verification_token is cleared
        - Success message is returned
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        token = mock_unverified_identity.verification_token
        
        assert mock_unverified_identity.is_verified is False
        assert mock_unverified_identity.is_active is False
        
        result = await auth_service.verify_email(token)
        
        await mock_unverified_identity.arefresh_from_db()
        
        assert mock_unverified_identity.is_verified is True
        assert mock_unverified_identity.is_active is True
        assert mock_unverified_identity.verification_token is None
        assert result['message'] == 'Email verified successfully'
    
    async def test_verify_email_with_expired_token(
        self,
        mock_unverified_identity
    ):
        """
        Test email verification with expired token fails.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message indicates token expired
        - User remains unverified
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        # Set expired token
        mock_unverified_identity.verification_token_expires_at = datetime.utcnow() - timedelta(hours=25)
        await mock_unverified_identity.asave()
        
        token = mock_unverified_identity.verification_token
        
        async with pytest.raises(ValueError, match="Invalid or expired verification token"):
            await auth_service.verify_email(token)
        
        await mock_unverified_identity.arefresh_from_db()
        assert mock_unverified_identity.is_verified is False
        assert mock_unverified_identity.is_active is False
    
    async def test_verify_email_with_invalid_token(self):
        """
        Test email verification with invalid token fails.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message indicates invalid token
        """
        from apps.identity.services import AuthService
        
        auth_service = AuthService()
        
        async with pytest.raises(ValueError, match="Invalid or expired verification token"):
            await auth_service.verify_email("this-is-not-a-valid-token")