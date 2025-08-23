#!/usr/bin/env python3
"""
MetaOps Validator - SLA Tracking and Performance Monitoring
Performance monitoring with business metrics
"""
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import logging
from pathlib import Path

@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    timestamp: datetime
    operation_type: str  # realtime_validation|batch_processing|retailer_submission
    duration_ms: int
    success: bool
    tenant_id: str
    additional_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SLATarget:
    """Service Level Agreement target definition"""
    metric_name: str
    target_value: float
    unit: str  # ms|hours|percent
    measurement_window: str  # 1h|24h|7d|30d
    threshold_type: str  # max|min|average

class PerformanceBuffer:
    """Ring buffer for storing recent performance metrics"""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.metrics: deque = deque(maxlen=max_size)
        self.operation_counters = defaultdict(int)
        self.success_counters = defaultdict(int)

    def add_metric(self, metric: PerformanceMetric):
        """Add performance metric to buffer"""
        self.metrics.append(metric)
        self.operation_counters[metric.operation_type] += 1
        if metric.success:
            self.success_counters[metric.operation_type] += 1

    def get_metrics_since(self, since: datetime, operation_type: Optional[str] = None) -> List[PerformanceMetric]:
        """Get metrics since specific timestamp"""
        filtered = [m for m in self.metrics if m.timestamp >= since]
        if operation_type:
            filtered = [m for m in filtered if m.operation_type == operation_type]
        return filtered

    def get_percentile(self, percentile: float, operation_type: str, since: datetime) -> Optional[float]:
        """Calculate percentile for operation duration"""
        metrics = self.get_metrics_since(since, operation_type)
        if not metrics:
            return None

        durations = sorted([m.duration_ms for m in metrics])
        index = int((percentile / 100) * len(durations))
        return durations[min(index, len(durations) - 1)]

    def get_success_rate(self, operation_type: str, since: datetime) -> float:
        """Calculate success rate for operation type"""
        metrics = self.get_metrics_since(since, operation_type)
        if not metrics:
            return 0.0

        successful = len([m for m in metrics if m.success])
        return (successful / len(metrics)) * 100

class SLATracker:
    """Service Level Agreement tracking and reporting"""

    def __init__(self):
        self.performance_buffer = PerformanceBuffer()
        self.sla_targets = self._initialize_sla_targets()
        self.cost_tracker = CostTracker()
        self.alert_thresholds = {
            "realtime_sla_breach": 30000,  # 30s SLA
            "batch_delay_hours": 4,        # 4h batch SLA
            "success_rate_threshold": 95.0  # 95% success rate
        }

    def _initialize_sla_targets(self) -> Dict[str, SLATarget]:
        """Initialize standard SLA targets"""
        return {
            "realtime_p99": SLATarget(
                metric_name="realtime_validation_p99",
                target_value=30000,
                unit="ms",
                measurement_window="1h",
                threshold_type="max"
            ),
            "realtime_success_rate": SLATarget(
                metric_name="realtime_validation_success",
                target_value=99.0,
                unit="percent",
                measurement_window="24h",
                threshold_type="min"
            ),
            "batch_completion": SLATarget(
                metric_name="batch_processing_completion",
                target_value=4.0,
                unit="hours",
                measurement_window="24h",
                threshold_type="max"
            )
        }

    async def record_operation(self,
                             operation_type: str,
                             start_time: float,
                             success: bool,
                             tenant_id: str,
                             additional_data: Optional[Dict] = None) -> PerformanceMetric:
        """Record completed operation performance"""
        end_time = time.time()
        duration_ms = int((end_time - start_time) * 1000)

        metric = PerformanceMetric(
            timestamp=datetime.now(),
            operation_type=operation_type,
            duration_ms=duration_ms,
            success=success,
            tenant_id=tenant_id,
            additional_data=additional_data or {}
        )

        self.performance_buffer.add_metric(metric)

        # Check for SLA breaches
        await self._check_sla_breach(metric)

        return metric

    async def _check_sla_breach(self, metric: PerformanceMetric):
        """Check if metric indicates SLA breach and alert if needed"""
        if metric.operation_type == "realtime_validation":
            if metric.duration_ms > self.alert_thresholds["realtime_sla_breach"]:
                await self._trigger_alert(
                    alert_type="sla_breach",
                    message=f"Realtime validation exceeded 30s SLA: {metric.duration_ms}ms",
                    severity="high",
                    metric=metric
                )

        # Check success rate trends
        if not metric.success:
            recent_success_rate = self.performance_buffer.get_success_rate(
                metric.operation_type,
                datetime.now() - timedelta(hours=1)
            )
            if recent_success_rate < self.alert_thresholds["success_rate_threshold"]:
                await self._trigger_alert(
                    alert_type="success_rate_decline",
                    message=f"{metric.operation_type} success rate dropped to {recent_success_rate:.1f}%",
                    severity="medium",
                    metric=metric
                )

    async def _trigger_alert(self, alert_type: str, message: str, severity: str, metric: PerformanceMetric):
        """Trigger performance alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "tenant_id": metric.tenant_id,
            "operation_type": metric.operation_type,
            "metric_details": {
                "duration_ms": metric.duration_ms,
                "success": metric.success
            }
        }

        # Log alert (in production, would send to alerting system)
        logging.warning(f"SLA Alert: {json.dumps(alert, indent=2)}")

    def get_sla_dashboard(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate SLA compliance dashboard"""
        now = datetime.now()

        # Calculate metrics for different time windows
        metrics_1h = self.performance_buffer.get_metrics_since(now - timedelta(hours=1))
        metrics_24h = self.performance_buffer.get_metrics_since(now - timedelta(hours=24))

        if tenant_id:
            metrics_1h = [m for m in metrics_1h if m.tenant_id == tenant_id]
            metrics_24h = [m for m in metrics_24h if m.tenant_id == tenant_id]

        # Realtime validation metrics
        realtime_metrics = {
            "target_ms": 30000,
            "p50_ms": self.performance_buffer.get_percentile(50, "realtime_validation", now - timedelta(hours=1)) or 0,
            "p95_ms": self.performance_buffer.get_percentile(95, "realtime_validation", now - timedelta(hours=1)) or 0,
            "p99_ms": self.performance_buffer.get_percentile(99, "realtime_validation", now - timedelta(hours=1)) or 0,
            "success_rate_percent": self.performance_buffer.get_success_rate("realtime_validation", now - timedelta(hours=24)),
            "total_requests": len([m for m in metrics_24h if m.operation_type == "realtime_validation"])
        }

        # Calculate SLA compliance
        realtime_sla_compliance = (realtime_metrics["p99_ms"] <= 30000) if realtime_metrics["p99_ms"] > 0 else True
        success_rate_compliance = realtime_metrics["success_rate_percent"] >= 99.0

        # Batch processing metrics
        batch_metrics = self._calculate_batch_metrics(metrics_24h)

        # Cost validation
        cost_metrics = self.cost_tracker.get_cost_summary(now - timedelta(days=30), tenant_id)

        return {
            "timestamp": now.isoformat(),
            "tenant_id": tenant_id,
            "sla_metrics": {
                "realtime_validation": {
                    **realtime_metrics,
                    "sla_compliance": realtime_sla_compliance and success_rate_compliance
                },
                "batch_processing": batch_metrics
            },
            "cost_validation": cost_metrics,
            "alerts": self._get_recent_alerts(now - timedelta(hours=24))
        }

    def _calculate_batch_metrics(self, metrics_24h: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calculate batch processing performance metrics"""
        batch_metrics = [m for m in metrics_24h if m.operation_type == "batch_processing"]

        if not batch_metrics:
            return {
                "target_completion_hours": 4,
                "average_completion_hours": 0,
                "sla_compliance_percent": 100.0,
                "total_batches": 0
            }

        # Calculate average completion time
        avg_duration_ms = sum(m.duration_ms for m in batch_metrics) / len(batch_metrics)
        avg_completion_hours = avg_duration_ms / (1000 * 60 * 60)  # Convert to hours

        # SLA compliance (batches completing within 4 hours)
        compliant_batches = len([m for m in batch_metrics if m.duration_ms <= (4 * 60 * 60 * 1000)])
        compliance_percent = (compliant_batches / len(batch_metrics)) * 100

        return {
            "target_completion_hours": 4,
            "average_completion_hours": round(avg_completion_hours, 2),
            "sla_compliance_percent": round(compliance_percent, 1),
            "total_batches": len(batch_metrics)
        }

    def _get_recent_alerts(self, since: datetime) -> List[Dict]:
        """Get alerts generated since timestamp"""
        # In production, this would query an alerting database
        # For now, return empty list as alerts are logged
        return []

class CostTracker:
    """Business cost tracking and ROI calculation"""

    def __init__(self):
        self.cost_per_operation = {
            "realtime_validation": 0.05,    # $0.05 per validation
            "batch_processing": 0.12,       # $0.12 per file in batch
            "retailer_submission": 0.08     # $0.08 per submission
        }
        self.prevention_value = {
            "retailer_rejection_cost": 240.0,  # $240 per rejected submission
            "manual_qa_cost": 45.0,            # $45 per manual QA hour
            "rework_cost": 120.0               # $120 per rework cycle
        }

    def get_cost_summary(self, since: datetime, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate cost and savings summary"""
        # This would normally query actual usage data
        # For demo, provide realistic estimates

        mock_usage = {
            "realtime_validations": 1250,
            "batch_files_processed": 850,
            "retailer_submissions": 425,
            "prevented_rejections": 47,
            "manual_qa_hours_saved": 180,
            "rework_cycles_avoided": 23
        }

        # Calculate processing costs
        processing_costs = (
            mock_usage["realtime_validations"] * self.cost_per_operation["realtime_validation"] +
            mock_usage["batch_files_processed"] * self.cost_per_operation["batch_processing"] +
            mock_usage["retailer_submissions"] * self.cost_per_operation["retailer_submission"]
        )

        # Calculate prevented costs (value delivered)
        prevented_costs = (
            mock_usage["prevented_rejections"] * self.prevention_value["retailer_rejection_cost"] +
            mock_usage["manual_qa_hours_saved"] * self.prevention_value["manual_qa_cost"] +
            mock_usage["rework_cycles_avoided"] * self.prevention_value["rework_cost"]
        )

        roi = ((prevented_costs - processing_costs) / processing_costs) * 100 if processing_costs > 0 else 0

        return {
            "processing_costs": round(processing_costs, 2),
            "prevented_costs": round(prevented_costs, 2),
            "net_savings": round(prevented_costs - processing_costs, 2),
            "roi_percent": round(roi, 1),
            "usage_summary": mock_usage,
            "cost_per_file_average": round(processing_costs / (mock_usage["realtime_validations"] + mock_usage["batch_files_processed"]), 3)
        }

class PerformanceOptimizer:
    """Automatic performance optimization based on SLA tracking"""

    def __init__(self, sla_tracker: SLATracker):
        self.sla_tracker = sla_tracker
        self.optimization_rules = {
            "cache_threshold_ms": 5000,      # Cache results for requests >5s
            "parallel_threshold": 10,        # Use parallel processing for >10 files
            "priority_threshold_ms": 25000   # Prioritize requests approaching SLA limit
        }

    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance patterns and suggest optimizations"""
        now = datetime.now()
        recent_metrics = self.sla_tracker.performance_buffer.get_metrics_since(
            now - timedelta(hours=1), "realtime_validation"
        )

        if not recent_metrics:
            return {"recommendations": [], "analysis": "Insufficient data"}

        recommendations = []

        # Analyze slow requests
        slow_requests = [m for m in recent_metrics if m.duration_ms > self.optimization_rules["cache_threshold_ms"]]
        if slow_requests:
            recommendations.append({
                "type": "caching",
                "priority": "high",
                "description": f"Enable caching for {len(slow_requests)} slow requests (>{self.optimization_rules['cache_threshold_ms']}ms)",
                "potential_improvement": "30-50% reduction in response time"
            })

        # Check for SLA approaching requests
        approaching_sla = [m for m in recent_metrics if m.duration_ms > self.optimization_rules["priority_threshold_ms"]]
        if approaching_sla:
            recommendations.append({
                "type": "priority_queue",
                "priority": "medium",
                "description": f"{len(approaching_sla)} requests approaching SLA limit",
                "potential_improvement": "Prevent SLA breaches through request prioritization"
            })

        # Resource utilization analysis
        avg_duration = sum(m.duration_ms for m in recent_metrics) / len(recent_metrics)
        if avg_duration > 15000:  # Average >15s suggests resource constraints
            recommendations.append({
                "type": "scaling",
                "priority": "high",
                "description": f"Average response time {avg_duration:.0f}ms suggests resource constraints",
                "potential_improvement": "Consider horizontal scaling or resource optimization"
            })

        return {
            "analysis_period": "Last 1 hour",
            "total_requests": len(recent_metrics),
            "average_duration_ms": round(avg_duration, 0),
            "recommendations": recommendations,
            "optimization_score": self._calculate_optimization_score(recent_metrics)
        }

    def _calculate_optimization_score(self, metrics: List[PerformanceMetric]) -> int:
        """Calculate performance optimization score (0-100)"""
        if not metrics:
            return 100

        # Factors: SLA compliance, success rate, consistency
        sla_compliance = len([m for m in metrics if m.duration_ms <= 30000]) / len(metrics)
        success_rate = len([m for m in metrics if m.success]) / len(metrics)

        # Consistency (lower variance is better)
        durations = [m.duration_ms for m in metrics]
        avg_duration = sum(durations) / len(durations)
        variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
        consistency_score = max(0, 1 - (variance / (avg_duration ** 2)))

        overall_score = (sla_compliance * 0.4 + success_rate * 0.4 + consistency_score * 0.2) * 100
        return int(overall_score)

# Global SLA tracker instance
sla_tracker = SLATracker()
performance_optimizer = PerformanceOptimizer(sla_tracker)
