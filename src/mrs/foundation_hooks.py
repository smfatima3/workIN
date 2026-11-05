"""Optional published-defense hooks; empty in the original Qwen cohort."""
from contextvars import ContextVar
ACTIVE_GUARD=ContextVar('foundation_guard',default=None)
