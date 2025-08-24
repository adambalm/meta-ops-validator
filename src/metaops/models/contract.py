"""
Contract model with validation rules and compliance tracking
"""
from sqlalchemy import String, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, Dict, Any
from datetime import date
import json

from .base import BaseModel

if False:  # TYPE_CHECKING
    from .publisher import Publisher
    from .validation import ContractCompliance


class Contract(BaseModel):
    __tablename__ = "contracts"

    publisher_id: Mapped[str] = mapped_column(String(36), ForeignKey("publishers.id"), nullable=False)
    contract_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'distribution_agreement', 'retailer_terms'
    retailer: Mapped[str] = mapped_column(String(100), nullable=False)  # 'amazon_kdp', 'ingram_spark', 'generic'
    
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # JSON field for territory restrictions: ["US", "CA"]
    _territory_restrictions: Mapped[Optional[str]] = mapped_column("territory_restrictions", Text, nullable=True)
    
    # JSON field for validation rules: {"required_fields": [...], "forbidden_values": {...}}
    _validation_rules: Mapped[Optional[str]] = mapped_column("validation_rules", Text, nullable=True)
    
    document_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Path to contract PDF/DOC
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # 'active', 'expired', 'suspended'

    # Relationships
    publisher: Mapped["Publisher"] = relationship("Publisher", back_populates="contracts")
    compliance_results: Mapped[List["ContractCompliance"]] = relationship("ContractCompliance", back_populates="contract")

    @property
    def territory_restrictions(self) -> List[str]:
        """Get territory restrictions as Python list"""
        if self._territory_restrictions:
            return json.loads(self._territory_restrictions)
        return []

    @territory_restrictions.setter
    def territory_restrictions(self, value: List[str]) -> None:
        """Set territory restrictions from Python list"""
        if value:
            self._territory_restrictions = json.dumps(value)
        else:
            self._territory_restrictions = None

    @property
    def validation_rules(self) -> Dict[str, Any]:
        """Get validation rules as Python dict"""
        if self._validation_rules:
            return json.loads(self._validation_rules)
        return {}

    @validation_rules.setter
    def validation_rules(self, value: Dict[str, Any]) -> None:
        """Set validation rules from Python dict"""
        if value:
            self._validation_rules = json.dumps(value)
        else:
            self._validation_rules = None

    def is_active(self) -> bool:
        """Check if contract is currently active"""
        if self.status != "active":
            return False
        
        today = date.today()
        
        if self.effective_date and today < self.effective_date:
            return False
            
        if self.expiration_date and today > self.expiration_date:
            return False
            
        return True

    def __repr__(self) -> str:
        return f"<Contract(id={self.id}, name='{self.contract_name}', retailer='{self.retailer}')>"