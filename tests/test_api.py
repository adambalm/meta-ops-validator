import pytest
from pathlib import Path
from metaops.api.state_manager import ValidationStateManager, ValidationState
from metaops.api.main import get_current_user
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException
from datetime import datetime


def test_validation_state_manager():
    """Test the ValidationStateManager functionality."""
    manager = ValidationStateManager()

    # Test state creation
    state = manager.create_validation("test-id", "test.xml", 1024, "user1", "tenant1")
    assert state.id == "test-id"
    assert state.filename == "test.xml"
    assert state.file_size == 1024
    assert state.status == "pending"

    # Test state retrieval
    retrieved = manager.get_validation("test-id")
    assert retrieved is not None
    assert retrieved.id == "test-id"

    # Test status updates
    assert manager.update_status("test-id", "processing")
    updated = manager.get_validation("test-id")
    assert updated.status == "processing"

    # Test results setting
    results = {"validation_findings": [], "nielsen_score": {"overall_score": 85}}
    assert manager.set_results("test-id", results)
    updated = manager.get_validation("test-id")
    assert updated.results == results

    # Test completion
    assert manager.update_status("test-id", "completed")
    updated = manager.get_validation("test-id")
    assert updated.status == "completed"
    assert updated.completed_at is not None


def test_validation_state_filtering():
    """Test validation state filtering by user and tenant."""
    manager = ValidationStateManager()

    # Create states for different users/tenants
    manager.create_validation("user1-1", "file1.xml", 1024, "user1", "tenant1")
    manager.create_validation("user1-2", "file2.xml", 2048, "user1", "tenant1")
    manager.create_validation("user2-1", "file3.xml", 1024, "user2", "tenant2")

    # Test filtering by user
    user1_states = manager.list_validations(user_id="user1")
    assert len(user1_states) == 2

    # Test filtering by tenant
    tenant1_states = manager.list_validations(tenant="tenant1")
    assert len(tenant1_states) == 2

    # Test combined filtering
    specific_states = manager.list_validations(user_id="user1", tenant="tenant1")
    assert len(specific_states) == 2


def test_api_authentication():
    """Test API authentication functionality."""
    # Test valid token
    valid_creds = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="demo.eyJ1c2VyX2lkIjoiZGVtb191c2VyIn0.signature"
    )
    user = get_current_user(valid_creds)
    assert user["user_id"] == "demo_user"
    assert user["tenant"] == "default"

    # Test invalid token format
    with pytest.raises(HTTPException) as exc_info:
        invalid_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")
        get_current_user(invalid_creds)
    assert exc_info.value.status_code == 401

    # Test missing token
    with pytest.raises(HTTPException) as exc_info:
        empty_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
        get_current_user(empty_creds)
    assert exc_info.value.status_code == 401


def test_validation_state_ttl():
    """Test TTL functionality of validation states."""
    manager = ValidationStateManager()

    # Create state with custom TTL (for testing, we'll modify the TTL directly)
    state = manager.create_validation("ttl-test", "test.xml", 1024, "user1")

    # Manually set TTL to past time for testing
    state.ttl_expires_at = datetime.utcnow().replace(year=2020)
    manager._states["ttl-test"] = state

    # Trigger cleanup
    manager._cleanup_expired()

    # State should be removed
    assert manager.get_validation("ttl-test") is None


def test_validation_state_stats():
    """Test validation statistics calculation."""
    manager = ValidationStateManager()

    # Create various states
    manager.create_validation("pending-1", "file1.xml", 1024, "user1")

    completed_state = manager.create_validation("completed-1", "file2.xml", 2048, "user1")
    manager.update_status("completed-1", "completed")

    failed_state = manager.create_validation("failed-1", "file3.xml", 1024, "user1")
    manager.update_status("failed-1", "failed")

    # Get stats
    stats = manager.get_stats()

    assert stats["total_validations"] == 3
    assert stats["completed_validations"] == 1
    assert stats["failed_validations"] == 1
    assert stats["pending_validations"] == 1
    assert "average_processing_time" in stats
