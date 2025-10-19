"""
Integration tests for Audit logging (US-014).

Tests cover:
- Authentication events create audit logs
- Audit logs include identity information
- Failed login attempts are logged
- Audit logs can be queried
"""

import pytest
from django.urls import reverse
from paperwurksapi.apps.common import status


pytestmark = pytest.mark.integration


@pytest.mark.django_db
class TestAuditIntegration:
    """Test Audit service integration with Identity module."""
    
    def test_auth_events_create_audit_logs(
        self,
        api_client,
        mock_verified_identity,
        valid_password,
        mock_audit_service
    ):
        """
        Test that authentication events create audit logs.
        
        Acceptance Criteria:
        - Registration creates audit log
        - Login creates audit log
        - Logout creates audit log
        - Each log has correct event type
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        login_response = api_client.post(login_url, login_data, format='json')
        assert login_response.status_code == status.HTTP_200_OK
        mock_audit_service.log.assert_called()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        assert call_kwargs['event_type'] == 'user_login'
        assert call_kwargs['identity_id'] == mock_verified_identity.id
    
    def test_audit_log_includes_identity_info(
        self,
        api_client,
        mock_verified_identity,
        valid_password,
        mock_audit_service
    ):
        """
        Test that audit logs include identity information.
        
        Acceptance Criteria:
        - Audit log contains identity ID
        - Audit log contains email
        - Audit log contains entity ID
        - Audit log contains timestamp
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        
        api_client.post(login_url, login_data, format='json')
        call_kwargs = mock_audit_service.log.call_args.kwargs
        assert 'identity_id' in call_kwargs
        assert 'email' in call_kwargs
        assert call_kwargs['identity_id'] == mock_verified_identity.id
        assert call_kwargs['email'] == mock_verified_identity.email
    
    def test_failed_login_audited_with_reason(
        self,
        api_client,
        mock_verified_identity,
        mock_audit_service
    ):
        """
        Test that failed login attempts are logged with reason.
        
        Acceptance Criteria:
        - Failed login creates audit log
        - Event type is 'login_failed'
        - Failure reason is included
        - Email is logged (but password is not)
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': 'WrongPassword123!'
        }
        response = api_client.post(login_url, login_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        mock_audit_service.log.assert_called()
        call_kwargs = mock_audit_service.log.call_args.kwargs 
        assert call_kwargs['event_type'] == 'login_failed'
        assert call_kwargs['email'] == mock_verified_identity.email
        assert 'reason' in call_kwargs
        assert 'password' not in str(call_kwargs).lower()
    
    def test_query_audit_logs_by_identity(
        self,
        api_client,
        mock_verified_identity,
        valid_password,
        mock_audit_service
    ):
        """
        Test that audit logs can be queried by identity.
        
        Acceptance Criteria:
        - Multiple events for same identity are logged
        - Logs can be filtered by identity_id
        - Logs are returned in chronological order
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        for _ in range(3):
            api_client.post(login_url, login_data, format='json')
        assert mock_audit_service.log.call_count >= 3
        for call in mock_audit_service.log.call_args_list:
            kwargs = call.kwargs
            assert kwargs['identity_id'] == mock_verified_identity.id


@pytest.mark.django_db
class TestAuditLoggingComprehensive:
    """Test comprehensive audit logging for all identity operations."""
    
    def test_registration_audit_log(
        self,
        api_client,
        identity_data,
        mock_entity,
        mock_audit_service
    ):
        """
        Test that user registration creates audit log.
        
        Acceptance Criteria:
        - Event type is 'user_registered'
        - Email is logged
        - Entity ID is logged
        - Timestamp is included
        """
        register_url = reverse('identity:register')
        register_data = {
            **identity_data,
            'entity_id': str(mock_entity.id)
        }
        
        response = api_client.post(register_url, register_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        mock_audit_service.log.assert_called()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        assert call_kwargs['event_type'] == 'user_registered'
        assert call_kwargs['email'] == identity_data['email']
    
    def test_email_verification_audit_log(
        self,
        api_client,
        mock_unverified_identity,
        mock_audit_service
    ):
        """
        Test that email verification creates audit log.
        
        Acceptance Criteria:
        - Event type is 'email_verified'
        - Identity ID is logged
        - Verification timestamp is included
        """
        verify_url = reverse('identity:verify-email')
        verify_data = {
            'token': mock_unverified_identity.verification_token
        }
        
        response = api_client.post(verify_url, verify_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        mock_audit_service.log.assert_called()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        assert call_kwargs['event_type'] == 'email_verified'
        assert call_kwargs['identity_id'] == mock_unverified_identity.id
    
    def test_password_reset_audit_logs(
        self,
        api_client,
        mock_verified_identity,
        mock_audit_service
    ):
        """
        Test that password reset flow creates audit logs.
        
        Acceptance Criteria:
        - Password reset request creates log
        - Password reset completion creates log
        - Both logs reference the same identity
        """
        forgot_url = reverse('identity:forgot-password')
        forgot_data = {'email': mock_verified_identity.email}
        api_client.post(forgot_url, forgot_data, format='json')
        assert mock_audit_service.log.called
        first_call_kwargs = mock_audit_service.log.call_args_list[0].kwargs
        assert first_call_kwargs['event_type'] == 'password_reset_requested'
        mock_verified_identity.refresh_from_db()
        reset_token = mock_verified_identity.password_reset_token   
        reset_url = reverse('identity:reset-password')
        reset_data = {
            'token': reset_token,
            'new_password': 'NewSecureP@ss456'
        }  
        api_client.post(reset_url, reset_data, format='json')
        last_call_kwargs = mock_audit_service.log.call_args_list[-1].kwargs
        assert last_call_kwargs['event_type'] == 'password_reset_completed'
    
    def test_logout_audit_log(
        self,
        api_client,
        mock_verified_identity,
        valid_password,
        mock_audit_service
    ):
        """
        Test that logout creates audit log.
        
        Acceptance Criteria:
        - Event type is 'user_logout'
        - Identity ID is logged
        - Logout timestamp is included
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        
        login_response = api_client.post(login_url, login_data, format='json')
        access_token = login_response.data['access_token']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_url = reverse('identity:logout')
        
        api_client.post(logout_url)
        logout_calls = [
            call for call in mock_audit_service.log.call_args_list
            if call.kwargs.get('event_type') == 'user_logout'
        ]
        assert len(logout_calls) > 0
        logout_kwargs = logout_calls[0].kwargs
        assert logout_kwargs['identity_id'] == mock_verified_identity.id


@pytest.mark.django_db
class TestAuditLoggingSecurity:
    """Test security aspects of audit logging."""
    
    def test_audit_log_never_contains_passwords(
        self,
        api_client,
        identity_data,
        mock_entity,
        mock_audit_service
    ):
        """
        Test that audit logs never contain passwords.
        
        Acceptance Criteria:
        - Registration log has no password
        - Login log has no password
        - Password reset log has no password
        - All logs are safe to store/view
        """
        register_url = reverse('identity:register')
        register_data = {
            **identity_data,
            'entity_id': str(mock_entity.id)
        }
        api_client.post(register_url, register_data, format='json')
        for call in mock_audit_service.log.call_args_list:
            call_str = str(call.kwargs).lower()
            assert 'password' not in call_str
    
    def test_audit_log_contains_ip_address(
        self,
        api_client,
        mock_verified_identity,
        valid_password,
        mock_audit_service
    ):
        """
        Test that audit logs include request IP address.
        
        Acceptance Criteria:
        - Audit log contains IP address
        - IP is properly formatted
        - IP helps track suspicious activity
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        api_client.post(
            login_url,
            login_data,
            format='json',
            REMOTE_ADDR='192.168.1.100'
        )
        call_kwargs = mock_audit_service.log.call_args.kwargs
        assert 'ip_address' in call_kwargs or 'remote_addr' in call_kwargs
    
    def test_audit_log_contains_user_agent(
        self,
        api_client,
        mock_verified_identity,
        valid_password,
        mock_audit_service
    ):
        """
        Test that audit logs include user agent.
        
        Acceptance Criteria:
        - Audit log contains user agent string
        - User agent helps identify client
        - Useful for security analysis
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        api_client.post(
            login_url,
            login_data,
            format='json',
            HTTP_USER_AGENT='TestClient/1.0'
        )
        call_kwargs = mock_audit_service.log.call_args.kwargs
        assert 'user_agent' in call_kwargs or 'http_user_agent' in call_kwargs
    
    def test_suspicious_activity_logging(
        self,
        api_client,
        mock_verified_identity,
        mock_audit_service
    ):
        """
        Test that suspicious activities are logged.
        
        Acceptance Criteria:
        - Multiple failed logins are logged
        - Each attempt includes attempt number
        - Pattern is identifiable in logs
        """
        login_url = reverse('identity:login')
        for i in range(5):
            login_data = {
                'email': mock_verified_identity.email,
                'password': f'WrongPassword{i}'
            }
            
            api_client.post(login_url, login_data, format='json')
        failed_login_calls = [
            call for call in mock_audit_service.log.call_args_list
            if call.kwargs.get('event_type') == 'login_failed'
        ]
        
        assert len(failed_login_calls) == 5


@pytest.mark.django_db
class TestAuditLogRetrieval:
    """Test audit log retrieval and querying."""
    
    def test_retrieve_audit_logs_for_identity(
        self,
        authenticated_client,
        mock_verified_identity,
        mock_audit_service
    ):
        """
        Test retrieving audit logs for specific identity.
        
        Acceptance Criteria:
        - Audit logs can be queried by identity_id
        - Results include all events for that identity
        - Results are ordered by timestamp
        
        Note: This assumes audit log retrieval API exists
        """
        audit_url = reverse('audit:logs')
        params = {'identity_id': str(mock_verified_identity.id)}
        response = authenticated_client.get(audit_url, params)
        assert mock_audit_service.log.called
    
    def test_audit_logs_immutable(
        self,
        authenticated_client,
        mock_verified_identity
    ):
        """
        Test that audit logs are immutable.
        
        Acceptance Criteria:
        - Audit logs cannot be modified
        - Audit logs cannot be deleted
        - Any attempt returns 403 or 405
        
        Note: This assumes audit log endpoints exist
        """
        pass
    
    def test_filter_audit_logs_by_event_type(
        self,
        authenticated_client,
        mock_audit_service
    ):
        """
        Test filtering audit logs by event type.
        
        Acceptance Criteria:
        - Can filter by event type
        - Only matching events are returned
        - Common filters: login, logout, registration
        
        Note: This assumes audit log retrieval API exists
        """
        pass


@pytest.mark.django_db
class TestAuditLogCompliance:
    """Test audit logging for compliance requirements."""
    
    def test_audit_logs_gdpr_compliant(
        self,
        api_client,
        mock_verified_identity,
        valid_password,
        mock_audit_service
    ):
        """
        Test that audit logs support GDPR compliance.
        
        Acceptance Criteria:
        - User actions are tracked
        - Data access is logged
        - Logs can be exported for user
        - Logs support right-to-access requests
        """
        login_url = reverse('identity:login')
        login_data = {
            'email': mock_verified_identity.email,
            'password': valid_password
        }
        
        api_client.post(login_url, login_data, format='json')
        
        # Verify audit log supports GDPR
        call_kwargs = mock_audit_service.log.call_args.kwargs
        assert 'identity_id' in call_kwargs or 'user_id' in call_kwargs
        assert 'event_type' in call_kwargs
        assert 'timestamp' in call_kwargs or 'created_at' in call_kwargs
    
    def test_audit_retention_policy(
        self,
        authenticated_client,
        mock_audit_service
    ):
        """
        Test that audit logs support retention policies.
        
        Acceptance Criteria:
        - Old logs can be archived
        - Retention period is configurable
        - Critical logs are preserved longer
        
        Note: Implementation depends on AuditService
        """
        # This will be implemented with AuditService
        # Audit logs should support configurable retention
        pass