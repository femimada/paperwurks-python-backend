
from django.db import models
import uuid


class Profile(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identity = models.OneToOneField(
        'Identity',
        on_delete=models.CASCADE,
        related_name='profile'
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    
    # Personal metadata (NOT for organization info)
    # Examples:
    # - Buyer preferences: {"budget_max": 500000, "areas": ["Kensington"]}
    # - Agent certifications: {"naea_member": true, "member_number": "12345"}
    metadata = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User interface preferences (theme, language, notifications)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def __str__(self):
        return f"Profile for {self.identity.email}"
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def default_preferences(self):
        """Default UI preferences"""
        return {
            "theme": "light",
            "language": "en-GB",
            "notifications": {
                "email": True,
                "push": True,
                "sms": False
            }
        }
    
    def get_preference(self, key, default=None):
        """Get a specific preference value"""
        return self.preferences.get(key, self.default_preferences.get(key, default))

