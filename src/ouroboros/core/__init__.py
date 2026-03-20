"""Ouroboros core module - shared types, errors, and protocols.

Note: context.py (WorkflowContext, compress_context, etc.) is intentionally
NOT re-exported here. It depends on providers/ (LiteLLMAdapter) which violates
the core layer's position as the lowest dependency layer. Import directly from
ouroboros.core.context when needed.
"""

from ouroboros.core.errors import (
    ConfigError,
    OuroborosError,
    PersistenceError,
    ProviderError,
    ValidationError,
)
from ouroboros.core.git_workflow import (
    GitWorkflowConfig,
    detect_git_workflow,
    is_on_protected_branch,
)
from ouroboros.core.security import (
    InputValidator,
    mask_api_key,
    sanitize_for_logging,
    validate_api_key_format,
)
from ouroboros.core.seed import (
    EvaluationPrinciple,
    ExitCondition,
    OntologyField,
    OntologySchema,
    Seed,
    SeedMetadata,
)
from ouroboros.core.types import CostUnits, DriftScore, EventPayload, Result

__all__ = [
    # Types
    "Result",
    "EventPayload",
    "CostUnits",
    "DriftScore",
    # Errors
    "OuroborosError",
    "ProviderError",
    "ConfigError",
    "PersistenceError",
    "ValidationError",
    # Seed (Immutable Specification)
    "Seed",
    "SeedMetadata",
    "OntologySchema",
    "OntologyField",
    "EvaluationPrinciple",
    "ExitCondition",
    # Git Workflow
    "GitWorkflowConfig",
    "detect_git_workflow",
    "is_on_protected_branch",
    # Security utilities
    "InputValidator",
    "mask_api_key",
    "validate_api_key_format",
    "sanitize_for_logging",
]
