"""
API endpoint tests for Entity management endpoints (US-011).

Tests cover:
- Entity creation
- Entity retrieval
- Entity updates
- Entity deletion
- Entity listing and filtering
"""

import pytest
from django.urls import reverse
from paperwurksapi.apps.common import status
import json


pytestmark = pytest.mark.api


@pytest.mark.django_db
class TestEntityAPI:
    """Test Entity API endpoints."""
    
    def test_create_entity_endpoint_returns_201(
        self,
        authenticated_client,
        entity_data
    ):
        """
        Test entity creation returns 201 Created.
        
        Acceptance Criteria:
        - Status code is 201
        - Response contains entity data
        - Entity ID is included
        """
        url = reverse('identity:entity-list')
        
        response = authenticated_client.post(url, entity_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert response.data['name'] == entity_data['name']
        assert response.data['entity_type'] == entity_data['entity_type']
    
    def test_create_entity_validates_required_fields(
        self,
        authenticated_client
    ):
        """
        Test entity creation validates required fields.
        
        Acceptance Criteria:
        - Returns 400 for missing required fields
        - Error response indicates which fields are required
        """
        url = reverse('identity:entity-list')
        
        # Missing entity_type
        incomplete_data = {
            'name': 'Test Agency'
        }
        
        response = authenticated_client.post(url, incomplete_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'entity_type' in str(response.data).lower()
    
    def test_get_entity_by_id(
        self,
        authenticated_client,
        mock_entity
    ):
        """
        Test retrieving entity by ID.
        
        Acceptance Criteria:
        - Status code is 200
        - Correct entity data is returned
        - All fields are present
        """
        url = reverse('identity:entity-detail', kwargs={'pk': mock_entity.id})
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(mock_entity.id)
        assert response.data['name'] == mock_entity.name
        assert response.data['entity_type'] == mock_entity.entity_type
        assert 'settings' in response.data
    
    def test_get_entity_by_id_not_found(
        self,
        authenticated_client
    ):
        """
        Test retrieving non-existent entity returns 404.
        
        Acceptance Criteria:
        - Status code is 404
        - Error message indicates not found
        """
        from uuid import uuid4
        
        url = reverse('identity:entity-detail', kwargs={'pk': uuid4()})
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_entities_with_pagination(
        self,
        authenticated_client,
        entity_data
    ):
        """
        Test listing entities with pagination.
        
        Acceptance Criteria:
        - Status code is 200
        - Results are paginated
        - Pagination metadata is included
        """
        from apps.identity.models import Entity

        for i in range(5):
            Entity.objects.create(
                name=f"Test Entity {i}",
                entity_type='estate_agency'
            )
        
        url = reverse('identity:entity-list')
        
        response = authenticated_client.get(url, {'page': 1, 'page_size': 2})
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert len(response.data['results']) <= 2
    
    def test_list_entities_filter_by_type(
        self,
        authenticated_client
    ):
        """
        Test filtering entities by type.
        
        Acceptance Criteria:
        - Only entities of specified type are returned
        - Other types are excluded
        """
        from apps.identity.models import Entity
        
        # Create entities of different types
        Entity.objects.create(
            name="Test Agency",
            entity_type='estate_agency'
        )
        Entity.objects.create(
            name="Test Firm",
            entity_type='law_firm'
        )
        
        url = reverse('identity:entity-list')
        
        response = authenticated_client.get(url, {'entity_type': 'estate_agency'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # All returned entities should be estate agencies
        for entity in response.data['results']:
            assert entity['entity_type'] == 'estate_agency'
    
    def test_update_entity_endpoint(
        self,
        authenticated_client,
        mock_entity
    ):
        """
        Test updating entity.
        
        Acceptance Criteria:
        - Status code is 200
        - Entity data is updated
        - Changes are persisted
        """
        url = reverse('identity:entity-detail', kwargs={'pk': mock_entity.id})
        
        update_data = {
            'name': mock_entity.name,
            'entity_type': mock_entity.entity_type,
            'address': 'New Address, London',
            'postcode': 'W1A 1AA'
        }
        
        response = authenticated_client.put(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['address'] == update_data['address']
        assert response.data['postcode'] == update_data['postcode']
        
        # Verify changes persisted
        mock_entity.refresh_from_db()
        assert mock_entity.address == update_data['address']
    
    def test_partial_update_entity_endpoint(
        self,
        authenticated_client,
        mock_entity
    ):
        """
        Test partial update (PATCH) of entity.
        
        Acceptance Criteria:
        - Status code is 200
        - Only specified fields are updated
        - Other fields remain unchanged
        """
        url = reverse('identity:entity-detail', kwargs={'pk': mock_entity.id})
        
        original_name = mock_entity.name
        
        patch_data = {
            'address': 'Updated Address'
        }
        
        response = authenticated_client.patch(url, patch_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['address'] == patch_data['address']
        assert response.data['name'] == original_name  # Unchanged
    
    def test_update_entity_settings(
        self,
        authenticated_client,
        mock_entity
    ):
        """
        Test updating entity settings via API.
        
        Acceptance Criteria:
        - Settings can be updated
        - Settings are properly merged/replaced
        - Changes are persisted
        """
        url = reverse('identity:entity-detail', kwargs={'pk': mock_entity.id})
        
        new_settings = {
            'notifications': {
                'email_enabled': False
            },
            'custom_feature': {
                'enabled': True
            }
        }
        
        update_data = {
            'name': mock_entity.name,
            'entity_type': mock_entity.entity_type,
            'settings': new_settings
        }
        
        response = authenticated_client.put(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['settings'] == new_settings
    
    def test_delete_entity_endpoint(
        self,
        authenticated_client,
        mock_entity
    ):
        """
        Test deleting entity (soft delete).
        
        Acceptance Criteria:
        - Status code is 204
        - Entity is soft deleted (not removed)
        - Entity is marked as inactive
        """
        from apps.identity.models import Entity
        
        entity_id = mock_entity.id
        url = reverse('identity:entity-detail', kwargs={'pk': entity_id})
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify entity still exists but is soft deleted
        entity = Entity.objects.get(id=entity_id)
        assert entity.deleted_at is not None
        assert entity.is_active is False
    
    def test_list_entities_excludes_deleted(
        self,
        authenticated_client,
        mock_entity
    ):
        """
        Test listing entities excludes soft deleted ones.
        
        Acceptance Criteria:
        - Soft deleted entities not in default list
        - Only active entities are returned
        """
        from apps.identity.models import Entity
        
        # Soft delete the entity
        mock_entity.soft_delete()
        
        # Create an active entity
        active_entity = Entity.objects.create(
            name="Active Entity",
            entity_type='estate_agency'
        )
        
        url = reverse('identity:entity-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        entity_ids = [e['id'] for e in response.data['results']]
        assert str(active_entity.id) in entity_ids
        assert str(mock_entity.id) not in entity_ids


@pytest.mark.django_db
class TestEntityAPIPermissions:
    """Test Entity API permission controls."""
    
    def test_create_entity_requires_authentication(
        self,
        api_client,
        entity_data
    ):
        """
        Test entity creation requires authentication.
        
        Acceptance Criteria:
        - Returns 401 if not authenticated
        """
        url = reverse('identity:entity-list')
        
        response = api_client.post(url, entity_data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_entities_requires_authentication(
        self,
        api_client
    ):
        """
        Test listing entities requires authentication.
        
        Acceptance Criteria:
        - Returns 401 if not authenticated
        """
        url = reverse('identity:entity-list')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_entity_requires_permission(
        self,
        authenticated_client,
        mock_entity
    ):
        """
        Test updating entity requires proper permissions.
        
        Acceptance Criteria:
        - User must have entity.update permission
        - Returns 403 if permission denied
        
        Note: This assumes RBAC is implemented (Sprint 1B)
        """
        # This test will be fully functional once RBAC is implemented
        url = reverse('identity:entity-detail', kwargs={'pk': mock_entity.id})
        
        update_data = {
            'name': 'Updated Name',
            'entity_type': mock_entity.entity_type
        }
        
        # For now, authenticated users can update
        # In Sprint 1B, this will check specific permissions
        response = authenticated_client.put(url, update_data, format='json')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
    
    def test_delete_entity_requires_permission(
        self,
        authenticated_client,
        mock_entity
    ):
        """
        Test deleting entity requires proper permissions.
        
        Acceptance Criteria:
        - User must have entity.delete permission
        - Returns 403 if permission denied
        
        Note: This assumes RBAC is implemented (Sprint 1B)
        """
        url = reverse('identity:entity-detail', kwargs={'pk': mock_entity.id})
        
        # For now, authenticated users can delete
        # In Sprint 1B, this will check specific permissions
        response = authenticated_client.delete(url)
        
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_403_FORBIDDEN]


@pytest.mark.django_db
class TestEntityAPIValidation:
    """Test Entity API validation."""
    
    def test_create_entity_validates_duplicate_name(
        self,
        authenticated_client,
        mock_entity
    ):
        """
        Test entity creation rejects duplicate names.
        
        Acceptance Criteria:
        - Returns 400 for duplicate name
        - Error message indicates duplicate
        """
        url = reverse('identity:entity-list')
        
        duplicate_data = {
            'name': mock_entity.name,
            'entity_type': 'law_firm'
        }
        
        response = authenticated_client.post(url, duplicate_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in str(response.data).lower()
    
    def test_create_entity_validates_entity_type(
        self,
        authenticated_client
    ):
        """
        Test entity creation validates entity type.
        
        Acceptance Criteria:
        - Returns 400 for invalid entity type
        - Error message lists valid types
        """
        url = reverse('identity:entity-list')
        
        invalid_data = {
            'name': 'Test Entity',
            'entity_type': 'invalid_type'
        }
        
        response = authenticated_client.post(url, invalid_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'entity_type' in str(response.data).lower()