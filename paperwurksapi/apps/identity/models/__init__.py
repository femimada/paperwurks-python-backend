

from .entity import Entity
from .identity import Identity, Profile

__all__ = ['Entity', 'Identity', 'Profile']

# ============================================
# DATA SEPARATION GUIDE
# ============================================
"""
AUTHENTICATION DATA → Identity
- email (login credential)
- password_hash
- entity
- verification/reset tokens
- NO name (name is personal data)

Example:
    identity = Identity(email="john@example.com", entity=abc_entity)
    identity.display_name  # "John Smith" (from profile) or "john" (service account)

PERSONAL DATA → Profile (linked to Identity)
- first_name, last_name
- phone
- avatar_url
- bio
- metadata (personal info, NOT organization)
- preferences (UI settings)

Example:
    john.profile.first_name = "John"
    john.profile.last_name = "Smith"
    john.profile.phone = "+44 7700 123456"  # John's personal phone
    john.profile.bio = "10 years experience in property"
    john.profile.preferences = {"theme": "dark"}

ORGANIZATION DATA → Entity.metadata
- address (company office)
- phone (company main line)
- email (company contact)
- website
- description
- etc.

Example:
    abc_entity.metadata = {
        "organization": {
            "address": "123 High Street, London SW1A 1AA",
            "phone": "+44 20 1234 5678",
            "email": "info@abcestates.com"
        }
    }
    
    # All employees access same organization data
    john.entity.metadata['organization']['address']
    agent.entity.metadata['organization']['phone']

WHY NAME IS IN PROFILE (NOT IDENTITY)?
1. Identity = Authentication (can you log in?)
2. Profile = Personal Information (who are you?)
3. Name is personal information, not authentication
4. Enables service accounts without names:
   
   # Human user
   jane = Identity(email="jane@gmail.com")
   jane.profile.first_name = "Jane"
   jane.profile.last_name = "Doe"
   jane.display_name  # "Jane Doe"
   
   # Service account (no profile, no name)
   api = Identity(email="ai-analysis@system.paperwurks.com")
   # No profile needed - it's not a person!
   api.is_service_account  # True
   api.display_name  # "ai-analysis" (from email prefix)

WHY THIS SEPARATION?
1. Personal data belongs to the person (survives if they leave company)
2. Organization data belongs to the company (survives when employees leave)
3. No duplication - one source of truth for organization info
4. All employees see same organization data
5. Service accounts can exist without personal profiles
6. Future-proof for bots, APIs, system accounts
"""