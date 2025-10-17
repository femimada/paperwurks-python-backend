"""
Unit tests for Identity model (US-006: User Registration).

Tests cover:
- Identity creation and validation
- Email uniqueness
- Password hashing with bcrypt
- Default field values
- Verification token generation and expiration
"""

import pytest
from datetime import datetime, timedelta
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import bcrypt
from django.utils import timezone

pytestmark = pytest.mark.unit


@pytest.mark.django_db
class TestIdentityCreation:
    """Test Identity model creation and basic field validation."""
    
    def test_identity_creation_with_valid_data(self, identity_data, mock_entity):
        """
        Test that an Identity can be created with valid data.
        
        Acceptance Criteria:
        - Identity is created successfully
        - All required fields are populated
        - ID is auto-generated
        """
        from apps.identity.models import Identity
        
        identity = Identity.objects.create(
            entity=mock_entity,
            **identity_data
        )
        
        assert identity.id is not None
        assert identity.email == identity_data['email']
        assert identity.first_name == identity_data['first_name']
        assert identity.last_name == identity_data['last_name']
        assert identity.entity == mock_entity
    
    def test_identity_email_must_be_unique(self, identity_data, mock_entity):
        """
        Test that duplicate email addresses are not allowed.
        
        Acceptance Criteria:
        - First identity with email is created successfully
        - Second identity with same email raises IntegrityError
        """
        from apps.identity.models import Identity
        
        Identity.objects.create(entity=mock_entity, **identity_data)
        
        with pytest.raises(IntegrityError):
            Identity.objects.create(entity=mock_entity, **identity_data)
    
    def test_identity_defaults_to_inactive(self, identity_data, mock_entity):
        """
        Test that newly created identities default to inactive status.
        
        Acceptance Criteria:
        - is_active field defaults to False
        """
        from apps.identity.models import Identity
        
        identity = Identity.objects.create(
            entity=mock_entity,
            **identity_data
        )
        
        assert identity.is_active is False
    
    def test_identity_defaults_to_unverified(self, identity_data, mock_entity):
        """
        Test that newly created identities default to unverified status.
        
        Acceptance Criteria:
        - is_verified field defaults to False
        """
        from apps.identity.models import Identity
        
        identity = Identity.objects.create(
            entity=mock_entity,
            **identity_data
        )
        
        assert identity.is_verified is False


@pytest.mark.django_db
class TestPasswordHashing:
    """Test password hashing functionality using bcrypt."""
    
    def test_password_is_hashed_before_save(self, identity_data, mock_entity):
        """
        Test that passwords are hashed before saving to database.
        
        Acceptance Criteria:
        - Password is not stored in plain text
        - Stored password is different from input password
        """
        from apps.identity.models import Identity
        
        plain_password = identity_data['password']
        identity = Identity.objects.create(
            entity=mock_entity,
            **identity_data
        )
        
        assert identity.password_hash != plain_password
        assert len(identity.password_hash) > 0
    
    def test_password_hash_uses_bcrypt(self, identity_data, mock_entity):
        """
        Test that bcrypt is used for password hashing.
        
        Acceptance Criteria:
        - Hashed password starts with bcrypt prefix ($2b$)
        - Password can be verified using bcrypt.checkpw()
        """
        from apps.identity.models import Identity
        
        plain_password = identity_data['password']
        identity = Identity.objects.create(
            entity=mock_entity,
            **identity_data
        )
        
        # Bcrypt hashes start with $2b$ or $2a$
        assert identity.password_hash.startswith('$2')
        
        # Verify password using bcrypt
        is_valid = bcrypt.checkpw(
            plain_password.encode('utf-8'),
            identity.password_hash.encode('utf-8')
        )
        assert is_valid is True


@pytest.mark.django_db
class TestVerificationToken:
    """Test verification token generation and expiration."""
    
    def test_verification_token_generated_on_creation(self, identity_data, mock_entity):
        """
        Test that a verification token is automatically generated.
        
        Acceptance Criteria:
        - verification_token field is populated on creation
        - Token is a non-empty string
        """
        from apps.identity.models import Identity
        
        identity = Identity.objects.create(
            entity=mock_entity,
            **identity_data
        )
        
        assert identity.verification_token is not None
        assert len(identity.verification_token) > 0
    
    def test_verification_token_expires_after_24_hours(self, identity_data, mock_entity):
        """
        Test that verification token expiration is set to 24 hours from creation.
        
        Acceptance Criteria:
        - verification_token_expires_at is set
        - Expiration is approximately 24 hours from now
        """
        from apps.identity.models import Identity
        
        before_creation = timezone.now()
        identity = Identity.objects.create(
            entity=mock_entity,
            **identity_data
        )
        after_creation = timezone.now()
        
        assert identity.verification_token_expires_at is not None
        
        # Check expiration is ~24 hours from now (allowing 1 minute tolerance)
        expected_expiry_min = before_creation + timedelta(hours=24, minutes=-1)
        expected_expiry_max = after_creation + timedelta(hours=24, minutes=1)
        
        assert expected_expiry_min <= identity.verification_token_expires_at <= expected_expiry_max


@pytest.mark.django_db
class TestIdentityStringRepresentation:
    """Test string representation and display methods."""
    
    def test_identity_str_returns_email(self, mock_identity):
        """
        Test that __str__ method returns email address.
        
        Acceptance Criteria:
        - String representation is the email address
        """
        assert str(mock_identity) == mock_identity.email
    
    def test_identity_get_full_name(self, mock_identity):
        """
        Test get_full_name method returns concatenated first and last name.
        
        Acceptance Criteria:
        - Full name is 'first_name last_name'
        """
        expected_name = f"{mock_identity.first_name} {mock_identity.last_name}"
        assert mock_identity.get_full_name() == expected_name


@pytest.mark.django_db
class TestIdentityQueryMethods:
    """Test custom query methods and managers."""
    
    def test_get_active_identities(self, identity_data, mock_entity):
        """
        Test filtering for active identities only.
        
        Acceptance Criteria:
        - Active identities are returned
        - Inactive identities are excluded
        """
        from apps.identity.models import Identity
        
        active_identity = Identity.objects.create(
            entity=mock_entity,
            is_active=True,
            **identity_data
        )
        
        inactive_data = identity_data.copy()
        inactive_data['email'] = f"inactive.{identity_data['email']}"
        Identity.objects.create(
            entity=mock_entity,
            is_active=False,
            **inactive_data
        )
        
        active_identities = Identity.objects.filter(is_active=True)
        
        assert active_identity in active_identities
        assert active_identities.count() == 1
    
    def test_get_verified_identities(self, identity_data, mock_entity):
        """
        Test filtering for verified identities only.
        
        Acceptance Criteria:
        - Verified identities are returned
        - Unverified identities are excluded
        """
        from apps.identity.models import Identity
        
        verified_identity = Identity.objects.create(
            entity=mock_entity,
            is_verified=True,
            **identity_data
        )
        
        unverified_data = identity_data.copy()
        unverified_data['email'] = f"unverified.{identity_data['email']}"
        Identity.objects.create(
            entity=mock_entity,
            is_verified=False,
            **unverified_data
        )
        
        verified_identities = Identity.objects.filter(is_verified=True)
        
        assert verified_identity in verified_identities
        assert verified_identities.count() == 1