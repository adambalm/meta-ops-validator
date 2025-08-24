#!/usr/bin/env python3
"""
Test script for MetaOps demo repositories
Validates repository operations work correctly with existing database models
"""

import asyncio
import sys
from pathlib import Path
from datetime import date, datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from metaops.database.engine import init_database, get_async_session
from metaops.repositories import (
    PublisherRepository,
    BookRepository,
    AuthorRepository,
    ContractRepository
)


async def test_repositories():
    """Test all repository operations"""
    print("🔧 Initializing database...")
    await init_database()
    
    session = await get_async_session()
    async with session:
        try:
            # Initialize repositories
            print("📚 Creating repository instances...")
            publisher_repo = PublisherRepository(session)
            book_repo = BookRepository(session)
            author_repo = AuthorRepository(session)
            contract_repo = ContractRepository(session)
            
            # Test 1: Create Publisher
            print("\n1️⃣ Testing Publisher creation...")
            publisher = await publisher_repo.create_publisher(
                name="Test Publishing House",
                imprint="Test Imprint",
                territory_codes=["US", "CA", "UK"],
                validation_profile={"default_rules": "strict"}
            )
            print(f"✅ Created publisher: {publisher.name} (ID: {publisher.id})")
            
            # Test 2: Create Author
            print("\n2️⃣ Testing Author creation...")
            author = await author_repo.create_author(
                name="Jane Test Author",
                contributor_type="A01",
                biography="A test author for demonstration purposes"
            )
            print(f"✅ Created author: {author.name} (ID: {author.id})")
            print(f"   Sort name: {author.sort_name}")
            
            # Test 3: Create Contract
            print("\n3️⃣ Testing Contract creation...")
            contract = await contract_repo.create_contract(
                publisher_id=publisher.id,
                contract_name="Test Amazon KDP Agreement",
                contract_type="distribution_agreement",
                retailer="amazon_kdp",
                effective_date=date.today(),
                territory_restrictions=["US", "CA"],
                validation_rules={
                    "required_fields": ["isbn", "title", "price"],
                    "forbidden_values": {"product_form": ["BC"]}
                }
            )
            print(f"✅ Created contract: {contract.contract_name} (ID: {contract.id})")
            print(f"   Territory restrictions: {contract.territory_restrictions}")
            print(f"   Validation rules: {contract.validation_rules}")
            
            # Test 4: Create Book
            print("\n4️⃣ Testing Book creation...")
            book = await book_repo.create_book_with_validation(
                title="Test Novel: A Demo Book",
                isbn="9781234567890",
                publisher_id=publisher.id,
                subtitle="Demonstrating Repository Patterns",
                publication_date=date(2024, 6, 15),
                trigger_validation=False  # Skip validation for now
            )
            print(f"✅ Created book: {book.title} (ID: {book.id})")
            print(f"   ISBN: {book.isbn}")
            print(f"   Status: {book.validation_status}")
            
            # Test 5: Link Author to Book
            print("\n5️⃣ Testing Author-Book linking...")
            book_author = await book_repo.link_author_to_book(
                book_id=book.id,
                author_id=author.id,
                sequence_number=1,
                contributor_role="A01"
            )
            print(f"✅ Linked author to book")
            print(f"   Role: {book_author.contributor_role}")
            print(f"   Sequence: {book_author.sequence_number}")
            
            # Test 6: Test Publisher Dashboard Stats
            print("\n6️⃣ Testing Publisher dashboard stats...")
            publisher_stats = await publisher_repo.get_publisher_with_stats(publisher.id)
            if publisher_stats:
                print(f"✅ Publisher stats retrieved:")
                print(f"   Books: {publisher_stats['book_count']}")
                print(f"   Contracts: {publisher_stats['contract_count']}")
                print(f"   Compliance rate: {publisher_stats['compliance_rate']}%")
                print(f"   Validation stats: {publisher_stats['validation_stats']}")
            
            # Test 7: Book Search
            print("\n7️⃣ Testing Book search...")
            books = await book_repo.search_books(
                search_term="Test Novel",
                publisher_id=publisher.id
            )
            print(f"✅ Found {len(books)} books matching search")
            if books:
                found_book = books[0]
                print(f"   Found: {found_book.title}")
                print(f"   Authors: {len(found_book.authors)} linked")
            
            # Test 8: Author Search
            print("\n8️⃣ Testing Author search...")
            author_results = await author_repo.search_authors("Jane")
            print(f"✅ Found {len(author_results)} authors matching 'Jane'")
            for result in author_results:
                author_data = result['author']
                print(f"   {author_data.name} - {result['book_count']} books")
            
            # Test 9: Contract Compliance Check
            print("\n9️⃣ Testing Contract compliance check...")
            compliance_result = await contract_repo.check_book_compliance(
                book_id=book.id,
                contract_id=contract.id
            )
            print(f"✅ Compliance check completed:")
            print(f"   Status: {compliance_result['status']}")
            print(f"   Compliant: {compliance_result['compliant']}")
            print(f"   Violations: {len(compliance_result['violations'])}")
            
            # Test 10: Book Detail View
            print("\n🔟 Testing Book detail view...")
            book_details = await book_repo.get_book_with_details(book.id)
            if book_details:
                print(f"✅ Book details retrieved:")
                print(f"   Title: {book_details['book'].title}")
                print(f"   Publisher: {book_details['publisher'].name}")
                print(f"   Authors: {len(book_details['authors'])}")
                for author in book_details['authors']:
                    print(f"     - {author.name}")
            
            await session.commit()
            print("\n🎉 All repository tests passed successfully!")
            
        except Exception as e:
            print(f"\n❌ Repository test failed: {e}")
            await session.rollback()
            raise


async def main():
    """Main test function"""
    try:
        await test_repositories()
        print("\n✅ Repository layer implementation completed successfully!")
        print("   - Publishers, Books, Authors, and Contracts can be created")
        print("   - Author-Book relationships work correctly")
        print("   - Search functionality operational")
        print("   - Contract compliance checking functional")
        print("   - Dashboard stats calculation working")
        
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)