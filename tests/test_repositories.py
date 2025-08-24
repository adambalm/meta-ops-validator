"""
Tests for MetaOps demo repositories
"""
import pytest
from datetime import date, datetime
from pathlib import Path
import tempfile
import os

from metaops.database.engine import create_database_engine, create_session_factory, create_tables
from metaops.repositories import (
    PublisherRepository,
    BookRepository,
    AuthorRepository,
    ContractRepository
)
from metaops.models.publisher import Publisher
from metaops.models.book import Book
from metaops.models.author import Author
from metaops.models.contract import Contract


@pytest.fixture
async def db_session():
    """Create temporary database session for testing"""
    # Create temporary SQLite database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    try:
        # Create engine and session factory
        database_url = f"sqlite+aiosqlite:///{db_path}"
        engine = create_database_engine(database_url)
        session_factory = create_session_factory(engine)
        
        # Create tables
        await create_tables(engine)
        
        # Create session
        async with session_factory() as session:
            yield session
            await session.rollback()
    
    finally:
        # Clean up temporary database
        try:
            os.unlink(db_path)
        except OSError:
            pass


@pytest.fixture
async def sample_publisher(db_session):
    """Create sample publisher for testing"""
    repo = PublisherRepository(db_session)
    publisher = await repo.create_publisher(
        name="Test Publisher",
        imprint="Test Imprint",
        territory_codes=["US", "CA"],
        validation_profile={"strict_mode": True}
    )
    await db_session.commit()
    return publisher


@pytest.fixture
async def sample_author(db_session):
    """Create sample author for testing"""
    repo = AuthorRepository(db_session)
    author = await repo.create_author(
        name="John Test Author",
        contributor_type="A01",
        biography="Test author biography"
    )
    await db_session.commit()
    return author


@pytest.fixture
async def sample_contract(db_session, sample_publisher):
    """Create sample contract for testing"""
    repo = ContractRepository(db_session)
    contract = await repo.create_contract(
        publisher_id=sample_publisher.id,
        contract_name="Test Contract",
        contract_type="distribution_agreement",
        retailer="test_retailer",
        effective_date=date.today(),
        territory_restrictions=["US"],
        validation_rules={"required_fields": ["isbn", "title"]}
    )
    await db_session.commit()
    return contract


class TestPublisherRepository:
    """Test PublisherRepository operations"""
    
    @pytest.mark.asyncio
    async def test_create_publisher(self, db_session):
        """Test publisher creation with all fields"""
        repo = PublisherRepository(db_session)
        
        publisher = await repo.create_publisher(
            name="Test Publisher Co",
            imprint="Test Books",
            territory_codes=["US", "UK", "CA"],
            validation_profile={"rule_set": "strict", "auto_approve": False}
        )
        
        assert publisher.id is not None
        assert publisher.name == "Test Publisher Co"
        assert publisher.imprint == "Test Books"
        assert publisher.territory_codes == ["US", "UK", "CA"]
        assert publisher.validation_profile["rule_set"] == "strict"
    
    @pytest.mark.asyncio
    async def test_get_publisher_with_stats(self, db_session, sample_publisher):
        """Test publisher statistics calculation"""
        repo = PublisherRepository(db_session)
        book_repo = BookRepository(db_session)
        
        # Create a book for the publisher
        await book_repo.create_book_with_validation(
            title="Test Book",
            isbn="9781234567890",
            publisher_id=sample_publisher.id,
            trigger_validation=False
        )
        await db_session.commit()
        
        stats = await repo.get_publisher_with_stats(sample_publisher.id)
        
        assert stats is not None
        assert stats['publisher'].id == sample_publisher.id
        assert stats['book_count'] == 1
        assert stats['validation_stats']['pending'] == 1
        assert isinstance(stats['compliance_rate'], float)
    
    @pytest.mark.asyncio
    async def test_search_publishers(self, db_session, sample_publisher):
        """Test publisher search functionality"""
        repo = PublisherRepository(db_session)
        
        results = await repo.search_publishers("Test")
        
        assert len(results) >= 1
        assert any(pub.name == sample_publisher.name for pub in results)


class TestBookRepository:
    """Test BookRepository operations"""
    
    @pytest.mark.asyncio
    async def test_create_book_with_validation(self, db_session, sample_publisher):
        """Test book creation with validation trigger"""
        repo = BookRepository(db_session)
        
        book = await repo.create_book_with_validation(
            title="Test Novel",
            isbn="9781234567891",
            publisher_id=sample_publisher.id,
            subtitle="A Test Story",
            publication_date=date(2024, 6, 15),
            onix_file_path="/test/path/onix.xml",
            trigger_validation=True
        )
        
        assert book.id is not None
        assert book.title == "Test Novel"
        assert book.isbn == "9781234567891"
        assert book.publisher_id == sample_publisher.id
        assert book.validation_status == "pending"
        assert book.onix_file_path == "/test/path/onix.xml"
    
    @pytest.mark.asyncio
    async def test_link_author_to_book(self, db_session, sample_publisher, sample_author):
        """Test author-book linking"""
        repo = BookRepository(db_session)
        
        # Create book
        book = await repo.create_book_with_validation(
            title="Test Book",
            isbn="9781234567892",
            publisher_id=sample_publisher.id,
            trigger_validation=False
        )
        await db_session.commit()
        
        # Link author
        book_author = await repo.link_author_to_book(
            book_id=book.id,
            author_id=sample_author.id,
            sequence_number=1,
            contributor_role="A01"
        )
        
        assert book_author.book_id == book.id
        assert book_author.author_id == sample_author.id
        assert book_author.sequence_number == 1
        assert book_author.contributor_role == "A01"
    
    @pytest.mark.asyncio
    async def test_get_book_with_details(self, db_session, sample_publisher, sample_author):
        """Test book detail retrieval with relationships"""
        repo = BookRepository(db_session)
        
        # Create book and link author
        book = await repo.create_book_with_validation(
            title="Detailed Test Book",
            isbn="9781234567893",
            publisher_id=sample_publisher.id,
            trigger_validation=False
        )
        await repo.link_author_to_book(book.id, sample_author.id)
        await db_session.commit()
        
        details = await repo.get_book_with_details(book.id)
        
        assert details is not None
        assert details['book'].title == "Detailed Test Book"
        assert details['publisher'].name == sample_publisher.name
        assert len(details['authors']) == 1
        assert details['authors'][0].name == sample_author.name
    
    @pytest.mark.asyncio
    async def test_search_books(self, db_session, sample_publisher):
        """Test book search functionality"""
        repo = BookRepository(db_session)
        
        # Create books
        await repo.create_book_with_validation(
            title="Mystery Novel",
            isbn="9781111111111",
            publisher_id=sample_publisher.id,
            trigger_validation=False
        )
        await repo.create_book_with_validation(
            title="Science Fiction Book",
            isbn="9782222222222",
            publisher_id=sample_publisher.id,
            trigger_validation=False
        )
        await db_session.commit()
        
        # Search by title
        results = await repo.search_books(search_term="Mystery")
        assert len(results) >= 1
        assert any(book.title == "Mystery Novel" for book in results)
        
        # Search by publisher
        results = await repo.search_books(publisher_id=sample_publisher.id)
        assert len(results) >= 2


class TestAuthorRepository:
    """Test AuthorRepository operations"""
    
    @pytest.mark.asyncio
    async def test_create_author(self, db_session):
        """Test author creation with sort name generation"""
        repo = AuthorRepository(db_session)
        
        author = await repo.create_author(
            name="Margaret Test Writer",
            contributor_type="A01",
            biography="Test biography"
        )
        
        assert author.id is not None
        assert author.name == "Margaret Test Writer"
        assert author.sort_name == "Writer, Margaret Test"
        assert author.contributor_type == "A01"
    
    @pytest.mark.asyncio
    async def test_search_authors(self, db_session, sample_author):
        """Test author search functionality"""
        repo = AuthorRepository(db_session)
        
        results = await repo.search_authors("John")
        
        assert len(results) >= 1
        found_author = next((r for r in results if r['author'].name == sample_author.name), None)
        assert found_author is not None
        assert found_author['book_count'] >= 0
    
    @pytest.mark.asyncio
    async def test_find_potential_duplicates(self, db_session):
        """Test duplicate author detection"""
        repo = AuthorRepository(db_session)
        
        # Create similar authors
        await repo.create_author(name="John Smith Writer")
        await repo.create_author(name="John Smith Author")  # More similar name
        await db_session.commit()
        
        duplicates = await repo.find_potential_duplicates("John Smith", threshold=0.5)  # Lower threshold
        
        assert len(duplicates) >= 1


class TestContractRepository:
    """Test ContractRepository operations"""
    
    @pytest.mark.asyncio
    async def test_create_contract(self, db_session, sample_publisher):
        """Test contract creation with JSON fields"""
        repo = ContractRepository(db_session)
        
        contract = await repo.create_contract(
            publisher_id=sample_publisher.id,
            contract_name="Test Distribution Agreement",
            contract_type="distribution_agreement",
            retailer="amazon",
            effective_date=date.today(),
            territory_restrictions=["US", "CA", "UK"],
            validation_rules={
                "required_fields": ["isbn", "title", "price"],
                "min_discount": 0.4
            }
        )
        
        assert contract.id is not None
        assert contract.contract_name == "Test Distribution Agreement"
        assert contract.territory_restrictions == ["US", "CA", "UK"]
        assert contract.validation_rules["min_discount"] == 0.4
    
    @pytest.mark.asyncio
    async def test_get_active_contracts(self, db_session, sample_contract):
        """Test active contract retrieval"""
        repo = ContractRepository(db_session)
        
        contracts = await repo.get_active_contracts(sample_contract.publisher_id)
        
        assert len(contracts) >= 1
        assert any(contract.id == sample_contract.id for contract in contracts)
    
    @pytest.mark.asyncio
    async def test_check_book_compliance(self, db_session, sample_publisher, sample_contract):
        """Test contract compliance checking"""
        repo = ContractRepository(db_session)
        book_repo = BookRepository(db_session)
        
        # Create book
        book = await book_repo.create_book_with_validation(
            title="Compliance Test Book",
            isbn="9781234567894",
            publisher_id=sample_publisher.id,
            trigger_validation=False
        )
        await db_session.commit()
        
        # Check compliance
        compliance_result = await repo.check_book_compliance(
            book_id=book.id,
            contract_id=sample_contract.id
        )
        
        assert 'compliant' in compliance_result
        assert 'status' in compliance_result
        assert 'violations' in compliance_result
        assert compliance_result['status'] in ['compliant', 'non_compliant', 'review_needed']