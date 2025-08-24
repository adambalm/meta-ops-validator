"""
Validation models for tracking validation sessions and results
"""
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from .base import BaseModel

if False:  # TYPE_CHECKING
    from .book import Book
    from .contract import Contract


class ValidationSession(BaseModel):
    """Tracks individual validation runs through the pipeline"""
    __tablename__ = "validation_sessions"

    book_id: Mapped[str] = mapped_column(String(36), ForeignKey("books.id"), nullable=False)
    session_type: Mapped[str] = mapped_column(String(20), default="individual", nullable=False)  # 'individual', 'batch', 'contract_check'
    status: Mapped[str] = mapped_column(String(20), default="queued", nullable=False)  # 'queued', 'processing', 'completed', 'failed'
    
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    book: Mapped["Book"] = relationship("Book", back_populates="validation_sessions")
    results: Mapped[List["ValidationResult"]] = relationship("ValidationResult", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ValidationSession(id={self.id}, book_id={self.book_id}, status='{self.status}')>"


class ValidationResult(BaseModel):
    """Individual validation findings from the pipeline stages"""
    __tablename__ = "validation_results"

    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("validation_sessions.id"), nullable=False)
    validation_stage: Mapped[str] = mapped_column(String(20), nullable=False)  # 'xsd', 'schematron', 'rules', 'nielsen'
    
    line_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_level: Mapped[str] = mapped_column(String(10), nullable=False)  # 'ERROR', 'WARNING', 'INFO'
    error_code: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    xpath_location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    element_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # XML snippet around error
    business_impact: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # 'high', 'medium', 'low'
    
    # JSON field for affected retailers: ["amazon", "ingram"]
    _retailer_impact: Mapped[Optional[str]] = mapped_column("retailer_impact", Text, nullable=True)
    
    suggested_fix: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    session: Mapped["ValidationSession"] = relationship("ValidationSession", back_populates="results")

    @property
    def retailer_impact(self) -> List[str]:
        """Get retailer impact as Python list"""
        if self._retailer_impact:
            return json.loads(self._retailer_impact)
        return []

    @retailer_impact.setter
    def retailer_impact(self, value: List[str]) -> None:
        """Set retailer impact from Python list"""
        if value:
            self._retailer_impact = json.dumps(value)
        else:
            self._retailer_impact = None

    def __repr__(self) -> str:
        return f"<ValidationResult(id={self.id}, stage='{self.validation_stage}', level='{self.error_level}')>"


class NielsenScore(BaseModel):
    """Nielsen completeness scoring results"""
    __tablename__ = "nielsen_scores"

    book_id: Mapped[str] = mapped_column(String(36), ForeignKey("books.id"), nullable=False)
    
    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    required_fields_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    optional_fields_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    recommended_fields_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    
    # JSON field for detailed field breakdown
    _field_breakdown: Mapped[Optional[str]] = mapped_column("field_breakdown", Text, nullable=True)
    
    # JSON field for missing critical fields
    _missing_high_impact: Mapped[Optional[str]] = mapped_column("missing_high_impact", Text, nullable=True)
    
    sales_impact_estimate: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)  # Estimated revenue impact
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now())

    # Relationships
    book: Mapped["Book"] = relationship("Book", back_populates="nielsen_scores")

    @property
    def field_breakdown(self) -> Dict[str, Any]:
        """Get field breakdown as Python dict"""
        if self._field_breakdown:
            return json.loads(self._field_breakdown)
        return {}

    @field_breakdown.setter
    def field_breakdown(self, value: Dict[str, Any]) -> None:
        """Set field breakdown from Python dict"""
        if value:
            self._field_breakdown = json.dumps(value)
        else:
            self._field_breakdown = None

    @property
    def missing_high_impact(self) -> List[str]:
        """Get missing high impact fields as Python list"""
        if self._missing_high_impact:
            return json.loads(self._missing_high_impact)
        return []

    @missing_high_impact.setter
    def missing_high_impact(self, value: List[str]) -> None:
        """Set missing high impact fields from Python list"""
        if value:
            self._missing_high_impact = json.dumps(value)
        else:
            self._missing_high_impact = None

    def __repr__(self) -> str:
        return f"<NielsenScore(id={self.id}, book_id={self.book_id}, score={self.overall_score})>"


class ContractCompliance(BaseModel):
    """Contract compliance checking results"""
    __tablename__ = "contract_compliance"

    book_id: Mapped[str] = mapped_column(String(36), ForeignKey("books.id"), nullable=False)
    contract_id: Mapped[str] = mapped_column(String(36), ForeignKey("contracts.id"), nullable=False)
    
    compliance_status: Mapped[str] = mapped_column(String(20), default="review_needed", nullable=False)  # 'compliant', 'non_compliant', 'review_needed'
    territory_check_passed: Mapped[Optional[bool]] = mapped_column(nullable=True)
    retailer_requirements_met: Mapped[Optional[bool]] = mapped_column(nullable=True)
    
    # JSON field for specific violations found
    _violations: Mapped[Optional[str]] = mapped_column("violations", Text, nullable=True)
    
    approval_status: Mapped[str] = mapped_column(String(20), default="needs_review", nullable=False)  # 'auto_approved', 'needs_review', 'rejected'
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    book: Mapped["Book"] = relationship("Book", back_populates="compliance_results")
    contract: Mapped["Contract"] = relationship("Contract", back_populates="compliance_results")

    @property
    def violations(self) -> List[Dict[str, Any]]:
        """Get violations as Python list of dicts"""
        if self._violations:
            return json.loads(self._violations)
        return []

    @violations.setter
    def violations(self, value: List[Dict[str, Any]]) -> None:
        """Set violations from Python list of dicts"""
        if value:
            self._violations = json.dumps(value)
        else:
            self._violations = None

    def __repr__(self) -> str:
        return f"<ContractCompliance(id={self.id}, book_id={self.book_id}, status='{self.compliance_status}')>"