"""
Service layer tests for EntityService (US-011).

Tests cover:
- Entity creation and management
- Settings management
- Activation/deactivation
- Soft delete functionality
"""

import pytest
from datetime import datetime
from uuid import uuid4


# Mark all tests in this module as async and unit tests
pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.mark.django_db(transaction=True)
class TestEntityService:
    """Test EntityService methods."""
    
    async def test_create_entity_with_valid_data(
        self,
        entity_data,
        mock_audit_service
    ):
        """
        Test that EntityService creates entity with valid data.
        
        Acceptance Criteria:
        - Entity is created successfully
        - All fields are populated correctly
        - Entity object is returned
        """
        from apps.identity.services import EntityService
        
        entity_service = EntityService()
        entity = await entity_service.create_entity(**entity_data)
        
        assert entity is not None
        assert entity.name == entity_data['name']
        assert entity.entity_type == entity_data['entity_type']
        assert entity.address == entity_data['address']
        assert entity.postcode == entity_data['postcode']
        assert entity.settings == entity_data['settings']
        assert entity.is_active is True
    
    async def test_create_entity_creates_audit_log(
        self,
        entity_data,
        mock_audit_service
    ):
        """
        Test that entity creation creates audit log.
        
        Acceptance Criteria:
        - AuditService is called
        - Event type is 'entity_created'
        - Entity ID and name are logged
        """
        from apps.identity.services import EntityService
        
        entity_service = EntityService()
        entity = await entity_service.create_entity(**entity_data)
        
        mock_audit_service.log.assert_awaited_once()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        
        assert call_kwargs['event_type'] == 'entity_created'
        assert call_kwargs['entity_id'] == entity.id
        assert call_kwargs['entity_name'] == entity.name
    
    async def test_create_entity_with_default_settings(
        self,
        mock_audit_service
    ):
        """
        Test that entity can be created without custom settings.
        
        Acceptance Criteria:
        - Entity is created with empty settings dict
        - Settings field is properly initialized
        """
        from apps.identity.services import EntityService
        
        entity_service = EntityService()
        entity = await entity_service.create_entity(
            name="Test Entity",
            entity_type="estate_agency"
        )
        
        assert entity.settings == {}
        assert isinstance(entity.settings, dict)
    
    async def test_update_entity_settings(
        self,
        mock_entity,
        mock_audit_service
    ):
        """
        Test that entity settings can be updated.
        
        Acceptance Criteria:
        - Settings are updated successfully
        - Changes are persisted to database
        - Audit log is created
        """
        from apps.identity.services import EntityService
        
        new_settings = {
            'notifications': {
                'email_enabled': False
            },
            'new_feature': {
                'enabled': True
            }
        }
        
        entity_service = EntityService()
        updated_entity = await entity_service.update_settings(
            entity_id=mock_entity.id,
            settings=new_settings
        )
        
        assert updated_entity.settings == new_settings
        
        # Verify audit log
        mock_audit_service.log.assert_awaited_once()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        assert call_kwargs['event_type'] == 'entity_settings_updated'
    
    async def test_deactivate_entity(
        self,
        mock_entity,
        mock_audit_service
    ):
        """
        Test that entity can be deactivated.
        
        Acceptance Criteria:
        - is_active is set to False
        - Changes are persisted
        - Audit log is created
        """
        from apps.identity.services import EntityService
        
        assert mock_entity.is_active is True
        
        entity_service = EntityService()
        deactivated_entity = await entity_service.deactivate(mock_entity.id)
        
        assert deactivated_entity.is_active is False
        
        # Verify audit log
        mock_audit_service.log.assert_awaited_once()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        assert call_kwargs['event_type'] == 'entity_deactivated'
    
    async def test_activate_entity(
        self,
        mock_entity,
        mock_audit_service
    ):
        """
        Test that entity can be activated.
        
        Acceptance Criteria:
        - is_active is set to True
        - Changes are persisted
        - Audit log is created
        """
        from apps.identity.services import EntityService
        
        # First deactivate
        mock_entity.is_active = False
        await mock_entity.asave()
        
        entity_service = EntityService()
        activated_entity = await entity_service.activate(mock_entity.id)
        
        assert activated_entity.is_active is True
        
        # Verify audit log
        mock_audit_service.log.assert_awaited_once()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        assert call_kwargs['event_type'] == 'entity_activated'
    
    async def test_delete_entity_soft_deletes(
        self,
        mock_entity,
        mock_audit_service
    ):
        """
        Test that entity deletion is soft delete.
        
        Acceptance Criteria:
        - deleted_at timestamp is set
        - is_active is set to False
        - Entity still exists in database
        - Audit log is created
        """
        from apps.identity.services import EntityService
        from apps.identity.models import Entity
        
        entity_id = mock_entity.id
        
        assert mock_entity.deleted_at is None
        assert mock_entity.is_active is True
        
        entity_service = EntityService()
        await entity_service.delete(entity_id)
        
        # Refresh entity from database
        await mock_entity.arefresh_from_db()
        
        assert mock_entity.deleted_at is not None
        assert isinstance(mock_entity.deleted_at, datetime)
        assert mock_entity.is_active is False
        
        # Verify entity still exists
        assert await Entity.objects.filter(id=entity_id).aexists()
        
        # Verify audit log
        mock_audit_service.log.assert_awaited_once()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        assert call_kwargs['event_type'] == 'entity_deleted'


@pytest.mark.django_db(transaction=True)
class TestEntityServiceQueryMethods:
    """Test EntityService query and retrieval methods."""
    
    async def test_get_entity_by_id(self, mock_entity):
        """
        Test retrieving entity by ID.
        
        Acceptance Criteria:
        - Correct entity is returned
        - All fields are populated
        """
        from apps.identity.services import EntityService
        
        entity_service = EntityService()
        entity = await entity_service.get_by_id(mock_entity.id)
        
        assert entity.id == mock_entity.id
        assert entity.name == mock_entity.name
    
    async def test_get_entity_by_id_not_found(self):
        """
        Test that getting non-existent entity raises error.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message indicates entity not found
        """
        from apps.identity.services import EntityService
        
        entity_service = EntityService()
        
        async with pytest.raises(ValueError, match="Entity not found"):
            await entity_service.get_by_id(uuid4())
    
    async def test_list_active_entities(self, entity_data):
        """
        Test listing only active entities.
        
        Acceptance Criteria:
        - Only active entities are returned
        - Inactive entities are excluded
        """
        from apps.identity.services import EntityService
        from apps.identity.models import Entity
        
        # Create active entity
        active_entity = await Entity.objects.acreate(
            name="Active Entity",
            entity_type="estate_agency",
            is_active=True
        )
        
        # Create inactive entity
        await Entity.objects.acreate(
            name="Inactive Entity",
            entity_type="law_firm",
            is_active=False
        )
        
        entity_service = EntityService()
        active_entities = await entity_service.list_active()
        
        # Asynchronously iterate over the queryset to build the list
        entity_ids = [e.id async for e in active_entities]
        inactive_count = len([e async for e in active_entities if not e.is_active])
        
        assert active_entity.id in entity_ids
        assert inactive_count == 0
    
    async def test_list_entities_by_type(self):
        """
        Test filtering entities by type.
        
        Acceptance Criteria:
        - Only entities of specified type are returned
        - Other types are excluded
        """
        from apps.identity.services import EntityService
        from apps.identity.models import Entity
        
        # Create entities of different types
        agency = await Entity.objects.acreate(
            name="Test Agency",
            entity_type="estate_agency"
        )
        
        firm = await Entity.objects.acreate(
            name="Test Firm",
            entity_type="law_firm"
        )
        
        entity_service = EntityService()
        
        agencies = await entity_service.list_by_type("estate_agency")
        firms = await entity_service.list_by_type("law_firm")
        
        # Asynchronously build ID lists from querysets
        agency_ids = [e.id async for e in agencies]
        firm_ids = [e.id async for e in firms]
        
        assert agency.id in agency_ids
        assert firm.id not in agency_ids
        assert firm.id in firm_ids
        assert agency.id not in firm_ids


@pytest.mark.django_db(transaction=True)
class TestEntityServiceValidation:
    """Test EntityService validation logic."""
    
    async def test_create_entity_validates_duplicate_name(
        self,
        mock_entity
    ):
        """
        Test that duplicate entity names are rejected.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message indicates duplicate name
        """
        from apps.identity.services import EntityService
        
        entity_service = EntityService()
        
        async with pytest.raises(ValueError, match="Entity with this name already exists"):
            await entity_service.create_entity(
                name=mock_entity.name,
                entity_type="law_firm"
            )
    
    async def test_create_entity_validates_entity_type(self):
        """
        Test that invalid entity types are rejected.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message indicates invalid type
        """
        from apps.identity.services import EntityService
        
        entity_service = EntityService()
        
        async with pytest.raises(ValueError, match="Invalid entity type"):
            await entity_service.create_entity(
                name="Test Entity",
                entity_type="invalid_type"
            )
    
    async def test_update_settings_validates_entity_exists(self):
        """
        Test that updating settings for non-existent entity fails.
        
        Acceptance Criteria:
        - ValueError is raised
        - Error message indicates entity not found
        """
        from apps.identity.services import EntityService
        
        entity_service = EntityService()
        
        async with pytest.raises(ValueError, match="Entity not found"):
            await entity_service.update_settings(
                entity_id=uuid4(),
                settings={'test': 'value'}
            )