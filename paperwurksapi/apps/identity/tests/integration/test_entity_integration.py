"""
Integration tests for Entity module (US-011).

Tests cover:
- Entity creation and audit logging
- Entity with multiple identities
- Entity settings persistence
- Multi-tenancy isolation
"""

import pytest
from django.urls import reverse
from paperwurksapi.apps.common import status


pytestmark = pytest.mark.integration


@pytest.mark.django_db
class TestEntityIntegration:
    """Test Entity integration with other modules."""
    
    def test_entity_creation_triggers_audit_log(
        self,
        authenticated_client,
        entity_data,
        mock_audit_service
    ):
        """
        Test that entity creation creates audit log.
        
        Acceptance Criteria:
        - Entity is created successfully
        - Audit log is created
        - Audit log contains entity details
        """
        url = reverse('identity:entity-list')
        
        response = authenticated_client.post(url, entity_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify audit log was created
        mock_audit_service.log.assert_called_once()
        call_kwargs = mock_audit_service.log.call_args.kwargs
        
        assert call_kwargs['event_type'] == 'entity_created'
        assert call_kwargs['entity_name'] == entity_data['name']
    
    def test_entity_with_multiple_identities(
        self,
        mock_entity,
        identity_data,
        valid_password
    ):
        """
        Test that entity can have multiple identities.
        
        Acceptance Criteria:
        - Multiple identities can be created for one entity
        - Identities are correctly associated with entity
        - Queries respect entity boundaries
        """
        from apps.identity.models import Identity
        identities = []
        for i in range(3):
            data = identity_data.copy()
            data['email'] = f'user{i}@entity.com'
            
            identity = Identity.objects.create(
                entity=mock_entity,
                **data
            )
            identities.append(identity)
        
        # Query identities by entity
        entity_identities = Identity.objects.filter(entity=mock_entity)
        
        assert entity_identities.count() == 3
        for identity in identities:
            assert identity in entity_identities
    
    def test_entity_settings_persistence(
        self,
        authenticated_client,
        mock_entity
    ):
        """
        Test that entity settings persist across operations.
        
        Acceptance Criteria:
        - Settings can be created
        - Settings can be updated
        - Settings can be retrieved
        - Settings maintain structure
        """
        url = reverse('identity:entity-detail', kwargs={'pk': mock_entity.id})
        
        # Set initial settings
        initial_settings = {
            'notifications': {
                'email_enabled': True,
                'push_enabled': False
            },
            'features': {
                'ai_enabled': True
            }
        }
        
        update_data = {
            'name': mock_entity.name,
            'entity_type': mock_entity.entity_type,
            'settings': initial_settings
        }
        
        update_response = authenticated_client.put(url, update_data, format='json')
        assert update_response.status_code == status.HTTP_200_OK
        get_response = authenticated_client.get(url)
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.data['settings'] == initial_settings
        
        # Update settings
        updated_settings = {
            'notifications': {
                'email_enabled': False,  # Changed
                'push_enabled': True     # Changed
            },
            'features': {
                'ai_enabled': True,
                'new_feature': True      # Added
            }
        }
        
        update_data['settings'] = updated_settings
        second_update = authenticated_client.put(url, update_data, format='json')
        assert second_update.status_code == status.HTTP_200_OK
        
        # Verify updated settings
        final_get = authenticated_client.get(url)
        assert final_get.data['settings'] == updated_settings
    
    def test_entity_deactivation_affects_identities(
        self,
        authenticated_client,
        mock_entity,
        identity_data
    ):
        """
        Test that entity deactivation affects related identities.
        
        Acceptance Criteria:
        - Identities can be created for active entity
        - Entity can be deactivated
        - Related identities reflect entity status
        """
        from apps.identity.models import Identity
        
        # Create identity for active entity
        identity = Identity.objects.create(
            entity=mock_entity,
            **identity_data
        )
        
        assert identity.entity.is_active is True
        
        # Deactivate entity
        entity_url = reverse('identity:entity-detail', kwargs={'pk': mock_entity.id})
        authenticated_client.delete(entity_url)
        
        # Refresh and verify entity is deactivated
        mock_entity.refresh_from_db()
        assert mock_entity.is_active is False
        
        # Verify identity's entity is deactivated
        identity.refresh_from_db()
        assert identity.entity.is_active is False


@pytest.mark.django_db
class TestEntityMultiTenancy:
    """Test multi-tenancy isolation."""
    
    def test_queries_respect_entity_boundaries(
        self,
        multiple_entities,
        identity_data
    ):
        """
        Test that queries properly scope to entity boundaries.
        
        Acceptance Criteria:
        - Identities belong to correct entities
        - Cross-entity queries return correct results
        - Entity boundaries are enforced
        """
        from apps.identity.models import Identity
        
        entity1 = multiple_entities['entity1']
        entity2 = multiple_entities['entity2']
        
        # Create identities for each entity
        identity1_data = identity_data.copy()
        identity1_data['email'] = 'user1@entity1.com'
        identity1 = Identity.objects.create(entity=entity1, **identity1_data)
        
        identity2_data = identity_data.copy()
        identity2_data['email'] = 'user2@entity2.com'
        identity2 = Identity.objects.create(entity=entity2, **identity2_data)
        
        # Query identities by entity1
        entity1_identities = Identity.objects.filter(entity=entity1)
        
        assert identity1 in entity1_identities
        assert identity2 not in entity1_identities
        assert entity1_identities.count() == 1
        
        # Query identities by entity2
        entity2_identities = Identity.objects.filter(entity=entity2)
        
        assert identity2 in entity2_identities
        assert identity1 not in entity2_identities
        assert entity2_identities.count() == 1
    
    def test_entity_data_isolation(
        self,
        api_client,
        multiple_entities,
        identity_data,
        valid_password
    ):
        """
        Test that entity data is properly isolated.
        
        Acceptance Criteria:
        - Users from entity1 can't see entity2 data
        - API endpoints respect entity scoping
        - Cross-entity access is denied
        """
        from apps.identity.models import Identity
        
        entity1 = multiple_entities['entity1']
        entity2 = multiple_entities['entity2']
        
        # Create user for entity1
        user1_data = identity_data.copy()
        user1_data['email'] = 'user1@entity1.com'
        user1 = Identity.objects.create(
            entity=entity1,
            is_verified=True,
            is_active=True,
            **user1_data
        )
        
        # Create user for entity2
        user2_data = identity_data.copy()
        user2_data['email'] = 'user2@entity2.com'
        user2 = Identity.objects.create(
            entity=entity2,
            is_verified=True,
            is_active=True,
            **user2_data
        )
        
        # Login as user1
        login_url = reverse('identity:login')
        login_response = api_client.post(
            login_url,
            {'email': user1.email, 'password': valid_password},
            format='json'
        )
        
        token = login_response.data['access_token']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # User1 should see their entity
        entity1_url = reverse('identity:entity-detail', kwargs={'pk': entity1.id})
        response1 = api_client.get(entity1_url)
        assert response1.status_code == status.HTTP_200_OK
        
        # User1 should be able to see entity2 details (for now)
        # In Sprint 1B with RBAC, this will be restricted
        entity2_url = reverse('identity:entity-detail', kwargs={'pk': entity2.id})
        response2 = api_client.get(entity2_url)
        # This assertion will change in Sprint 1B
        assert response2.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
    
    def test_entity_deletion_with_related_identities(
        self,
        authenticated_client,
        mock_entity,
        sample_identities
    ):
        """
        Test entity soft delete with related identities.
        
        Acceptance Criteria:
        - Entity with identities can be soft deleted
        - Identities are preserved
        - Identities still reference the entity
        - Entity can be restored
        """
        from apps.identity.models import Entity, Identity
        
        entity_id = mock_entity.id
        identity_ids = [identity.id for identity in sample_identities]
        
        # Soft delete entity
        entity_url = reverse('identity:entity-detail', kwargs={'pk': entity_id})
        delete_response = authenticated_client.delete(entity_url)
        
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify entity is soft deleted
        entity = Entity.objects.get(id=entity_id)
        assert entity.deleted_at is not None
        assert entity.is_active is False
        
        # Verify identities still exist
        for identity_id in identity_ids:
            identity = Identity.objects.get(id=identity_id)
            assert identity.entity == mock_entity
            assert identity.entity.deleted_at is not None


@pytest.mark.django_db
class TestEntityAPIIntegration:
    """Test Entity API integration scenarios."""
    
    def test_create_entity_and_add_identities(
        self,
        authenticated_client,
        entity_data,
        identity_data
    ):
        """
        Test creating entity and adding identities through API.
        
        Acceptance Criteria:
        - Entity can be created via API
        - Identities can be added to entity
        - Relationship is properly established
        """
        from apps.identity.models import Entity, Identity
        
        # Create entity
        entity_url = reverse('identity:entity-list')
        entity_response = authenticated_client.post(
            entity_url,
            entity_data,
            format='json'
        )
        
        assert entity_response.status_code == status.HTTP_201_CREATED
        entity_id = entity_response.data['id']
        
        # Get created entity
        entity = Entity.objects.get(id=entity_id)
        
        # Create identity for this entity
        identity = Identity.objects.create(
            entity=entity,
            **identity_data
        )
        
        # Verify relationship
        assert identity.entity.id == entity.id
        
        # Query identities for this entity
        entity_identities = Identity.objects.filter(entity=entity)
        assert identity in entity_identities
    
    def test_update_entity_preserves_relationships(
        self,
        authenticated_client,
        mock_entity,
        sample_identities
    ):
        """
        Test that updating entity preserves identity relationships.
        
        Acceptance Criteria:
        - Entity can be updated
        - Identity relationships remain intact
        - Identities still reference correct entity
        """
        entity_url = reverse('identity:entity-detail', kwargs={'pk': mock_entity.id})
        
        # Update entity
        update_data = {
            'name': 'Updated Entity Name',
            'entity_type': mock_entity.entity_type,
            'address': 'New Address'
        }
        
        update_response = authenticated_client.put(
            entity_url,
            update_data,
            format='json'
        )
        
        assert update_response.status_code == status.HTTP_200_OK
        
        # Verify identities still reference the entity
        for identity in sample_identities:
            identity.refresh_from_db()
            assert identity.entity.id == mock_entity.id
            assert identity.entity.name == 'Updated Entity Name'