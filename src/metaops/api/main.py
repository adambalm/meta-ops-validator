"""
MetaOps Validator API Gateway
FastAPI implementation of validation endpoints per MVP_API_SPEC.md
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

app = FastAPI(
    title="MetaOps Validator API",
    description="Pre-feed ONIX validation and metadata completeness scoring",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
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

# In-memory storage for validation results (use Redis/database in production)
validation_results: Dict[str, Dict] = {}
validation_status: Dict[str, str] = {}

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

# Authentication (simplified for MVP)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simplified JWT authentication for MVP."""
    token = credentials.credentials
    
    # For MVP, accept any non-empty token
    # In production, implement proper JWT validation
    if not token or len(token) < 10:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
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
    
    if file.size > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")
    
    # Generate validation ID
    validation_id = str(uuid4())
    
    # Initialize status tracking
    validation_status[validation_id] = "pending"
    validation_results[validation_id] = {
        "id": validation_id,
        "status": "pending",
        "filename": file.filename,
        "submitted_at": datetime.utcnow().isoformat(),
        "user_id": current_user["user_id"],
        "tenant": current_user["tenant"]
    }
    
    # Read file content before queuing (file will be closed after request)
    file_content = await file.read()
    
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
    
    if validation_id not in validation_results:
        raise HTTPException(status_code=404, detail="Validation not found")
    
    result = validation_results[validation_id]
    
    # Check tenant isolation
    if result.get("tenant") != current_user["tenant"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ValidationResult(**result)

@app.get("/api/v1/validations", response_model=List[ValidationResult])
async def list_validations(
    limit: int = 50,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List validation results for current user/tenant."""
    
    user_results = []
    for result in validation_results.values():
        if result.get("tenant") == current_user["tenant"]:
            if status_filter is None or result.get("status") == status_filter:
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
    
    if validation_id not in validation_results:
        raise HTTPException(status_code=404, detail="Validation not found")
    
    result = validation_results[validation_id]
    
    # Check tenant isolation
    if result.get("tenant") != current_user["tenant"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Remove from storage
    del validation_results[validation_id]
    if validation_id in validation_status:
        del validation_status[validation_id]
    
    return {"message": "Validation deleted successfully"}

@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_api_stats(current_user: dict = Depends(get_current_user)):
    """Get API usage statistics for current tenant."""
    
    tenant_results = [r for r in validation_results.values() if r.get("tenant") == current_user["tenant"]]
    
    total = len(tenant_results)
    completed = len([r for r in tenant_results if r.get("status") == "completed"])
    failed = len([r for r in tenant_results if r.get("status") == "failed"])
    
    # Calculate average processing time (simplified)
    avg_time = 0.0
    processing_times = []
    for r in tenant_results:
        if r.get("completed_at") and r.get("submitted_at"):
            submitted = datetime.fromisoformat(r["submitted_at"])
            completed_dt = datetime.fromisoformat(r["completed_at"])
            processing_times.append((completed_dt - submitted).total_seconds())
    
    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
    
    return StatsResponse(
        total_validations=total,
        completed_validations=completed,
        failed_validations=failed,
        average_processing_time=avg_time,
        popular_retailers=["amazon", "ingram", "apple"]  # Simplified for MVP
    )

async def process_validation(validation_id: str, file_content: bytes, filename: str, request: ValidationRequest):
    """Background task to process validation."""
    
    try:
        # Update status
        validation_status[validation_id] = "processing"
        validation_results[validation_id]["status"] = "processing"
        
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
            validation_results[validation_id].update({
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "results": {
                    "validation_findings": all_results,
                    "nielsen_score": nielsen_data,
                    "retailer_analysis": retailer_data
                },
                "pipeline_summary": pipeline_summary
            })
            
            validation_status[validation_id] = "completed"
            
        finally:
            # Clean up temporary file
            if temp_path.exists():
                os.unlink(temp_path)
                
    except Exception as e:
        # Handle validation errors
        validation_results[validation_id].update({
            "status": "failed",
            "completed_at": datetime.utcnow().isoformat(),
            "error": str(e)
        })
        validation_status[validation_id] = "failed"
        
        # Clean up on error
        try:
            if 'temp_path' in locals() and temp_path.exists():
                os.unlink(temp_path)
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)