"""
Validation State Management
Thread-safe storage for validation results with TTL cleanup.
"""

import asyncio
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
import weakref


@dataclass
class ValidationState:
    """Individual validation state with metadata."""
    id: str
    status: str
    filename: str
    file_size: int
    submitted_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    user_id: str = ""
    tenant: str = "default"
    pipeline_summary: Optional[Dict[str, Any]] = None
    ttl_expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24))


class ValidationStateManager:
    """Thread-safe validation state manager with TTL cleanup."""

    def __init__(self, cleanup_interval: int = 3600):  # 1 hour cleanup interval
        self._states: Dict[str, ValidationState] = {}
        self._lock = threading.RLock()
        self._cleanup_interval = cleanup_interval
        self._cleanup_task = None
        self._shutdown = False

    async def start_cleanup_task(self):
        """Start the TTL cleanup background task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup_task(self):
        """Stop the TTL cleanup background task."""
        self._shutdown = True
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self):
        """Background task to cleanup expired validation states."""
        while not self._shutdown:
            try:
                await asyncio.sleep(self._cleanup_interval)
                self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception:
                # Continue cleanup on errors
                pass

    def _cleanup_expired(self):
        """Remove expired validation states."""
        now = datetime.now(timezone.utc)
        with self._lock:
            expired_ids = [
                validation_id for validation_id, state in self._states.items()
                if state.ttl_expires_at <= now
            ]
            for validation_id in expired_ids:
                del self._states[validation_id]

    def create_validation(self, validation_id: str, filename: str, file_size: int,
                         user_id: str, tenant: str = "default") -> ValidationState:
        """Create a new validation state."""
        state = ValidationState(
            id=validation_id,
            status="pending",
            filename=filename,
            file_size=file_size,
            submitted_at=datetime.now(timezone.utc),
            user_id=user_id,
            tenant=tenant
        )

        with self._lock:
            self._states[validation_id] = state

        return state

    def get_validation(self, validation_id: str) -> Optional[ValidationState]:
        """Get validation state by ID."""
        with self._lock:
            return self._states.get(validation_id)

    def update_status(self, validation_id: str, status: str) -> bool:
        """Update validation status."""
        with self._lock:
            if validation_id in self._states:
                self._states[validation_id].status = status
                if status in ["completed", "failed"]:
                    self._states[validation_id].completed_at = datetime.now(timezone.utc)
                return True
            return False

    def set_results(self, validation_id: str, results: Dict[str, Any]) -> bool:
        """Set validation results."""
        with self._lock:
            if validation_id in self._states:
                self._states[validation_id].results = results
                return True
            return False

    def set_error(self, validation_id: str, error: str) -> bool:
        """Set validation error."""
        with self._lock:
            if validation_id in self._states:
                self._states[validation_id].error = error
                return True
            return False

    def set_pipeline_summary(self, validation_id: str, summary: Dict[str, Any]) -> bool:
        """Set pipeline summary."""
        with self._lock:
            if validation_id in self._states:
                self._states[validation_id].pipeline_summary = summary
                return True
            return False

    def list_validations(self, user_id: Optional[str] = None,
                        tenant: Optional[str] = None) -> Dict[str, ValidationState]:
        """List validation states with optional filtering."""
        with self._lock:
            if user_id is None and tenant is None:
                return dict(self._states)

            filtered = {}
            for validation_id, state in self._states.items():
                if user_id and state.user_id != user_id:
                    continue
                if tenant and state.tenant != tenant:
                    continue
                filtered[validation_id] = state

            return filtered

    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        with self._lock:
            total = len(self._states)
            completed = sum(1 for state in self._states.values() if state.status == "completed")
            failed = sum(1 for state in self._states.values() if state.status == "failed")

            # Calculate average processing time for completed validations
            processing_times = []
            for state in self._states.values():
                if state.completed_at and state.status == "completed":
                    delta = state.completed_at - state.submitted_at
                    processing_times.append(delta.total_seconds())

            avg_time = sum(processing_times) / len(processing_times) if processing_times else 0

            return {
                "total_validations": total,
                "completed_validations": completed,
                "failed_validations": failed,
                "pending_validations": total - completed - failed,
                "average_processing_time": avg_time
            }


# Global state manager instance
_state_manager: Optional[ValidationStateManager] = None


def get_state_manager() -> ValidationStateManager:
    """Get the global validation state manager."""
    global _state_manager
    if _state_manager is None:
        _state_manager = ValidationStateManager()
    return _state_manager


async def startup_state_manager():
    """Initialize state manager cleanup task."""
    manager = get_state_manager()
    await manager.start_cleanup_task()


async def shutdown_state_manager():
    """Cleanup state manager on shutdown."""
    global _state_manager
    if _state_manager:
        await _state_manager.stop_cleanup_task()
        _state_manager = None
