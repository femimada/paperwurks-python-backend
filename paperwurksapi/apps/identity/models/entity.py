"""
Represents a data boundary (organization or individual)
"""
from django.db import models
from ..utils import EntityType
import uuid


class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    entity_type = models.CharField(max_length=50, choices=EntityType.choices())
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    settings = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict, blank=True)
    class Meta:
        app_label = 'identity'
        db_table = 'entities'
        verbose_name = 'Entity'
        verbose_name_plural = 'Entities'
        indexes = [
            models.Index(fields=['entity_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"
    
    @property
    def is_organization(self):
        return self.entity_type != EntityType.Individual
    
    @property
    def is_personal(self):
        return not self.is_organization
    
    async def deactivate(self):
        self.is_active = False
        await self.asave()

    @property
    def organization_info(self):
        """
        Get organization information
        Returns empty dict for individuals
        
        Example structure for organizations:
        {
            "address": "123 High Street, London SW1A 1AA",
            "phone": "+44 20 1234 5678",
            "email": "info@abcestates.com",
            "website": "https://abcestates.com",
            "description": "Leading estate agency in London",
            "established": 2005,
            "registration_number": "12345678"
        }
        """
        return self.metadata.get('organization', {})
    
    async def set_organization_info(self, **kwargs):
        """
        Set organization information
        
        Usage:
            entity.set_organization_info(
                address="123 High Street, London SW1A 1AA",
                phone="+44 20 1234 5678",
                email="info@abcestates.com"
            )
        """
        if self.is_personal:
            raise ValueError("Cannot set organization info for individual entities")
        if 'organization' not in self.metadata:
            self.metadata['organization'] = {}
        self.metadata['organization'].update(kwargs)
        await self.asave()
