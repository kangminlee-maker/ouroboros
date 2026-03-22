"""Job snapshot rendering helpers.

Shared by all job-related handlers (JobStatusHandler, JobWaitHandler,
CancelJobHandler). The _render_cache dict is module-level mutable state;
because Python caches modules in sys.modules, there is exactly one instance.
"""

from ouroboros.mcp.job_manager import JobSnapshot, JobStatus  # noqa: F401 (JobStatus used by callers)
from ouroboros.orchestrator.session import SessionRepository
from ouroboros.persistence.event_store import EventStore

_render_cache: dict[tuple[str, int], str] = {}
_RENDER_CACHE_MAX = 64


async def _render_job_snapshot(snapshot: JobSnapshot, event_store: EventStore) -> str:
    """Format a user-facing job summary with linked execution context.

    Results are cached by (job_id, cursor) to avoid redundant EventStore queries
    when the same snapshot is rendered repeatedly (e.g. poll loops).
    Terminal snapshots are never cached since they won't change.
    """
    cache_key = (snapshot.job_id, snapshot.cursor)
    if not snapshot.is_terminal and cache_key in _render_cache:
        return _render_cache[cache_key]

    text = await _render_job_snapshot_inner(snapshot, event_store)

    if not snapshot.is_terminal:
        if len(_render_cache) >= _RENDER_CACHE_MAX:
            # Evict oldest entries
            to_remove = list(_render_cache.keys())[: _RENDER_CACHE_MAX // 2]
            for key in to_remove:
                _render_cache.pop(key, None)
        _render_cache[cache_key] = text

    return text


async def _render_job_snapshot_inner(snapshot: JobSnapshot, event_store: EventStore) -> str:
    """Inner render without caching."""
    lines = [
        f"## Job: {snapshot.job_id}",
        "",
        f"**Type**: {snapshot.job_type}",
        f"**Status**: {snapshot.status.value}",
        f"**Message**: {snapshot.message}",
        f"**Created**: {snapshot.created_at.isoformat()}",
        f"**Updated**: {snapshot.updated_at.isoformat()}",
        f"**Cursor**: {snapshot.cursor}",
    ]

    if snapshot.links.execution_id:
        events = await event_store.query_events(
            aggregate_id=snapshot.links.execution_id,
            limit=25,
        )
        workflow_event = next((e for e in events if e.type == "workflow.progress.updated"), None)
        if workflow_event is not None:
            data = workflow_event.data
            lines.extend(
                [
                    "",
                    "### Execution",
                    f"**Execution ID**: {snapshot.links.execution_id}",
                    f"**Phase**: {data.get('current_phase') or 'Working'}",
                    f"**Activity**: {data.get('activity_detail') or data.get('activity') or 'running'}",
                    f"**AC Progress**: {data.get('completed_count', 0)}/{data.get('total_count', '?')}",
                ]
            )

        subtasks: dict[str, tuple[str, str]] = {}
        for event in events:
            if event.type != "execution.subtask.updated":
                continue
            sub_task_id = event.data.get("sub_task_id")
            if sub_task_id and sub_task_id not in subtasks:
                subtasks[sub_task_id] = (
                    event.data.get("content", ""),
                    event.data.get("status", "unknown"),
                )

        if subtasks:
            lines.append("")
            lines.append("### Recent Subtasks")
            for sub_task_id, (content, status) in list(subtasks.items())[:3]:
                lines.append(f"- `{sub_task_id}`: {status} -- {content}")

    elif snapshot.links.session_id:
        repo = SessionRepository(event_store)
        session_result = await repo.reconstruct_session(snapshot.links.session_id)
        if session_result.is_ok:
            tracker = session_result.value
            lines.extend(
                [
                    "",
                    "### Session",
                    f"**Session ID**: {tracker.session_id}",
                    f"**Session Status**: {tracker.status.value}",
                    f"**Messages Processed**: {tracker.messages_processed}",
                ]
            )

    if snapshot.links.lineage_id:
        events = await event_store.query_events(
            aggregate_id=snapshot.links.lineage_id,
            limit=10,
        )
        latest = next((e for e in events if e.type.startswith("lineage.")), None)
        if latest is not None:
            lines.extend(
                [
                    "",
                    "### Lineage",
                    f"**Lineage ID**: {snapshot.links.lineage_id}",
                ]
            )
            if latest.type == "lineage.generation.started":
                lines.append(
                    f"**Current Step**: Gen {latest.data.get('generation_number')} {latest.data.get('phase')}"
                )
            elif latest.type == "lineage.generation.completed":
                lines.append(
                    f"**Current Step**: Gen {latest.data.get('generation_number')} completed"
                )
            elif latest.type == "lineage.generation.failed":
                lines.append(
                    f"**Current Step**: Gen {latest.data.get('generation_number')} failed at {latest.data.get('phase')}"
                )
            elif latest.type in {"lineage.converged", "lineage.stagnated", "lineage.exhausted"}:
                lines.append(f"**Current Step**: {latest.type.split('.', 1)[1]}")
                if latest.data.get("reason"):
                    lines.append(f"**Reason**: {latest.data.get('reason')}")

    if snapshot.result_text and snapshot.is_terminal:
        lines.extend(
            [
                "",
                "### Result",
                "Use `ouroboros_job_result` to fetch the full terminal output.",
            ]
        )

    if snapshot.error:
        lines.extend(["", f"**Error**: {snapshot.error}"])

    return "\n".join(lines)
