"""
Repository layer for MetaOps demo application
Provides data access patterns for book-author-contract relationships
"""
from .base import BaseRepository
from .publisher_repository import PublisherRepository
from .book_repository import BookRepository
from .author_repository import AuthorRepository
from .contract_repository import ContractRepository

__all__ = [
    'BaseRepository',
    'PublisherRepository',
    'BookRepository',  
    'AuthorRepository',
    'ContractRepository'
]