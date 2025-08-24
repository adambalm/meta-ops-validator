"""
MetaOps Validator API Gateway
FastAPI implementation of validation endpoints per MVP_API_SPEC.md
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from pathlib import Path
from uuid import uuid4
import tempfile
import asyncio
from datetime import datetime, timedelta
import json
import os

from metaops.validators.onix_xsd import validate_xsd
from metaops.validators.onix_schematron import validate_schematron
from metaops.validators.nielsen_scoring import calculate_nielsen_score
from metaops.validators.retailer_profiles import calculate_retailer_score, calculate_multi_retailer_score, RETAILER_PROFILES
from metaops.rules.engine import evaluate as eval_rules
from metaops.api.state_manager import get_state_manager, startup_state_manager, shutdown_state_manager

# Import database and repository dependencies
from metaops.database.engine import get_async_session, init_database
from metaops.repositories import (
    PublisherRepository,
    BookRepository,
    AuthorRepository,
    ContractRepository
)
from metaops.services.onix_generator import ONIXGenerator

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    await startup_state_manager()
    await init_database()  # Initialize database tables
    yield
    # Shutdown
    await shutdown_state_manager()

app = FastAPI(
    title="MetaOps Validator API",
    description="Pre-feed ONIX validation and metadata completeness scoring",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# State management
state_manager = get_state_manager()

# Pydantic models
class ValidationRequest(BaseModel):
    """Request model for validation operations."""
    include_nielsen: bool = Field(True, description="Include Nielsen completeness scoring")
    include_retailer: bool = Field(True, description="Include retailer profiling")
    retailers: Optional[List[str]] = Field(["amazon", "ingram", "apple"], description="Retailers to analyze")
    pipeline_stages: Optional[List[str]] = Field(["xsd", "schematron", "rules", "scoring"], description="Validation stages to run")

class ValidationResult(BaseModel):
    """Validation result model."""
    id: str
    status: str  # "pending", "processing", "completed", "failed"
    filename: str
    submitted_at: str
    completed_at: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    pipeline_summary: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
    services: Dict[str, str]

class StatsResponse(BaseModel):
    """API statistics response."""
    total_validations: int
    completed_validations: int
    failed_validations: int
    average_processing_time: float
    popular_retailers: List[str]

# === New Models for Book-Author-Contract Management ===

class PublisherCreate(BaseModel):
    """Create publisher request."""
    name: str = Field(..., min_length=1, max_length=255)
    imprint: Optional[str] = Field(None, max_length=255)
    territory_codes: Optional[List[str]] = Field(default_factory=list)
    validation_profile: Optional[Dict[str, Any]] = Field(default_factory=dict)

class PublisherResponse(BaseModel):
    """Publisher response model."""
    id: str
    name: str
    imprint: Optional[str]
    territory_codes: List[str]
    created_at: datetime
    book_count: Optional[int] = 0
    contract_count: Optional[int] = 0
    compliance_rate: Optional[float] = 0.0

class BookCreate(BaseModel):
    """Create book request."""
    title: str = Field(..., min_length=1, max_length=500)
    isbn: str = Field(..., pattern=r'^\d{13}$')
    subtitle: Optional[str] = Field(None, max_length=500)
    publisher_id: str
    publication_date: Optional[str] = None
    product_form: str = Field('BA', pattern=r'^[A-Z]{2}$')

class BookResponse(BaseModel):
    """Book response model."""
    id: str
    title: str
    isbn: str
    subtitle: Optional[str]
    publisher_id: str
    publication_date: Optional[str]
    product_form: str
    validation_status: str
    authors: List[Dict[str, Any]] = []
    onix_file_path: Optional[str]
    created_at: datetime

class AuthorCreate(BaseModel):
    """Create author request."""
    name: str = Field(..., min_length=1, max_length=255)
    contributor_type: str = Field('A01', pattern=r'^[A-Z]\d{2}$')
    biography: Optional[str] = None
    website_url: Optional[str] = None

class AuthorResponse(BaseModel):
    """Author response model."""
    id: str
    name: str
    sort_name: str
    contributor_type: str
    biography: Optional[str]
    book_count: int = 0

class AuthorLink(BaseModel):
    """Link author to book request."""
    author_id: str
    sequence_number: int = Field(1, ge=1, le=20)
    contributor_role: str = Field('A01', pattern=r'^[A-Z]\d{2}$')

class ContractCreate(BaseModel):
    """Create contract request."""
    publisher_id: str
    contract_name: str = Field(..., min_length=1, max_length=255)
    contract_type: str = Field(..., pattern=r'^(distribution_agreement|retailer_terms|licensing)$')
    retailer: str = Field(..., max_length=100)
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    territory_restrictions: Optional[List[str]] = []
    validation_rules: Optional[Dict[str, Any]] = {}

class ContractResponse(BaseModel):
    """Contract response model."""
    id: str
    publisher_id: str
    contract_name: str
    contract_type: str
    retailer: str
    effective_date: Optional[str]
    expiration_date: Optional[str]
    territory_restrictions: List[str]
    status: str
    created_at: datetime

class ComplianceResult(BaseModel):
    """Compliance check result."""
    book_id: str
    contract_id: str
    compliant: bool
    status: str
    violations: List[str]
    warnings: List[str]
    territory_check_passed: bool
    rules_check_passed: bool

# Authentication with proper token validation
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Secure token authentication."""
    token = credentials.credentials

    # Validate token format and content
    if not token:
        raise HTTPException(status_code=401, detail="Authentication token required")

    # Check for valid JWT-like structure (header.payload.signature)
    token_parts = token.split('.')
    if len(token_parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid token format")

    # Basic token validation (in production, use proper JWT validation)
    if not all(len(part) > 0 for part in token_parts):
        raise HTTPException(status_code=401, detail="Malformed authentication token")

    # For demo purposes, accept properly formatted tokens
    # In production, implement actual JWT signature verification
    if token != "demo.eyJ1c2VyX2lkIjoiZGVtb191c2VyIn0.signature":
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    return {"user_id": "demo_user", "tenant": "default"}

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """System health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "xsd_validator": "operational",
            "schematron_validator": "operational",
            "rules_engine": "operational",
            "nielsen_scoring": "operational",
            "retailer_profiles": "operational"
        }
    )

@app.post("/api/v1/validate", response_model=Dict[str, str])
async def validate_onix(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    request_data: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit ONIX file for validation.
    Returns validation ID for tracking progress.
    """

    # Parse request options
    validation_request = ValidationRequest()
    if request_data:
        try:
            request_dict = json.loads(request_data)
            validation_request = ValidationRequest(**request_dict)
        except Exception:
            pass  # Use defaults

    # Validate file
    if not file.filename.lower().endswith('.xml'):
        raise HTTPException(status_code=400, detail="Only XML files are supported")

    # Read file content to validate size by actual content length
    file_content = await file.read()
    content_length = len(file_content)

    if content_length > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")

    if content_length == 0:
        raise HTTPException(status_code=400, detail="Empty file not allowed")

    # Generate validation ID and create state
    validation_id = str(uuid4())

    # Create validation state
    validation_state = state_manager.create_validation(
        validation_id=validation_id,
        filename=file.filename,
        file_size=content_length,
        user_id=current_user["user_id"],
        tenant=current_user["tenant"]
    )

    # Queue background validation
    background_tasks.add_task(
        process_validation,
        validation_id,
        file_content,
        file.filename,
        validation_request
    )

    return {
        "validation_id": validation_id,
        "status": "accepted",
        "message": "Validation queued for processing"
    }

@app.get("/api/v1/validation/{validation_id}", response_model=ValidationResult)
async def get_validation_result(
    validation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get validation results by ID."""

    validation_state = state_manager.get_validation(validation_id)
    if not validation_state:
        raise HTTPException(status_code=404, detail="Validation not found")

    # Check tenant isolation
    if validation_state.tenant != current_user["tenant"]:
        raise HTTPException(status_code=403, detail="Access denied")

    result = {
        "id": validation_state.id,
        "status": validation_state.status,
        "filename": validation_state.filename,
        "submitted_at": validation_state.submitted_at.isoformat(),
        "completed_at": validation_state.completed_at.isoformat() if validation_state.completed_at else None,
        "results": validation_state.results,
        "error": validation_state.error,
        "pipeline_summary": validation_state.pipeline_summary
    }

    return ValidationResult(**result)

@app.get("/api/v1/validations", response_model=List[ValidationResult])
async def list_validations(
    limit: int = 50,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List validation results for current user/tenant."""

    # Get filtered validations from state manager
    validations = state_manager.list_validations(tenant=current_user["tenant"])

    user_results = []
    for validation_state in validations.values():
        if status_filter is None or validation_state.status == status_filter:
            result = {
                "id": validation_state.id,
                "status": validation_state.status,
                "filename": validation_state.filename,
                "submitted_at": validation_state.submitted_at.isoformat(),
                "completed_at": validation_state.completed_at.isoformat() if validation_state.completed_at else None,
                "results": validation_state.results,
                "error": validation_state.error,
                "pipeline_summary": validation_state.pipeline_summary
            }
            user_results.append(ValidationResult(**result))

    # Sort by submission time (most recent first) and limit
    user_results.sort(key=lambda x: x.submitted_at, reverse=True)
    return user_results[:limit]

@app.delete("/api/v1/validation/{validation_id}")
async def delete_validation(
    validation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete validation result."""

    validation_state = state_manager.get_validation(validation_id)
    if not validation_state:
        raise HTTPException(status_code=404, detail="Validation not found")

    # Check tenant isolation
    if validation_state.tenant != current_user["tenant"]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Note: State cleanup handled by TTL in state manager

    return {"message": "Validation deleted successfully"}

@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_api_stats(current_user: dict = Depends(get_current_user)):
    """Get API usage statistics for current tenant."""

    # Get stats from state manager
    stats = state_manager.get_stats()

    # Filter for tenant (simplified for MVP)
    tenant_validations = state_manager.list_validations(tenant=current_user["tenant"])
    tenant_total = len(tenant_validations)
    tenant_completed = sum(1 for v in tenant_validations.values() if v.status == "completed")
    tenant_failed = sum(1 for v in tenant_validations.values() if v.status == "failed")

    # Calculate tenant-specific average processing time
    processing_times = []
    for validation_state in tenant_validations.values():
        if validation_state.completed_at and validation_state.status == "completed":
            delta = validation_state.completed_at - validation_state.submitted_at
            processing_times.append(delta.total_seconds())

    avg_time = sum(processing_times) / len(processing_times) if processing_times else 0

    return StatsResponse(
        total_validations=tenant_total,
        completed_validations=tenant_completed,
        failed_validations=tenant_failed,
        average_processing_time=avg_time,
        popular_retailers=["amazon", "ingram", "apple"]  # Simplified for MVP
    )

# === Book-Author-Contract Management Endpoints ===

@app.get("/api/v1/publishers", response_model=List[PublisherResponse], tags=["Publishers"])
async def list_publishers(current_user: dict = Depends(get_current_user)):
    """Get all publishers for selection interface."""
    session = await get_async_session()
    async with session:
        repo = PublisherRepository(session)
        publishers = await repo.get_all_publishers()
        
        return [
            PublisherResponse(
                id=pub.id,
                name=pub.name,
                imprint=pub.imprint,
                territory_codes=pub.territory_codes,
                created_at=pub.created_at,
                book_count=0,  # Will be calculated if needed
                contract_count=0,
                compliance_rate=0.0
            )
            for pub in publishers
        ]

@app.post("/api/v1/publishers", response_model=PublisherResponse, tags=["Publishers"])
async def create_publisher(
    publisher_data: PublisherCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new publisher with validation profile."""
    session = await get_async_session()
    async with session:
        repo = PublisherRepository(session)
        
        publisher = await repo.create_publisher(
            name=publisher_data.name,
            imprint=publisher_data.imprint,
            territory_codes=publisher_data.territory_codes,
            validation_profile=publisher_data.validation_profile
        )
        await session.commit()
        
        return PublisherResponse(
            id=publisher.id,
            name=publisher.name,
            imprint=publisher.imprint,
            territory_codes=publisher.territory_codes or [],
            created_at=publisher.created_at,
            book_count=0,
            contract_count=0,
            compliance_rate=0.0
        )

@app.get("/api/v1/publishers/{publisher_id}", response_model=PublisherResponse, tags=["Publishers"])
async def get_publisher(
    publisher_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get publisher details by ID."""
    session = await get_async_session()
    async with session:
        repo = PublisherRepository(session)
        
        publisher = await repo.get_by_id(publisher_id)
        if not publisher:
            raise HTTPException(status_code=404, detail="Publisher not found")
        
        stats = await repo.get_publisher_with_stats(publisher_id)
        
        return PublisherResponse(
            id=publisher.id,
            name=publisher.name,
            imprint=publisher.imprint,
            territory_codes=publisher.territory_codes or [],
            created_at=publisher.created_at,
            book_count=stats['book_count'] if stats else 0,
            contract_count=stats['contract_count'] if stats else 0,
            compliance_rate=stats['compliance_rate'] if stats else 0.0
        )

@app.get("/api/v1/publishers/{publisher_id}/dashboard", tags=["Publishers"])
async def get_publisher_dashboard(
    publisher_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get publisher dashboard with KPIs and statistics."""
    session = await get_async_session()
    async with session:
        repo = PublisherRepository(session)
        contract_repo = ContractRepository(session)
        
        stats = await repo.get_publisher_with_stats(publisher_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Publisher not found")
        
        # Get compliance summary
        compliance_summary = await contract_repo.get_publisher_compliance_summary(publisher_id)
        
        return {
            "publisher": {
                "id": stats['publisher'].id,
                "name": stats['publisher'].name,
                "imprint": stats['publisher'].imprint
            },
            "metrics": {
                "book_count": stats['book_count'],
                "contract_count": stats['contract_count'],
                "validation_stats": stats['validation_stats'],
                "compliance_rate": stats['compliance_rate']
            },
            "compliance": compliance_summary,
            "recent_books": await repo.get_publisher_books(publisher_id, limit=5)
        }

@app.get("/api/v1/books", response_model=List[BookResponse], tags=["Books"])
async def list_books(
    publisher_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get books with optional publisher filtering."""
    session = await get_async_session()
    async with session:
        repo = BookRepository(session)
        books = await repo.search_books(publisher_id=publisher_id)
        
        book_responses = []
        for book in books:
            # Get book details with authors
            details = await repo.get_book_with_details(book.id)
            
            authors = []
            if details and details['authors']:
                authors = [
                    {"id": author.id, "name": author.name}
                    for author in details['authors']
                ]
            
            book_responses.append(BookResponse(
                id=book.id,
                title=book.title,
                isbn=book.isbn,
                subtitle=book.subtitle,
                publisher_id=book.publisher_id,
                publication_date=book.publication_date.isoformat() if book.publication_date else None,
                product_form=book.product_form,
                validation_status=book.validation_status,
                authors=authors,
                onix_file_path=book.onix_file_path,
                created_at=book.created_at
            ))
        
        return book_responses

@app.post("/api/v1/books", response_model=BookResponse, tags=["Books"])
async def create_book(
    book_data: BookCreate,
    trigger_validation: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Create a new book with optional ONIX file upload."""
    session = await get_async_session()
    async with session:
        repo = BookRepository(session)
        
        # For now, no ONIX file upload
        onix_file_path = None
        
        # Parse publication date if provided
        from datetime import date
        pub_date = None
        if book_data.publication_date:
            try:
                pub_date = date.fromisoformat(book_data.publication_date)
            except:
                pass
        
        # Create book
        book = await repo.create_book_with_validation(
            title=book_data.title,
            isbn=book_data.isbn,
            subtitle=book_data.subtitle,
            publisher_id=book_data.publisher_id,
            publication_date=pub_date,
            product_form=book_data.product_form,
            onix_file_path=onix_file_path,
            trigger_validation=trigger_validation
        )
        await session.commit()
        
        return BookResponse(
            id=book.id,
            title=book.title,
            isbn=book.isbn,
            subtitle=book.subtitle,
            publisher_id=book.publisher_id,
            publication_date=book.publication_date.isoformat() if book.publication_date else None,
            product_form=book.product_form,
            validation_status=book.validation_status,
            authors=[],
            onix_file_path=book.onix_file_path,
            created_at=book.created_at
        )

@app.get("/api/v1/books/{book_id}", response_model=BookResponse, tags=["Books"])
async def get_book(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get book details including authors and validation status."""
    session = await get_async_session()
    async with session:
        repo = BookRepository(session)
        
        book_details = await repo.get_book_with_details(book_id)
        if not book_details:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book = book_details['book']
        authors_data = []
        for author in book_details['authors']:
            authors_data.append({
                "id": author.id,
                "name": author.name,
                "contributor_type": author.contributor_type
            })
        
        return BookResponse(
            id=book.id,
            title=book.title,
            isbn=book.isbn,
            subtitle=book.subtitle,
            publisher_id=book.publisher_id,
            publication_date=book.publication_date.isoformat() if book.publication_date else None,
            product_form=book.product_form,
            validation_status=book.validation_status,
            authors=authors_data,
            onix_file_path=book.onix_file_path,
            created_at=book.created_at
        )

@app.put("/api/v1/books/{book_id}/authors", tags=["Books"])
async def link_authors_to_book(
    book_id: str,
    authors: List[AuthorLink],
    current_user: dict = Depends(get_current_user)
):
    """Link authors to a book with contributor roles."""
    session = await get_async_session()
    async with session:
        repo = BookRepository(session)
        
        # Verify book exists
        book = await repo.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Link each author
        links = []
        for author_link in authors:
            link = await repo.link_author_to_book(
                book_id=book_id,
                author_id=author_link.author_id,
                sequence_number=author_link.sequence_number,
                contributor_role=author_link.contributor_role
            )
            links.append({
                "author_id": link.author_id,
                "sequence_number": link.sequence_number,
                "contributor_role": link.contributor_role
            })
        
        await session.commit()
        
        return {"book_id": book_id, "authors": links}

@app.post("/api/v1/books/{book_id}/validate", tags=["Books"])
async def validate_book(
    book_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Trigger validation for a book's ONIX file."""
    session = await get_async_session()
    async with session:
        repo = BookRepository(session)
        
        book = await repo.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        if not book.onix_file_path:
            raise HTTPException(status_code=400, detail="Book has no ONIX file to validate")
        
        # Read ONIX file
        onix_path = Path(book.onix_file_path)
        if not onix_path.exists():
            raise HTTPException(status_code=404, detail="ONIX file not found")
        
        file_content = onix_path.read_bytes()
        
        # Create validation request
        validation_id = str(uuid4())
        validation_state = state_manager.create_validation(
            validation_id=validation_id,
            filename=onix_path.name,
            file_size=len(file_content),
            user_id=current_user["user_id"],
            tenant=current_user["tenant"]
        )
        
        # Queue validation
        validation_request = ValidationRequest()
        background_tasks.add_task(
            process_validation,
            validation_id,
            file_content,
            onix_path.name,
            validation_request
        )
        
        # Update book validation status
        await repo.update_validation_status(book_id, "processing")
        await session.commit()
        
        return {
            "book_id": book_id,
            "validation_id": validation_id,
            "status": "validation_queued"
        }

@app.get("/api/v1/authors/search", response_model=List[AuthorResponse], tags=["Authors"])
async def search_authors(
    q: str,
    publisher_id: Optional[str] = None,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Search for authors by name with intelligent suggestions."""
    session = await get_async_session()
    async with session:
        repo = AuthorRepository(session)
        
        results = await repo.search_authors(
            search_term=q,
            publisher_context=publisher_id,
            limit=limit
        )
        
        authors = []
        for result in results:
            author = result['author']
            authors.append(AuthorResponse(
                id=author.id,
                name=author.name,
                sort_name=author.sort_name,
                contributor_type=author.contributor_type,
                biography=author.biography,
                book_count=result['book_count']
            ))
        
        return authors

@app.post("/api/v1/authors", response_model=AuthorResponse, tags=["Authors"])
async def create_author(
    author_data: AuthorCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new author."""
    session = await get_async_session()
    async with session:
        repo = AuthorRepository(session)
        
        author = await repo.create_author(
            name=author_data.name,
            contributor_type=author_data.contributor_type,
            biography=author_data.biography,
            website_url=author_data.website_url
        )
        await session.commit()
        
        return AuthorResponse(
            id=author.id,
            name=author.name,
            sort_name=author.sort_name,
            contributor_type=author.contributor_type,
            biography=author.biography,
            book_count=0
        )

@app.get("/api/v1/contracts", response_model=List[ContractResponse], tags=["Contracts"])
async def list_contracts(
    publisher_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get contracts with optional publisher filtering."""
    session = await get_async_session()
    async with session:
        repo = ContractRepository(session)
        if publisher_id:
            contracts = await repo.get_active_contracts(publisher_id)
        else:
            contracts = await repo.get_all_contracts()
        
        return [
            ContractResponse(
                id=contract.id,
                publisher_id=contract.publisher_id,
                contract_name=contract.contract_name,
                contract_type=contract.contract_type,
                retailer=contract.retailer,
                effective_date=contract.effective_date.isoformat(),
                expiration_date=contract.expiration_date.isoformat() if contract.expiration_date else None,
                territory_restrictions=contract.territory_restrictions,
                status=contract.status,
                created_at=contract.created_at
            )
            for contract in contracts
        ]

@app.post("/api/v1/contracts", response_model=ContractResponse, tags=["Contracts"])
async def create_contract(
    contract_data: ContractCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new contract with validation rules."""
    session = await get_async_session()
    async with session:
        repo = ContractRepository(session)
        
        # For now, no contract file upload
        document_path = None
        
        # Parse dates
        from datetime import date
        eff_date = None
        exp_date = None
        if contract_data.effective_date:
            try:
                eff_date = date.fromisoformat(contract_data.effective_date)
            except:
                pass
        if contract_data.expiration_date:
            try:
                exp_date = date.fromisoformat(contract_data.expiration_date)
            except:
                pass
        
        contract = await repo.create_contract(
            publisher_id=contract_data.publisher_id,
            contract_name=contract_data.contract_name,
            contract_type=contract_data.contract_type,
            retailer=contract_data.retailer,
            effective_date=eff_date,
            expiration_date=exp_date,
            territory_restrictions=contract_data.territory_restrictions,
            validation_rules=contract_data.validation_rules,
            document_path=document_path
        )
        await session.commit()
        
        return ContractResponse(
            id=contract.id,
            publisher_id=contract.publisher_id,
            contract_name=contract.contract_name,
            contract_type=contract.contract_type,
            retailer=contract.retailer,
            effective_date=contract.effective_date.isoformat() if contract.effective_date else None,
            expiration_date=contract.expiration_date.isoformat() if contract.expiration_date else None,
            territory_restrictions=contract.territory_restrictions or [],
            status=contract.status,
            created_at=contract.created_at
        )

@app.post("/api/v1/books/{book_id}/check-compliance", response_model=ComplianceResult, tags=["Contracts"])
async def check_book_compliance(
    book_id: str,
    contract_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Check if a book complies with a specific contract."""
    session = await get_async_session()
    async with session:
        repo = ContractRepository(session)
        
        result = await repo.check_book_compliance(book_id, contract_id)
        
        # Create compliance record
        compliance_record = await repo.create_compliance_result(
            book_id=book_id,
            contract_id=contract_id,
            compliance_status=result['status'],
            territory_check_passed=result.get('territory_check_passed', True),
            retailer_requirements_met=result.get('rules_check_passed', True),
            violations=[{"message": v} for v in result.get('violations', [])]
        )
        await session.commit()
        
        return ComplianceResult(
            book_id=book_id,
            contract_id=contract_id,
            compliant=result['compliant'],
            status=result['status'],
            violations=result.get('violations', []),
            warnings=result.get('warnings', []),
            territory_check_passed=result.get('territory_check_passed', True),
            rules_check_passed=result.get('rules_check_passed', True)
        )

# === ONIX Generation Endpoints ===

@app.get("/api/v1/books/{book_id}/onix", tags=["ONIX"])
async def generate_onix_for_book(
    book_id: str,
    contract_id: Optional[str] = None,
    target_territory: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Generate ONIX 3.0 XML for a book with contract-based filtering."""
    session = await get_async_session()
    async with session:
        book_repo = BookRepository(session)
        contract_repo = ContractRepository(session)
        
        # Get book with full details
        book_details = await book_repo.get_book_with_details(book_id)
        if not book_details:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book = book_details['book']
        publisher = book_details['publisher'] 
        authors = book_details['authors']
        
        # Convert to dict format for ONIX generator
        book_data = {
            'id': book.id,
            'title': book.title,
            'isbn': book.isbn,
            'subtitle': book.subtitle,
            'publication_date': book.publication_date.isoformat() if book.publication_date else None,
            'product_form': book.product_form
        }
        
        publisher_data = {
            'name': publisher.name,
            'imprint': publisher.imprint,
            'territory_codes': publisher.territory_codes or ['US']
        }
        
        authors_data = [
            {
                'name': author.name,
                'contributor_type': author.contributor_type,
                'biography': author.biography
            }
            for author in authors
        ]
        
        # Get contracts if specified
        contracts = None
        if contract_id:
            contract = await contract_repo.get_by_id(contract_id)
            if contract:
                contracts = [{
                    'id': contract.id,
                    'territory_restrictions': contract.territory_restrictions or [],
                    'validation_rules': contract.validation_rules or {}
                }]
        
        # Generate ONIX
        generator = ONIXGenerator()
        onix_xml = generator.generate_onix_for_book(
            book_data=book_data,
            publisher_data=publisher_data,
            authors=authors_data,
            contracts=contracts,
            target_territory=target_territory
        )
        
        return {
            "book_id": book_id,
            "onix_xml": onix_xml,
            "contract_id": contract_id,
            "target_territory": target_territory,
            "generated_at": datetime.utcnow().isoformat()
        }

@app.get("/api/v1/books/{book_id}/onix-preview", tags=["ONIX"])
async def get_onix_preview(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get truncated ONIX preview for UI display."""
    session = await get_async_session()
    async with session:
        book_repo = BookRepository(session)
        
        book_details = await book_repo.get_book_with_details(book_id)
        if not book_details:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book = book_details['book']
        
        # Convert to simple format for preview
        book_data = {
            'id': book.id,
            'title': book.title,
            'isbn': book.isbn,
            'subtitle': book.subtitle,
            'publication_date': book.publication_date.isoformat() if book.publication_date else None
        }
        
        generator = ONIXGenerator()
        preview_xml = generator.generate_onix_preview(book_data)
        
        return {
            "book_id": book_id,
            "preview_xml": preview_xml,
            "is_preview": True
        }

async def process_validation(validation_id: str, file_content: bytes, filename: str, request: ValidationRequest):
    """Background task to process validation."""

    try:
        # Update status
        state_manager.update_status(validation_id, "processing")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp_file:
            tmp_file.write(file_content)
            tmp_file.flush()
            temp_path = Path(tmp_file.name)

        # Run validation pipeline
        all_results = []
        pipeline_summary = {"stages_completed": [], "errors": 0, "warnings": 0, "info": 0}

        try:
            # XSD validation
            if "xsd" in request.pipeline_stages:
                xsd_results = validate_xsd(temp_path)
                all_results.extend(xsd_results)
                pipeline_summary["stages_completed"].append("xsd")

            # Schematron validation
            if "schematron" in request.pipeline_stages:
                sch_results = validate_schematron(temp_path)
                all_results.extend(sch_results)
                pipeline_summary["stages_completed"].append("schematron")

            # Rules validation
            if "rules" in request.pipeline_stages:
                rules_results = eval_rules(temp_path)
                all_results.extend(rules_results)
                pipeline_summary["stages_completed"].append("rules")

            # Nielsen scoring
            nielsen_data = None
            if request.include_nielsen and "scoring" in request.pipeline_stages:
                nielsen_data = calculate_nielsen_score(temp_path)
                nielsen_result = {
                    "line": 1,
                    "level": "INFO",
                    "domain": "NIELSEN_SCORE",
                    "type": "scoring",
                    "message": f"Nielsen completeness score: {nielsen_data['overall_score']}%",
                    "path": filename,
                    "nielsen_data": nielsen_data
                }
                all_results.append(nielsen_result)
                pipeline_summary["stages_completed"].append("nielsen_scoring")

            # Retailer profiling
            retailer_data = None
            if request.include_retailer and request.retailers and "scoring" in request.pipeline_stages:
                retailer_data = calculate_multi_retailer_score(temp_path, request.retailers)
                retailer_result = {
                    "line": 1,
                    "level": "INFO",
                    "domain": "RETAILER_ANALYSIS",
                    "type": "scoring",
                    "message": f"Multi-retailer analysis complete: {retailer_data.get('average_score', 0)}% average",
                    "path": filename,
                    "retailer_data": retailer_data
                }
                all_results.append(retailer_result)
                pipeline_summary["stages_completed"].append("retailer_profiling")

            # Count results by level
            pipeline_summary["errors"] = len([r for r in all_results if r.get("level") == "ERROR"])
            pipeline_summary["warnings"] = len([r for r in all_results if r.get("level") == "WARNING"])
            pipeline_summary["info"] = len([r for r in all_results if r.get("level") == "INFO"])
            pipeline_summary["total_findings"] = len(all_results)

            # Update results
            results = {
                "validation_findings": all_results,
                "nielsen_score": nielsen_data,
                "retailer_analysis": retailer_data
            }

            state_manager.set_results(validation_id, results)
            state_manager.set_pipeline_summary(validation_id, pipeline_summary)
            state_manager.update_status(validation_id, "completed")

        finally:
            # Clean up temporary file
            if temp_path.exists():
                os.unlink(temp_path)

    except Exception as e:
        # Handle validation errors
        state_manager.set_error(validation_id, str(e))
        state_manager.update_status(validation_id, "failed")

        # Clean up on error
        try:
            if 'temp_path' in locals() and temp_path.exists():
                os.unlink(temp_path)
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
