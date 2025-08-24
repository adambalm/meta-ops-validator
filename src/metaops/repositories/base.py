"""
Base repository with common CRUD operations
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from ..models.base import BaseModel

T = TypeVar('T', bound=BaseModel)


class BaseRepository(ABC, Generic[T]):
    """Base repository with common async CRUD operations"""
    
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    async def create(self, **kwargs) -> T:
        """Create a new record"""
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: str) -> Optional[T]:
        """Get record by ID"""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """Get all records with optional pagination"""
        query = select(self.model_class).offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_filter(self, **filters) -> List[T]:
        """Get records by filters"""
        query = select(self.model_class)
        
        for attr, value in filters.items():
            if hasattr(self.model_class, attr):
                query = query.where(getattr(self.model_class, attr) == value)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_one_by_filter(self, **filters) -> Optional[T]:
        """Get single record by filters"""
        query = select(self.model_class)
        
        for attr, value in filters.items():
            if hasattr(self.model_class, attr):
                query = query.where(getattr(self.model_class, attr) == value)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, id: str, **kwargs) -> Optional[T]:
        """Update record by ID"""
        # Remove None values to avoid overwriting with null
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(id)
        
        await self.session.execute(
            update(self.model_class)
            .where(self.model_class.id == id)
            .values(**update_data)
        )
        
        return await self.get_by_id(id)

    async def delete(self, id: str) -> bool:
        """Delete record by ID"""
        result = await self.session.execute(
            delete(self.model_class).where(self.model_class.id == id)
        )
        return result.rowcount > 0

    async def count(self, **filters) -> int:
        """Count records with optional filters"""
        query = select(func.count(self.model_class.id))
        
        for attr, value in filters.items():
            if hasattr(self.model_class, attr):
                query = query.where(getattr(self.model_class, attr) == value)
        
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def exists(self, id: str) -> bool:
        """Check if record exists by ID"""
        result = await self.session.execute(
            select(func.count(self.model_class.id)).where(self.model_class.id == id)
        )
        count = result.scalar() or 0
        return count > 0