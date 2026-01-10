from __future__ import annotations

from source_clouwatch_logs.source import SourceCloudwatchLogs


def run() -> None:
    SourceCloudwatchLogs.launch()
