import logging
from typing import Optional

import ddtrace

logger = logging.getLogger(__name__)


def apply_trace_tags_from_context(
    workspace_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> None:
    """Apply trace tags from context to the current span."""
    if not workspace_id and not project_id:
        return

    # Log the trace IDs for observability
    log_parts = []
    if workspace_id:
        log_parts.append(f"workspace_id={workspace_id}")
    if project_id:
        log_parts.append(f"project_id={project_id}")

    if log_parts:
        logger.info(f"Processing request with trace tags: {', '.join(log_parts)}")

    try:
        span = ddtrace.tracer.current_span()
        if span:
            if workspace_id:
                span.set_tag("workspace_id", workspace_id)
            if project_id:
                span.set_tag("project_id", project_id)
    except Exception:
        # Silently ignore any ddtrace-related errors (e.g. if ddtrace.auto wasn't run)
        pass
