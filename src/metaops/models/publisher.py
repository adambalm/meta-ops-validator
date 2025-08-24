"""
Publisher model for multi-tenant isolation and validation profiles
"""
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, Dict, Any
import json

from .base import BaseModel

if False:  # TYPE_CHECKING
    from .book import Book
    from .contract import Contract


class Publisher(BaseModel):
    __tablename__ = "publishers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    imprint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # JSON field for territory codes: ["US", "CA", "GB"]
    _territory_codes: Mapped[Optional[str]] = mapped_column("territory_codes", Text, nullable=True)
    
    # JSON field for publisher-specific validation rules
    _validation_profile: Mapped[Optional[str]] = mapped_column("validation_profile", Text, nullable=True)

    # Relationships
    books: Mapped[List["Book"]] = relationship("Book", back_populates="publisher")
    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="publisher")

    @property
    def territory_codes(self) -> List[str]:
        """Get territory codes as Python list"""
        if self._territory_codes:
            return json.loads(self._territory_codes)
        return []

    @territory_codes.setter
    def territory_codes(self, value: List[str]) -> None:
        """Set territory codes from Python list"""
        if value:
            self._territory_codes = json.dumps(value)
        else:
            self._territory_codes = None

    @property
    def validation_profile(self) -> Dict[str, Any]:
        """Get validation profile as Python dict"""
        if self._validation_profile:
            return json.loads(self._validation_profile)
        return {}

    @validation_profile.setter
    def validation_profile(self, value: Dict[str, Any]) -> None:
        """Set validation profile from Python dict"""
        if value:
            self._validation_profile = json.dumps(value)
        else:
            self._validation_profile = None

    def __repr__(self) -> str:
        return f"<Publisher(id={self.id}, name='{self.name}')>"