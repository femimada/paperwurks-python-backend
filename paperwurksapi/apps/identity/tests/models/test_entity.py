"""
Unit tests for Entity model (US-011: Entity Model).

Tests cover:
- Entity creation and validation
- Name uniqueness
- Entity type validation
- Default values and settings
- Soft delete functionality
- Multi-tenancy scoping
"""

import pytest
from django.db import IntegrityError
from datetime import datetime


pytestmark = pytest.mark.unit


@pytest.mark.django_db
class TestEntityCreation:
    """Test Entity model creation and basic validation."""
    
    def test_entity_creation_with_required_fields(self, entity_data):
        """
        Test that an Entity can be created with required fields only.
        
        Acceptance Criteria:
        - Entity is created successfully with minimal data
        - ID is auto-generated
        - Required fields are populated
        """
        from apps.identity.models import Entity
        
        entity = Entity.objects.create(
            name=entity_data['name'],
            entity_type=entity_data['entity_type']
        )
        
        assert entity.id is not None
        assert entity.name == entity_data['name']
        assert entity.entity_type == entity_data['entity_type']
    
    def test_entity_name_must_be_unique(self, entity_data):
        """
        Test that duplicate entity names are not allowed.
        
        Acceptance Criteria:
        - First entity with name is created successfully
        - Second entity with same name raises IntegrityError
        """
        from apps.identity.models import Entity
        
        Entity.objects.create(
            name=entity_data['name'],
            entity_type=entity_data['entity_type']
        )
        
        with pytest.raises(IntegrityError):
            Entity.objects.create(
                name=entity_data['name'],
                entity_type='law_firm'
            )
    
    def test_entity_type_must_be_valid_choice(self, entity_data):
        """
        Test that entity_type must be one of the allowed choices.
        
        Acceptance Criteria:
        - Valid entity types are accepted
        - Invalid entity types raise ValidationError
        """
        from apps.identity.models import Entity
        from django.core.exceptions import ValidationError
        
        # Valid entity types should work
        valid_types = ['estate_agency', 'law_firm', 'individual']
        for entity_type in valid_types:
            entity = Entity.objects.create(
                name=f"Test {entity_type}",
                entity_type=entity_type
            )
            assert entity.entity_type == entity_type
        
        # Invalid entity type should fail validation
        entity = Entity(
            name="Invalid Type Entity",
            entity_type='invalid_type'
        )
        
        with pytest.raises(ValidationError):
            entity.full_clean()
    
    def test_entity_defaults_to_active(self, entity_data):
        """
        Test that newly created entities default to active status.
        
        Acceptance Criteria:
        - is_active field defaults to True
        """
        from apps.identity.models import Entity
        
        entity = Entity.objects.create(
            name=entity_data['name'],
            entity_type=entity_data['entity_type']
        )
        
        assert entity.is_active is True
    
    def test_entity_settings_default_to_empty_dict(self):
        """
        Test that settings field defaults to an empty dictionary.
        
        Acceptance Criteria:
        - settings field is a dictionary
        - settings is empty by default
        """
        from apps.identity.models import Entity
        
        entity = Entity.objects.create(
            name="Test Entity",
            entity_type='estate_agency'
        )
        
        assert isinstance(entity.settings, dict)
        assert entity.settings == {}


@pytest.mark.django_db
class TestEntitySettings:
    """Test Entity settings JSON field management."""
    
    def test_entity_creation_with_settings(self, entity_data):
        """
        Test that Entity can be created with complex settings.
        
        Acceptance Criteria:
        - Settings JSON field accepts nested dictionaries
        - Settings are persisted correctly
        """
        from apps.identity.models import Entity
        
        entity = Entity.objects.create(**entity_data)
        
        assert entity.settings == entity_data['settings']
        assert entity.settings['notifications']['email_enabled'] is True
        assert entity.settings['compliance']['require_solicitor_signoff'] is True
    
    def test_entity_settings_can_be_updated(self, mock_entity):
        """
        Test that Entity settings can be updated.
        
        Acceptance Criteria:
        - Settings can be modified
        - Changes are persisted to database
        """
        new_settings = {
            'notifications': {
                'email_enabled': False,
                'push_enabled': False
            }
        }
        
        mock_entity.settings = new_settings
        mock_entity.save()
        mock_entity.refresh_from_db()
        
        assert mock_entity.settings == new_settings
        assert mock_entity.settings['notifications']['email_enabled'] is False


@pytest.mark.django_db
class TestEntitySoftDelete:
    """Test Entity soft delete functionality."""
    
    def test_entity_soft_delete(self, mock_entity):
        """
        Test that Entity can be soft deleted.
        
        Acceptance Criteria:
        - deleted_at timestamp is set
        - Entity is not actually removed from database
        - is_active is set to False
        """
        assert mock_entity.deleted_at is None
        assert mock_entity.is_active is True
        
        mock_entity.soft_delete()
        
        assert mock_entity.deleted_at is not None
        assert isinstance(mock_entity.deleted_at, datetime)
        assert mock_entity.is_active is False
        
        # Verify entity still exists in database
        from apps.identity.models import Entity
        assert Entity.objects.filter(id=mock_entity.id).exists()
    
    def test_entity_restore_from_soft_delete(self, mock_entity):
        """
        Test that soft deleted Entity can be restored.
        
        Acceptance Criteria:
        - deleted_at is set to None
        - is_active is set to True
        """
        mock_entity.soft_delete()
        assert mock_entity.deleted_at is not None
        
        mock_entity.restore()
        
        assert mock_entity.deleted_at is None
        assert mock_entity.is_active is True


@pytest.mark.django_db
class TestEntityStringRepresentation:
    """Test Entity string representation."""
    
    def test_entity_string_representation(self, mock_entity):
        """
        Test that __str__ method returns entity name.
        
        Acceptance Criteria:
        - String representation is the entity name
        """
        assert str(mock_entity) == mock_entity.name


@pytest.mark.django_db
class TestEntityQueryMethods:
    """Test Entity query methods and filtering."""
    
    def test_entity_get_active_entities(self, entity_data):
        """
        Test filtering for active entities only.
        
        Acceptance Criteria:
        - Active entities are returned
        - Inactive entities are excluded
        """
        from apps.identity.models import Entity
        
        active_entity = Entity.objects.create(
            name="Active Entity",
            entity_type='estate_agency',
            is_active=True
        )
        
        Entity.objects.create(
            name="Inactive Entity",
            entity_type='law_firm',
            is_active=False
        )
        
        active_entities = Entity.objects.filter(is_active=True)
        
        assert active_entity in active_entities
        assert active_entities.count() == 1
    
    def test_entity_filter_by_type(self):
        """
        Test filtering entities by entity_type.
        
        Acceptance Criteria:
        - Entities of specified type are returned
        - Other types are excluded
        """
        from apps.identity.models import Entity
        
        estate_agency = Entity.objects.create(
            name="Test Agency",
            entity_type='estate_agency'
        )
        
        law_firm = Entity.objects.create(
            name="Test Law Firm",
            entity_type='law_firm'
        )
        
        agencies = Entity.objects.filter(entity_type='estate_agency')
        firms = Entity.objects.filter(entity_type='law_firm')
        
        assert estate_agency in agencies
        assert law_firm not in agencies
        assert law_firm in firms
        assert estate_agency not in firms


@pytest.mark.django_db
class TestEntityMultiTenancy:
    """Test Entity multi-tenancy scoping."""
    
    def test_entities_are_isolated(self, multiple_entities, identity_data):
        """
        Test that identities are correctly scoped to their entities.
        
        Acceptance Criteria:
        - Identities belong to their respective entities
        - Queries respect entity boundaries
        """
        from apps.identity.models import Identity
        
        entity1 = multiple_entities['entity1']
        entity2 = multiple_entities['entity2']
        
        identity1 = Identity.objects.create(
            entity=entity1,
            email="user1@entity1.com",
            **{k: v for k, v in identity_data.items() if k != 'email'}
        )
        
        identity2 = Identity.objects.create(
            entity=entity2,
            email="user2@entity2.com",
            **{k: v for k, v in identity_data.items() if k != 'email'}
        )
        
        entity1_identities = Identity.objects.filter(entity=entity1)
        entity2_identities = Identity.objects.filter(entity=entity2)
        
        assert identity1 in entity1_identities
        assert identity2 not in entity1_identities
        assert identity2 in entity2_identities
        assert identity1 not in entity2_identities
    
    def test_entity_deletion_handling(self, mock_entity, identity_data):
        """
        Test that entity deletion is handled appropriately.
        
        Acceptance Criteria:
        - Soft delete prevents entity removal
        - Related identities are not affected by soft delete
        """
        from apps.identity.models import Identity
        
        identity = Identity.objects.create(
            entity=mock_entity,
            **identity_data
        )
        
        mock_entity.soft_delete()
        identity.refresh_from_db()
        
        # Identity should still exist and reference the soft-deleted entity
        assert identity.entity == mock_entity
        assert mock_entity.deleted_at is not None