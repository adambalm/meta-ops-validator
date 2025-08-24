"""
Contract repository for managing contract entities and compliance operations
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..models.contract import Contract
from ..models.book import Book
from ..models.validation import ContractCompliance


class ContractRepository(BaseRepository[Contract]):
    """Repository for Contract operations with compliance checking"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Contract)
    
    async def get_all_contracts(self) -> List[Contract]:
        """Get all contracts"""
        query = select(Contract).order_by(Contract.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create_contract(
        self,
        publisher_id: str,
        contract_name: str,
        contract_type: str,
        retailer: str,
        effective_date: Optional[date] = None,
        expiration_date: Optional[date] = None,
        territory_restrictions: Optional[List[str]] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        document_path: Optional[str] = None,
        status: str = "active"
    ) -> Contract:
        """Create a new contract with proper field handling"""
        
        contract = Contract(
            publisher_id=publisher_id,
            contract_name=contract_name,
            contract_type=contract_type,
            retailer=retailer,
            effective_date=effective_date,
            expiration_date=expiration_date,
            document_path=document_path,
            status=status
        )
        
        # Set JSON fields using properties
        if territory_restrictions:
            contract.territory_restrictions = territory_restrictions
        if validation_rules:
            contract.validation_rules = validation_rules
        
        self.session.add(contract)
        await self.session.flush()
        await self.session.refresh(contract)
        return contract
    
    async def get_active_contracts(self, publisher_id: str) -> List[Contract]:
        """Get all active contracts for a publisher"""
        today = date.today()
        
        result = await self.session.execute(
            select(Contract)
            .where(
                and_(
                    Contract.publisher_id == publisher_id,
                    Contract.status == "active",
                    or_(
                        Contract.effective_date.is_(None),
                        Contract.effective_date <= today
                    ),
                    or_(
                        Contract.expiration_date.is_(None),
                        Contract.expiration_date > today
                    )
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_contracts_by_retailer(self, publisher_id: str, retailer: str) -> List[Contract]:
        """Get contracts for a specific retailer"""
        result = await self.session.execute(
            select(Contract)
            .where(
                and_(
                    Contract.publisher_id == publisher_id,
                    Contract.retailer == retailer,
                    Contract.status == "active"
                )
            )
        )
        return list(result.scalars().all())
    
    async def check_book_compliance(self, book_id: str, contract_id: str) -> Dict[str, Any]:
        """Check if a book complies with a specific contract"""
        
        # Get book and contract
        book_result = await self.session.execute(
            select(Book).where(Book.id == book_id)
        )
        book = book_result.scalar_one_or_none()
        
        contract_result = await self.session.execute(
            select(Contract).where(Contract.id == contract_id)
        )
        contract = contract_result.scalar_one_or_none()
        
        if not book or not contract:
            return {
                'compliant': False,
                'violations': ['Book or contract not found'],
                'status': 'error'
            }
        
        violations = []
        warnings = []
        
        # Check territory restrictions
        territory_compliant = True
        if contract.territory_restrictions:
            # For demo purposes, assume we can extract territory info from ONIX
            # In real implementation, would parse ONIX file for territory data
            territory_compliant = True  # Simplified for MVP
        
        # Check validation rules
        rules_compliant = True
        if contract.validation_rules:
            rules = contract.validation_rules
            
            # Check required fields (simplified)
            if 'required_fields' in rules:
                for field in rules['required_fields']:
                    # Simplified check - in real implementation would parse ONIX
                    if field == 'isbn' and not book.isbn:
                        violations.append(f"Missing required field: {field}")
                        rules_compliant = False
            
            # Check forbidden values
            if 'forbidden_values' in rules:
                # Simplified implementation
                pass
        
        # Determine overall compliance
        overall_compliant = territory_compliant and rules_compliant and len(violations) == 0
        
        # Determine status
        if overall_compliant:
            status = 'compliant'
        elif warnings and not violations:
            status = 'review_needed'
        else:
            status = 'non_compliant'
        
        return {
            'compliant': overall_compliant,
            'territory_check_passed': territory_compliant,
            'rules_check_passed': rules_compliant,
            'violations': violations,
            'warnings': warnings,
            'status': status
        }
    
    async def create_compliance_result(
        self,
        book_id: str,
        contract_id: str,
        compliance_status: str,
        territory_check_passed: Optional[bool] = None,
        retailer_requirements_met: Optional[bool] = None,
        violations: Optional[List[Dict[str, Any]]] = None,
        approval_status: str = "needs_review"
    ) -> ContractCompliance:
        """Create a compliance result record"""
        
        compliance = ContractCompliance(
            book_id=book_id,
            contract_id=contract_id,
            compliance_status=compliance_status,
            territory_check_passed=territory_check_passed,
            retailer_requirements_met=retailer_requirements_met,
            approval_status=approval_status
        )
        
        # Set violations using property
        if violations:
            compliance.violations = violations
        
        self.session.add(compliance)
        await self.session.flush()
        await self.session.refresh(compliance)
        return compliance
    
    async def get_compliance_results(self, book_id: str) -> List[Dict[str, Any]]:
        """Get all compliance results for a book"""
        
        result = await self.session.execute(
            select(ContractCompliance, Contract)
            .join(Contract, ContractCompliance.contract_id == Contract.id)
            .where(ContractCompliance.book_id == book_id)
            .options(selectinload(ContractCompliance.contract))
        )
        
        compliance_data = []
        for compliance, contract in result.all():
            compliance_data.append({
                'compliance': compliance,
                'contract': contract,
                'contract_name': contract.contract_name,
                'retailer': contract.retailer,
                'status': compliance.compliance_status,
                'violations': compliance.violations,
                'needs_review': compliance.approval_status == "needs_review"
            })
        
        return compliance_data
    
    async def get_publisher_compliance_summary(self, publisher_id: str) -> Dict[str, Any]:
        """Get compliance summary for all publisher books"""
        
        # Get all compliance results for publisher books
        result = await self.session.execute(
            select(ContractCompliance, Book, Contract)
            .join(Book, ContractCompliance.book_id == Book.id)
            .join(Contract, ContractCompliance.contract_id == Contract.id)
            .where(Book.publisher_id == publisher_id)
        )
        
        compliance_results = result.all()
        
        # Calculate statistics
        total_checks = len(compliance_results)
        compliant_count = sum(1 for compliance, _, _ in compliance_results 
                            if compliance.compliance_status == 'compliant')
        needs_review_count = sum(1 for compliance, _, _ in compliance_results 
                               if compliance.compliance_status == 'review_needed')
        non_compliant_count = sum(1 for compliance, _, _ in compliance_results 
                                if compliance.compliance_status == 'non_compliant')
        
        compliance_rate = (compliant_count / total_checks * 100) if total_checks > 0 else 0
        
        # Group by retailer
        retailer_stats = {}
        for compliance, book, contract in compliance_results:
            retailer = contract.retailer
            if retailer not in retailer_stats:
                retailer_stats[retailer] = {
                    'total': 0,
                    'compliant': 0,
                    'needs_review': 0,
                    'non_compliant': 0
                }
            
            retailer_stats[retailer]['total'] += 1
            retailer_stats[retailer][compliance.compliance_status] += 1
        
        return {
            'total_compliance_checks': total_checks,
            'compliant_count': compliant_count,
            'needs_review_count': needs_review_count,
            'non_compliant_count': non_compliant_count,
            'compliance_rate': round(compliance_rate, 1),
            'retailer_breakdown': retailer_stats
        }
    
    async def update_contract_rules(self, contract_id: str, validation_rules: Dict[str, Any]) -> Optional[Contract]:
        """Update validation rules for a contract"""
        contract = await self.get_by_id(contract_id)
        if contract:
            contract.validation_rules = validation_rules
            await self.session.flush()
            await self.session.refresh(contract)
        return contract