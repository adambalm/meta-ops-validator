"""
Book model with ONIX integration and validation tracking
"""
from sqlalchemy import String, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import date, datetime

from .base import BaseModel

if False:  # TYPE_CHECKING
    from .publisher import Publisher
    from .author import Author
    from .validation import ValidationSession, NielsenScore, ContractCompliance


class Book(BaseModel):
    __tablename__ = "books"

    isbn: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    subtitle: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    publisher_id: Mapped[str] = mapped_column(String(36), ForeignKey("publishers.id"), nullable=False)
    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # ONIX List 7: Product form ('BA'=Book, 'EA'=Digital)
    product_form: Mapped[str] = mapped_column(String(10), default="BA", nullable=False)
    
    # ONIX file metadata
    onix_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    onix_namespace_uri: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    onix_version: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Validation tracking
    last_validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    validation_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # 'pending', 'validated', 'failed'

    # Relationships
    publisher: Mapped["Publisher"] = relationship("Publisher", back_populates="books")
    book_authors: Mapped[List["BookAuthor"]] = relationship("BookAuthor", back_populates="book", cascade="all, delete-orphan")
    validation_sessions: Mapped[List["ValidationSession"]] = relationship("ValidationSession", back_populates="book")
    nielsen_scores: Mapped[List["NielsenScore"]] = relationship("NielsenScore", back_populates="book")
    compliance_results: Mapped[List["ContractCompliance"]] = relationship("ContractCompliance", back_populates="book")

    @property
    def authors(self):
        """Get all authors for this book"""
        return [book_author.author for book_author in self.book_authors]

    @property
    def latest_nielsen_score(self):
        """Get the most recent Nielsen score"""
        if self.nielsen_scores:
            return max(self.nielsen_scores, key=lambda x: x.calculated_at)
        return None

    @property
    def latest_validation_session(self):
        """Get the most recent validation session"""
        if self.validation_sessions:
            return max(self.validation_sessions, key=lambda x: x.created_at)
        return None

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, isbn='{self.isbn}', title='{self.title}')>"


class BookAuthor(BaseModel):
    """Association table for many-to-many relationship between books and authors"""
    __tablename__ = "book_authors"

    book_id: Mapped[str] = mapped_column(String(36), ForeignKey("books.id"), primary_key=True)
    author_id: Mapped[str] = mapped_column(String(36), ForeignKey("authors.id"), primary_key=True)
    
    sequence_number: Mapped[int] = mapped_column(default=1, nullable=False)  # Order for multiple authors
    contributor_role: Mapped[str] = mapped_column(String(10), default="A01", nullable=False)  # ONIX List 17 code

    # Relationships
    book: Mapped["Book"] = relationship("Book", back_populates="book_authors")
    author: Mapped["Author"] = relationship("Author", back_populates="book_authors")

    def __repr__(self) -> str:
        return f"<BookAuthor(book_id={self.book_id}, author_id={self.author_id}, role='{self.contributor_role}')>"