"""Tests for async MCP job management."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from ouroboros.events.base import BaseEvent
from ouroboros.mcp.job_manager import JobLinks, JobManager, JobSnapshot, JobStatus
from ouroboros.mcp.types import ContentType, MCPContentItem, MCPToolResult
from ouroboros.persistence.event_store import EventStore


def _build_store(tmp_path) -> EventStore:
    db_path = tmp_path / "jobs.db"
    return EventStore(f"sqlite+aiosqlite:///{db_path}")


class TestJobManager:
    """Test background job lifecycle behavior."""

    async def test_start_job_completes_and_persists_result(self, tmp_path) -> None:
        store = _build_store(tmp_path)
        manager = JobManager(store)

        async def _runner() -> MCPToolResult:
            await asyncio.sleep(0.05)
            return MCPToolResult(
                content=(MCPContentItem(type=ContentType.TEXT, text="done"),),
                is_error=False,
                meta={"kind": "test"},
            )

        started = await manager.start_job(
            job_type="test",
            initial_message="queued",
            runner=_runner(),
            links=JobLinks(),
        )

        await asyncio.sleep(0.15)
        snapshot = await manager.get_snapshot(started.job_id)

        assert snapshot.status == JobStatus.COMPLETED
        assert snapshot.result_text == "done"
        assert snapshot.result_meta["kind"] == "test"

    async def test_wait_for_change_returns_new_cursor(self, tmp_path) -> None:
        store = _build_store(tmp_path)
        manager = JobManager(store)

        async def _runner() -> MCPToolResult:
            await asyncio.sleep(0.05)
            return MCPToolResult(
                content=(MCPContentItem(type=ContentType.TEXT, text="waited"),),
                is_error=False,
            )

        started = await manager.start_job(
            job_type="wait-test",
            initial_message="queued",
            runner=_runner(),
            links=JobLinks(),
        )

        snapshot, changed = await manager.wait_for_change(
            started.job_id,
            cursor=started.cursor,
            timeout_seconds=2,
        )

        assert changed is True
        assert snapshot.cursor >= started.cursor

    async def test_cancel_job_cancels_non_session_task(self, tmp_path) -> None:
        store = _build_store(tmp_path)
        manager = JobManager(store)

        async def _runner() -> MCPToolResult:
            await asyncio.sleep(10)
            return MCPToolResult(
                content=(MCPContentItem(type=ContentType.TEXT, text="late"),),
                is_error=False,
            )

        started = await manager.start_job(
            job_type="cancel-test",
            initial_message="queued",
            runner=_runner(),
            links=JobLinks(),
        )

        await manager.cancel_job(started.job_id)
        await asyncio.sleep(0.1)
        snapshot = await manager.get_snapshot(started.job_id)

        assert snapshot.status in {JobStatus.CANCEL_REQUESTED, JobStatus.CANCELLED}

    async def test_derive_status_message_includes_latest_subtask_update(self, tmp_path) -> None:
        store = _build_store(tmp_path)
        await store.initialize()
        manager = JobManager(store)

        execution_id = "exec_subtask"
        await store.append(
            BaseEvent(
                type="workflow.progress.updated",
                aggregate_type="execution",
                aggregate_id=execution_id,
                data={
                    "completed_count": 1,
                    "total_count": 3,
                    "current_phase": "Decompose",
                    "activity_detail": "Breaking AC into subtasks",
                },
            )
        )
        await store.append(
            BaseEvent(
                type="execution.subtask.updated",
                aggregate_type="execution",
                aggregate_id=execution_id,
                data={
                    "sub_task_id": "ac_2_sub_1",
                    "content": "Analyze dependency chain",
                    "status": "running",
                },
            )
        )

        snapshot = JobSnapshot(
            job_id="job_derive",
            job_type="derive-test",
            status=JobStatus.RUNNING,
            message="queued",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            links=JobLinks(execution_id=execution_id),
        )
        message = await manager._derive_status_message(snapshot)

        assert message == (
            "Decompose | Breaking AC into subtasks | "
            "Subtask running Analyze dependency chain | 1/3 ACs"
        )

    async def test_derive_status_message_uses_latest_relevant_events_when_buried(self, tmp_path) -> None:
        store = _build_store(tmp_path)
        await store.initialize()
        manager = JobManager(store)

        execution_id = "exec_buried_subtask"
        await store.append(
            BaseEvent(
                type="workflow.progress.updated",
                aggregate_type="execution",
                aggregate_id=execution_id,
                data={
                    "completed_count": 0,
                    "total_count": 2,
                    "current_phase": "Decompose",
                    "activity_detail": "Executing child subtasks",
                },
            )
        )
        await store.append(
            BaseEvent(
                type="execution.subtask.updated",
                aggregate_type="execution",
                aggregate_id=execution_id,
                data={
                    "sub_task_id": "ac_1_sub_2",
                    "content": "Implement parser changes",
                    "status": "executing",
                },
            )
        )
        for index in range(30):
            await store.append(
                BaseEvent(
                    type="execution.agent.thinking",
                    aggregate_type="execution",
                    aggregate_id=execution_id,
                    data={"summary": f"noise-{index}"},
                )
            )

        snapshot = JobSnapshot(
            job_id="job_buried_derive",
            job_type="derive-test",
            status=JobStatus.RUNNING,
            message="queued",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            links=JobLinks(execution_id=execution_id),
        )

        message = await manager._derive_status_message(snapshot)

        assert message == (
            "Decompose | Executing child subtasks | "
            "Subtask executing Implement parser changes | 0/2 ACs"
        )

    async def test_monitor_job_emits_heartbeat_for_unchanged_message(self, tmp_path) -> None:
        store = _build_store(tmp_path)
        manager = JobManager(store)
        manager._monitor_initial_interval_seconds = 0.01
        manager._monitor_max_interval_seconds = 0.02
        manager._monitor_heartbeat_seconds = 0.03

        done = asyncio.Event()

        async def _runner() -> MCPToolResult:
            await done.wait()
            return MCPToolResult(
                content=(MCPContentItem(type=ContentType.TEXT, text="done"),),
                is_error=False,
            )

        started = await manager.start_job(
            job_type="heartbeat-test",
            initial_message="queued",
            runner=_runner(),
            links=JobLinks(execution_id="exec_heartbeat"),
        )

        await store.append(
            BaseEvent(
                type="workflow.progress.updated",
                aggregate_type="execution",
                aggregate_id="exec_heartbeat",
                data={
                    "completed_count": 0,
                    "total_count": 2,
                    "current_phase": "Decompose",
                    "activity_detail": "Waiting on subtask progress",
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )
        )

        await asyncio.sleep(0.12)
        done.set()
        await asyncio.sleep(0.05)

        events = await store.replay("job", started.job_id)
        update_messages = [
            event.data.get("message")
            for event in events
            if event.type == "mcp.job.updated"
            and event.data.get("message") == "Decompose | Waiting on subtask progress | 0/2 ACs"
        ]

        assert len(update_messages) >= 2
