"""
Author repository for managing author entities and book relationships
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..models.author import Author
from ..models.book import Book, BookAuthor


class AuthorRepository(BaseRepository[Author]):
    """Repository for Author operations with intelligent search and suggestions"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Author)
    
    async def create_author(
        self,
        name: str,
        contributor_type: str = "A01",
        sort_name: Optional[str] = None,
        biography: Optional[str] = None,
        website_url: Optional[str] = None
    ) -> Author:
        """Create a new author with proper field handling"""
        
        # Auto-generate sort_name if not provided
        if not sort_name:
            sort_name = self._generate_sort_name(name)
        
        author = Author(
            name=name,
            sort_name=sort_name,
            contributor_type=contributor_type,
            biography=biography,
            website_url=website_url
        )
        
        self.session.add(author)
        await self.session.flush()
        await self.session.refresh(author)
        return author
    
    async def search_authors(
        self,
        search_term: str,
        publisher_context: Optional[str] = None,
        contributor_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search authors with intelligent suggestions and context"""
        
        search_pattern = f'%{search_term}%'
        
        # Base query with book count and recent activity
        query = (
            select(
                Author,
                func.count(BookAuthor.book_id).label('book_count')
            )
            .outerjoin(BookAuthor)
            .where(
                or_(
                    Author.name.ilike(search_pattern),
                    Author.sort_name.ilike(search_pattern)
                )
            )
            .group_by(Author.id)
        )
        
        # Add contributor type filter if specified
        if contributor_type:
            query = query.where(Author.contributor_type == contributor_type)
        
        # Add publisher context - authors who have worked with this publisher
        if publisher_context:
            query = query.join(BookAuthor).join(Book).where(
                Book.publisher_id == publisher_context
            )
        
        query = query.order_by(func.count(BookAuthor.book_id).desc()).limit(limit)
        
        result = await self.session.execute(query)
        authors_with_counts = result.all()
        
        # Get additional details for each author
        enhanced_results = []
        for author, book_count in authors_with_counts:
            
            # Get recent books
            recent_books_result = await self.session.execute(
                select(Book.title)
                .join(BookAuthor)
                .where(BookAuthor.author_id == author.id)
                .order_by(Book.created_at.desc())
                .limit(3)
            )
            recent_books = [title for (title,) in recent_books_result.fetchall()]
            
            enhanced_results.append({
                'author': author,
                'book_count': book_count or 0,
                'recent_books': recent_books,
                'last_book': recent_books[0] if recent_books else None
            })
        
        return enhanced_results
    
    async def get_author_suggestions(
        self,
        publisher_id: Optional[str] = None,
        genre_hint: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get author suggestions based on publisher history and context"""
        
        query = (
            select(
                Author,
                func.count(BookAuthor.book_id).label('collaboration_count')
            )
            .join(BookAuthor)
            .join(Book)
        )
        
        if publisher_id:
            query = query.where(Book.publisher_id == publisher_id)
        
        # Group by author and order by collaboration frequency
        query = (
            query.group_by(Author.id)
            .order_by(func.count(BookAuthor.book_id).desc())
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        suggestions = result.all()
        
        enhanced_suggestions = []
        for author, collab_count in suggestions:
            enhanced_suggestions.append({
                'author': author,
                'collaboration_count': collab_count,
                'suggested_reason': f"Previously worked on {collab_count} books" + (f" with this publisher" if publisher_id else "")
            })
        
        return enhanced_suggestions
    
    async def get_author_with_books(self, author_id: str) -> Optional[Dict[str, Any]]:
        """Get author with full book details"""
        
        result = await self.session.execute(
            select(Author)
            .options(
                selectinload(Author.book_authors).selectinload(BookAuthor.book)
            )
            .where(Author.id == author_id)
        )
        
        author = result.scalar_one_or_none()
        if not author:
            return None
        
        # Calculate statistics
        books = author.books
        total_books = len(books)
        
        # Get role distribution
        role_distribution = {}
        for book_author in author.book_authors:
            role = book_author.contributor_role
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        return {
            'author': author,
            'books': books,
            'total_books': total_books,
            'role_distribution': role_distribution,
            'primary_role': max(role_distribution.items(), key=lambda x: x[1])[0] if role_distribution else author.contributor_type
        }
    
    async def find_potential_duplicates(self, name: str, threshold: float = 0.8) -> List[Author]:
        """Find potential duplicate authors based on name similarity"""
        
        # Simple approach - look for very similar names
        # In production, could use more sophisticated fuzzy matching
        name_parts = name.lower().split()
        
        conditions = []
        for part in name_parts:
            if len(part) > 2:  # Only consider meaningful parts
                conditions.append(Author.name.ilike(f'%{part}%'))
        
        if not conditions:
            return []
        
        query = select(Author).where(or_(*conditions))
        result = await self.session.execute(query)
        potential_matches = list(result.scalars().all())
        
        # Filter out exact matches and very dissimilar names
        filtered_matches = []
        for author in potential_matches:
            if author.name.lower() != name.lower():
                # Simple similarity check - could be enhanced
                similarity = self._calculate_name_similarity(name, author.name)
                if similarity >= threshold:
                    filtered_matches.append(author)
        
        return filtered_matches
    
    def _generate_sort_name(self, name: str) -> str:
        """Generate sort name (Last, First) from display name"""
        parts = name.strip().split()
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[-1]}, {parts[0]}"
        elif len(parts) > 2:
            # Assume last part is surname
            return f"{parts[-1]}, {' '.join(parts[:-1])}"
        return name
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Simple name similarity calculation"""
        # Very basic implementation - could be enhanced with proper string similarity algorithms
        name1_parts = set(name1.lower().split())
        name2_parts = set(name2.lower().split())
        
        if not name1_parts or not name2_parts:
            return 0.0
        
        intersection = len(name1_parts & name2_parts)
        union = len(name1_parts | name2_parts)
        
        return intersection / union if union > 0 else 0.0