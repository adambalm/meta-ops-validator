"""
Publisher repository for managing publisher entities and operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..models.publisher import Publisher
from ..models.book import Book
from ..models.contract import Contract


class PublisherRepository(BaseRepository[Publisher]):
    """Repository for Publisher operations with business logic"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Publisher)
    
    async def get_all_publishers(self) -> List[Publisher]:
        """Get all publishers"""
        query = select(Publisher).order_by(Publisher.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create_publisher(
        self,
        name: str,
        imprint: Optional[str] = None,
        territory_codes: Optional[List[str]] = None,
        validation_profile: Optional[Dict[str, Any]] = None
    ) -> Publisher:
        """Create a new publisher with proper field handling"""
        publisher = Publisher(
            name=name,
            imprint=imprint
        )
        
        # Set JSON fields using properties
        if territory_codes:
            publisher.territory_codes = territory_codes
        if validation_profile:
            publisher.validation_profile = validation_profile
        
        self.session.add(publisher)
        await self.session.flush()
        await self.session.refresh(publisher)
        return publisher
    
    async def get_publisher_with_stats(self, publisher_id: str) -> Optional[Dict[str, Any]]:
        """Get publisher with aggregated statistics for dashboard"""
        publisher = await self.get_by_id(publisher_id)
        if not publisher:
            return None
        
        # Get book count
        book_count_result = await self.session.execute(
            select(func.count(Book.id)).where(Book.publisher_id == publisher_id)
        )
        book_count = book_count_result.scalar() or 0
        
        # Get contract count
        contract_count_result = await self.session.execute(
            select(func.count(Contract.id)).where(Contract.publisher_id == publisher_id)
        )
        contract_count = contract_count_result.scalar() or 0
        
        # Get books with validation status counts
        validation_stats = await self.session.execute(
            select(Book.validation_status, func.count(Book.id))
            .where(Book.publisher_id == publisher_id)
            .group_by(Book.validation_status)
        )
        validation_counts = dict(validation_stats.fetchall())
        
        return {
            'publisher': publisher,
            'book_count': book_count,
            'contract_count': contract_count,
            'validation_stats': validation_counts,
            'compliance_rate': self._calculate_compliance_rate(validation_counts)
        }
    
    async def get_publisher_books(
        self,
        publisher_id: str,
        limit: Optional[int] = None,
        validation_status: Optional[str] = None
    ) -> List[Book]:
        """Get books for a publisher with optional filtering"""
        query = (
            select(Book)
            .where(Book.publisher_id == publisher_id)
            .options(selectinload(Book.book_authors))
        )
        
        if validation_status:
            query = query.where(Book.validation_status == validation_status)
        
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_publisher_contracts(self, publisher_id: str) -> List[Contract]:
        """Get all contracts for a publisher"""
        result = await self.session.execute(
            select(Contract).where(Contract.publisher_id == publisher_id)
        )
        return list(result.scalars().all())
    
    async def search_publishers(self, search_term: str, limit: int = 10) -> List[Publisher]:
        """Search publishers by name"""
        result = await self.session.execute(
            select(Publisher)
            .where(Publisher.name.ilike(f'%{search_term}%'))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    def _calculate_compliance_rate(self, validation_counts: Dict[str, int]) -> float:
        """Calculate compliance rate from validation status counts"""
        total = sum(validation_counts.values())
        if total == 0:
            return 0.0
        
        compliant = validation_counts.get('validated', 0)
        return round((compliant / total) * 100, 1)