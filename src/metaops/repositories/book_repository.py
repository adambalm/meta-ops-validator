"""
Book repository for managing book entities and ONIX integration
"""
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..models.book import Book, BookAuthor
from ..models.author import Author
from ..models.publisher import Publisher
from ..models.validation import ValidationSession, NielsenScore


class BookRepository(BaseRepository[Book]):
    """Repository for Book operations with ONIX and validation integration"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Book)
    
    async def create_book_with_validation(
        self,
        title: str,
        isbn: str,
        publisher_id: str,
        subtitle: Optional[str] = None,
        publication_date: Optional[date] = None,
        product_form: str = "BA",
        onix_file_path: Optional[str] = None,
        trigger_validation: bool = True
    ) -> Book:
        """Create book and optionally trigger validation pipeline"""
        
        # Create book record
        book = Book(
            title=title,
            isbn=isbn,
            subtitle=subtitle,
            publisher_id=publisher_id,
            publication_date=publication_date,
            product_form=product_form,
            onix_file_path=onix_file_path,
            validation_status="pending"
        )
        
        self.session.add(book)
        await self.session.flush()
        
        # Create validation session if requested
        if trigger_validation and onix_file_path:
            validation_session = ValidationSession(
                book_id=book.id,
                session_type='individual',
                status='queued'
            )
            self.session.add(validation_session)
            await self.session.flush()
        
        await self.session.refresh(book)
        return book
    
    async def get_book_with_details(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Get book with full details including authors, publisher, validation results"""
        
        # Get book with relationships
        result = await self.session.execute(
            select(Book)
            .options(
                selectinload(Book.publisher),
                selectinload(Book.book_authors).selectinload(BookAuthor.author),
                selectinload(Book.validation_sessions),
                selectinload(Book.nielsen_scores),
                selectinload(Book.compliance_results)
            )
            .where(Book.id == book_id)
        )
        
        book = result.scalar_one_or_none()
        if not book:
            return None
        
        # Get latest Nielsen score
        latest_score = None
        if book.nielsen_scores:
            latest_score = max(book.nielsen_scores, key=lambda x: x.calculated_at)
        
        # Get latest validation session
        latest_validation = None
        if book.validation_sessions:
            latest_validation = max(book.validation_sessions, key=lambda x: x.created_at)
        
        return {
            'book': book,
            'authors': book.authors,
            'publisher': book.publisher,
            'latest_nielsen_score': latest_score,
            'latest_validation_session': latest_validation,
            'validation_sessions': book.validation_sessions,
            'compliance_results': book.compliance_results
        }
    
    async def link_author_to_book(
        self,
        book_id: str,
        author_id: str,
        sequence_number: int = 1,
        contributor_role: str = "A01"
    ) -> BookAuthor:
        """Link an author to a book with contributor role"""
        
        # Check if link already exists
        existing = await self.session.execute(
            select(BookAuthor).where(
                and_(BookAuthor.book_id == book_id, BookAuthor.author_id == author_id)
            )
        )
        existing_link = existing.scalar_one_or_none()
        
        if existing_link:
            # Update existing link
            existing_link.sequence_number = sequence_number
            existing_link.contributor_role = contributor_role
            await self.session.flush()
            return existing_link
        
        # Create new link
        book_author = BookAuthor(
            book_id=book_id,
            author_id=author_id,
            sequence_number=sequence_number,
            contributor_role=contributor_role
        )
        
        self.session.add(book_author)
        await self.session.flush()
        await self.session.refresh(book_author)
        return book_author
    
    async def unlink_author_from_book(self, book_id: str, author_id: str) -> bool:
        """Remove author link from book"""
        result = await self.session.execute(
            select(BookAuthor).where(
                and_(BookAuthor.book_id == book_id, BookAuthor.author_id == author_id)
            )
        )
        book_author = result.scalar_one_or_none()
        
        if book_author:
            await self.session.delete(book_author)
            await self.session.flush()
            return True
        return False
    
    async def search_books(
        self,
        search_term: Optional[str] = None,
        publisher_id: Optional[str] = None,
        validation_status: Optional[str] = None,
        limit: int = 50
    ) -> List[Book]:
        """Search books with multiple criteria"""
        
        query = select(Book).options(
            selectinload(Book.publisher),
            selectinload(Book.book_authors).selectinload(BookAuthor.author)
        )
        
        if search_term:
            search_pattern = f'%{search_term}%'
            query = query.where(
                Book.title.ilike(search_pattern) | Book.isbn.ilike(search_pattern)
            )
        
        if publisher_id:
            query = query.where(Book.publisher_id == publisher_id)
        
        if validation_status:
            query = query.where(Book.validation_status == validation_status)
        
        query = query.order_by(desc(Book.created_at)).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_books_needing_validation(self, publisher_id: Optional[str] = None) -> List[Book]:
        """Get books that need validation or re-validation"""
        query = select(Book).where(Book.validation_status.in_(['pending', 'failed']))
        
        if publisher_id:
            query = query.where(Book.publisher_id == publisher_id)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_onix_file_path(self, book_id: str, file_path: str, namespace_uri: Optional[str] = None, version: Optional[str] = None) -> Optional[Book]:
        """Update ONIX file path and metadata for a book"""
        book = await self.get_by_id(book_id)
        if book:
            book.onix_file_path = file_path
            book.onix_namespace_uri = namespace_uri
            book.onix_version = version
            book.validation_status = "pending"  # Reset validation status
            await self.session.flush()
            await self.session.refresh(book)
        return book
    
    async def update_validation_status(self, book_id: str, status: str, validated_at: Optional[datetime] = None) -> Optional[Book]:
        """Update book validation status"""
        book = await self.get_by_id(book_id)
        if book:
            book.validation_status = status
            if validated_at:
                book.last_validated_at = validated_at
            elif status == "validated":
                book.last_validated_at = datetime.utcnow()
            await self.session.flush()
            await self.session.refresh(book)
        return book