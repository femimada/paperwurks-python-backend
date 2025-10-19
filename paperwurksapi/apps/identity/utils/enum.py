
from enum import StrEnum, auto

class EntityType(StrEnum):
    EstateAgent = auto()
    LawFirm = auto()
    Individual = auto()

    @classmethod
    def choices(cls):
        """Convert to Django choices format"""
        return [(member.value, member.name.replace('_', ' ').title()) for member in cls]
