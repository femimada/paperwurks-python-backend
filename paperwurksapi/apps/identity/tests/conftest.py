"""
Shared pytest fixtures for Identity app tests.

These fixtures provide reusable test data and objects following DRY principles.
Supports both sync and async testing for Django Ninja.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from uuid import uuid4
import bcrypt
import json
from asgiref.sync import sync_to_async
from httpx import AsyncClient, ASGITransport
from django.test import Client



@pytest.fixture
def valid_email():
    """Generate a unique valid email address for testing."""
    return f"test.user.{uuid4().hex[:8]}@example.com"


@pytest.fixture
def valid_password():
    """Provide a valid password that meets all requirements."""
    return "SecureP@ss123"


@pytest.fixture
def weak_password():
    """Provide a weak password for testing validation."""
    return "weak"


@pytest.fixture
def hashed_password(valid_password):
    """Provide a bcrypt hashed password."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(valid_password.encode('utf-8'), salt).decode('utf-8')


@pytest.fixture
def identity_data(valid_email, valid_password):
    """Provide valid identity creation data."""
    return {
        'email': valid_email,
        'password': valid_password,
        'first_name': 'John',
        'last_name': 'Doe',
    }


@pytest.fixture
def entity_data():
    """Provide valid entity creation data."""
    return {
        'name': f'Test Agency {uuid4().hex[:8]}',
        'entity_type': 'estate_agency',
        'address': '123 Test Street, London',
        'postcode': 'SW1A 1AA',
        'settings': {
            'notifications': {
                'email_enabled': True,
                'push_enabled': True
            },
            'compliance': {
                'require_solicitor_signoff': True
            }
        }
    }


@pytest.fixture
def jwt_payload(identity_data):
    """Provide a valid JWT token payload structure."""
    return {
        'sub': str(uuid4()),
        'email': identity_data['email'],
        'entity_id': str(uuid4()),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=1),
        'token_type': 'access'
    }


@pytest.fixture
def mock_entity(db, entity_data):
    """Create and return a test Entity instance."""
    from apps.identity.models import Entity
    return Entity.objects.create(**entity_data)


@pytest.fixture
def mock_identity(db, identity_data, mock_entity):
    """Create and return a test Identity instance."""
    from apps.identity.models import Identity
    return Identity.objects.create(
        entity=mock_entity,
        **identity_data
    )


@pytest.fixture
def mock_verified_identity(db, mock_identity):
    """Create and return a verified Identity instance."""
    mock_identity.is_verified = True
    mock_identity.is_active = True
    mock_identity.save()
    return mock_identity


@pytest.fixture
def mock_unverified_identity(db, mock_identity):
    """Create and return an unverified Identity instance."""
    mock_identity.is_verified = False
    mock_identity.is_active = False
    mock_identity.save()
    return mock_identity


@pytest.fixture
def mock_inactive_identity(db, mock_identity):
    """Create and return an inactive Identity instance."""
    mock_identity.is_active = False
    mock_identity.save()
    return mock_identity


@pytest.fixture
def multiple_entities(db):
    """Create multiple entities for multi-tenancy testing."""
    from apps.identity.models import Entity
    
    entity1 = Entity.objects.create(
        name=f"Agency One {uuid4().hex[:8]}",
        entity_type='estate_agency'
    )
    entity2 = Entity.objects.create(
        name=f"Law Firm One {uuid4().hex[:8]}",
        entity_type='law_firm'
    )
    
    return {'entity1': entity1, 'entity2': entity2}


@pytest.fixture
def sample_identities(db, mock_entity, identity_data):
    """Create multiple sample identities for bulk testing."""
    from apps.identity.models import Identity
    
    identities = []
    for i in range(3):
        data = identity_data.copy()
        data['email'] = f"user{i}@example.com"
        identity = Identity.objects.create(
            entity=mock_entity,
            **data
        )
        identities.append(identity)
    
    return identities


@pytest.fixture
def mock_audit_service(mocker):
    """Mock the AuditService for testing audit log creation."""
    return mocker.patch('apps.identity.services.auth_service.AuditService')


@pytest.fixture
def mock_email_service(mocker):
    """Mock the email service for testing email sending."""
    return mocker.patch('apps.identity.services.auth_service.send_email')


@pytest.fixture
def mock_redis(mocker):
    """Mock Redis for testing token blacklist functionality."""
    return mocker.patch('apps.identity.utils.jwt_utils.redis_client')


@pytest.fixture
def api_client():
    """
    Provide Django test client for API tests.
    
    This is Django's built-in test client that works with Django Ninja.
    """
    return Client()


@pytest.fixture
def authenticated_client(api_client, mock_verified_identity, valid_password):
    """
    Provide authenticated Django test client with valid JWT token.
    
    Performs login and sets Authorization header with JWT token.
    """
    # Login to get token
    login_response = api_client.post(
        '/api/identity/login',
        data=json.dumps({
            'email': mock_verified_identity.email,
            'password': valid_password
        }),
        content_type='application/json'
    )
    
    if login_response.status_code == 200:
        response_data = json.loads(login_response.content)
        access_token = response_data['access_token']
        api_client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
    
    return api_client


@pytest_asyncio.fixture
async def async_client():
    """
    Async HTTP client for testing Django Ninja endpoints.
    
    Uses httpx.AsyncClient with ASGI transport.
    """
    from apps.config.asgi import application
    
    transport = ASGITransport(app=application)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def async_authenticated_client(async_client, mock_verified_identity, valid_password):
    """
    Authenticated async client with valid JWT token.
    
    Performs async login and sets Authorization header.
    """
    # Login to get token
    login_response = await async_client.post(
        '/api/identity/login',
        json={
            'email': mock_verified_identity.email,
            'password': valid_password
        }
    )
    
    if login_response.status_code == 200:
        response_data = login_response.json()
        access_token = response_data['access_token']
        
        # Set authorization header
        async_client.headers['Authorization'] = f'Bearer {access_token}'
    
    return async_client


@pytest_asyncio.fixture
async def async_mock_entity(entity_data):
    """Async fixture to create Entity."""
    from apps.identity.models import Entity
    
    create_entity = sync_to_async(Entity.objects.create)
    entity = await create_entity(**entity_data)
    return entity


@pytest_asyncio.fixture
async def async_mock_identity(identity_data, async_mock_entity):
    """Async fixture to create Identity."""
    from apps.identity.models import Identity
    
    create_identity = sync_to_async(Identity.objects.create)
    identity = await create_identity(
        entity=async_mock_entity,
        **identity_data
    )
    return identity


@pytest_asyncio.fixture
async def async_mock_verified_identity(async_mock_identity):
    """Async fixture for verified Identity."""
    async_mock_identity.is_verified = True
    async_mock_identity.is_active = True
    
    save_identity = sync_to_async(async_mock_identity.save)
    await save_identity()
    
    return async_mock_identity



@pytest.fixture
def password_reset_token(mock_verified_identity):
    """
    Generate a valid password reset token for testing.
    
    Requests password reset and returns the generated token.
    """
    from apps.identity.services import AuthService
    
    auth_service = AuthService()
    auth_service.request_password_reset(
        email=mock_verified_identity.email
    )
    
    mock_verified_identity.refresh_from_db()
    return mock_verified_identity.password_reset_token


@pytest.fixture
def json_response_data():
    """
    Helper to parse JSON response from Django test client.
    
    Usage:
        response = api_client.post(url, data)
        data = json_response_data(response)
    """
    def parse(response):
        return json.loads(response.content)
    return parse


@pytest.fixture(autouse=True)
def reset_mocks(mocker):
    """Automatically reset all mocks after each test."""
    yield
    mocker.resetall()