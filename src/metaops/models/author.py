"""
Author model with ONIX contributor role support
"""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from .base import BaseModel

if False:  # TYPE_CHECKING  
    from .book import BookAuthor


class Author(BaseModel):
    __tablename__ = "authors"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # ONIX List 17: Contributor code (A01=Author, B01=Editor, etc.)
    contributor_type: Mapped[str] = mapped_column(String(10), default="A01", nullable=False)
    
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships (many-to-many through book_authors table)
    book_authors: Mapped[List["BookAuthor"]] = relationship("BookAuthor", back_populates="author")

    @property
    def books(self):
        """Get all books for this author"""
        return [book_author.book for book_author in self.book_authors]

    def __repr__(self) -> str:
        return f"<Author(id={self.id}, name='{self.name}', type='{self.contributor_type}')>"