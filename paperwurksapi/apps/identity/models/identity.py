# paperwurksapi/apps/identity/models/identity.py
"""
Identity Model - The Driver's License
Represents a person who can authenticate
"""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from .profile import Profile
import uuid
import secrets

class IdentityManager(BaseUserManager):

    async def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        extra_fields.pop('password', None)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        await user.afull_clean()
        await user.asave(using=self._db)
        return user

    async def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return await self.create_user(email, password, **extra_fields)


class Identity(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    entity = models.ForeignKey(
        'Entity',
        on_delete=models.PROTECT,
        related_name='identities'
    )
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, null=True, blank=True)
    verification_token_expires = models.DateTimeField(null=True, blank=True)
    password_reset_token = models.CharField(max_length=64, null=True, blank=True)
    password_reset_token_expires = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'identities'
        verbose_name = 'Identity'
        verbose_name_plural = 'Identities'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['entity', 'is_active']),
            models.Index(fields=['verification_token']),
            models.Index(fields=['password_reset_token']),
        ]
    
    def __str__(self):
        return f"{self.display_name}"

 
    async def generate_verification_token(self):
        """Generate token for email verification"""
        self.verification_token = secrets.token_urlsafe(32)
        self.verification_token_expires = timezone.now() + timezone.timedelta(days=1)
        await self.asave()
        return self.verification_token
    
    async def verify_email(self, token):
        """Verify email with token"""
        if not self.verification_token or self.verification_token != token:
            return False
        if timezone.now() > self.verification_token_expires:
            return False
        self.is_verified = True
        self.is_active = True
        self.verification_token = None
        self.verification_token_expires = None
        await self.asave()
        return True
    
    async def generate_password_reset_token(self):
        """Generate token for password reset"""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_token_expires = timezone.now() + timezone.timedelta(hours=1)
        await self.asave()
        return self.password_reset_token
    
    async def reset_password(self, token, new_password):
        """Reset password with token"""
        if not self.password_reset_token or self.password_reset_token != token:
            return False
        if timezone.now() > self.password_reset_token_expires:
            return False
        self.set_password(new_password)
        self.password_reset_token = None
        self.password_reset_token_expires = None
        await self.asave()
        return True
    
    @property
    def display_name(self):
        """
        Get display name for this identity
        - For humans: Returns their full name from Profile
        - For service accounts: Returns email prefix
        """
        try:
            return self.profile.get_full_name()
        except Profile.DoesNotExist:
            return self.email.split('@')[0]

    @property
    def is_service_account(self):
        """Is this a service account (no profile)?"""
        return not hasattr(self, 'profile')
    
    
    async def update_last_login(self):
        self.last_login = timezone.now()
        await self.asave(update_fields=['last_login'])
    
    @property
    def is_professional(self):
        return self.entity.is_organization
    
    @property
    def is_consumer(self):
        return self.entity.is_personal