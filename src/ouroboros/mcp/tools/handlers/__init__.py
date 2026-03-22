"""Ouroboros MCP tool handlers.

Re-exports all handler classes, factory functions, and the OUROBOROS_TOOLS tuple.
"""

# --- Handler classes ---
from ouroboros.mcp.tools.handlers.evaluation import (
    EvaluateHandler,
    MeasureDriftHandler,
)
from ouroboros.mcp.tools.handlers.evolution import (
    EvolveRewindHandler,
    EvolveStepHandler,
)
from ouroboros.mcp.tools.handlers.execution import (
    CancelExecutionHandler,
    ExecuteSeedHandler,
)
from ouroboros.mcp.tools.handlers.interview import (
    GenerateSeedHandler,
    InterviewHandler,
)
from ouroboros.mcp.tools.handlers.jobs import (
    CancelJobHandler,
    JobResultHandler,
    JobStatusHandler,
    JobWaitHandler,
    StartEvolveStepHandler,
    StartExecuteSeedHandler,
)
from ouroboros.mcp.tools.handlers.lateral import LateralThinkHandler
from ouroboros.mcp.tools.handlers.status import (
    ACDashboardHandler,
    LineageStatusHandler,
    QueryEventsHandler,
    SessionStatusHandler,
)


# --- Convenience factory functions ---
def execute_seed_handler() -> ExecuteSeedHandler:
    """Create an ExecuteSeedHandler instance."""
    return ExecuteSeedHandler()


def start_execute_seed_handler() -> StartExecuteSeedHandler:
    """Create a StartExecuteSeedHandler instance."""
    return StartExecuteSeedHandler()


def session_status_handler() -> SessionStatusHandler:
    """Create a SessionStatusHandler instance."""
    return SessionStatusHandler()


def job_status_handler() -> JobStatusHandler:
    """Create a JobStatusHandler instance."""
    return JobStatusHandler()


def job_wait_handler() -> JobWaitHandler:
    """Create a JobWaitHandler instance."""
    return JobWaitHandler()


def job_result_handler() -> JobResultHandler:
    """Create a JobResultHandler instance."""
    return JobResultHandler()


def cancel_job_handler() -> CancelJobHandler:
    """Create a CancelJobHandler instance."""
    return CancelJobHandler()


def query_events_handler() -> QueryEventsHandler:
    """Create a QueryEventsHandler instance."""
    return QueryEventsHandler()


def generate_seed_handler() -> GenerateSeedHandler:
    """Create a GenerateSeedHandler instance."""
    return GenerateSeedHandler()


def measure_drift_handler() -> MeasureDriftHandler:
    """Create a MeasureDriftHandler instance."""
    return MeasureDriftHandler()


def interview_handler() -> InterviewHandler:
    """Create an InterviewHandler instance."""
    return InterviewHandler()


def lateral_think_handler() -> LateralThinkHandler:
    """Create a LateralThinkHandler instance."""
    return LateralThinkHandler()


def evaluate_handler() -> EvaluateHandler:
    """Create an EvaluateHandler instance."""
    return EvaluateHandler()


def evolve_step_handler() -> EvolveStepHandler:
    """Create an EvolveStepHandler instance."""
    return EvolveStepHandler()


def start_evolve_step_handler() -> StartEvolveStepHandler:
    """Create a StartEvolveStepHandler instance."""
    return StartEvolveStepHandler()


def lineage_status_handler() -> LineageStatusHandler:
    """Create a LineageStatusHandler instance."""
    return LineageStatusHandler()


def evolve_rewind_handler() -> EvolveRewindHandler:
    """Create an EvolveRewindHandler instance."""
    return EvolveRewindHandler()


# --- OUROBOROS_TOOLS tuple ---
from ouroboros.mcp.tools.qa import QAHandler  # noqa: E402

OUROBOROS_TOOLS: tuple[
    ExecuteSeedHandler
    | StartExecuteSeedHandler
    | SessionStatusHandler
    | JobStatusHandler
    | JobWaitHandler
    | JobResultHandler
    | CancelJobHandler
    | QueryEventsHandler
    | GenerateSeedHandler
    | MeasureDriftHandler
    | InterviewHandler
    | EvaluateHandler
    | LateralThinkHandler
    | EvolveStepHandler
    | StartEvolveStepHandler
    | LineageStatusHandler
    | EvolveRewindHandler
    | CancelExecutionHandler
    | QAHandler,
    ...,
] = (
    ExecuteSeedHandler(),
    StartExecuteSeedHandler(),
    SessionStatusHandler(),
    JobStatusHandler(),
    JobWaitHandler(),
    JobResultHandler(),
    CancelJobHandler(),
    QueryEventsHandler(),
    GenerateSeedHandler(),
    MeasureDriftHandler(),
    InterviewHandler(),
    EvaluateHandler(),
    LateralThinkHandler(),
    EvolveStepHandler(),
    StartEvolveStepHandler(),
    LineageStatusHandler(),
    EvolveRewindHandler(),
    CancelExecutionHandler(),
    QAHandler(),
)

__all__ = [
    # Classes
    "ACDashboardHandler",
    "CancelExecutionHandler",
    "CancelJobHandler",
    "EvaluateHandler",
    "EvolveRewindHandler",
    "EvolveStepHandler",
    "ExecuteSeedHandler",
    "GenerateSeedHandler",
    "InterviewHandler",
    "JobResultHandler",
    "JobStatusHandler",
    "JobWaitHandler",
    "LateralThinkHandler",
    "LineageStatusHandler",
    "MeasureDriftHandler",
    "QueryEventsHandler",
    "SessionStatusHandler",
    "StartEvolveStepHandler",
    "StartExecuteSeedHandler",
    # Factory functions
    "cancel_job_handler",
    "evaluate_handler",
    "evolve_rewind_handler",
    "evolve_step_handler",
    "execute_seed_handler",
    "generate_seed_handler",
    "interview_handler",
    "job_result_handler",
    "job_status_handler",
    "job_wait_handler",
    "lateral_think_handler",
    "lineage_status_handler",
    "measure_drift_handler",
    "query_events_handler",
    "session_status_handler",
    "start_evolve_step_handler",
    "start_execute_seed_handler",
    # Tuple
    "OUROBOROS_TOOLS",
]
