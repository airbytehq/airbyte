from __future__ import annotations

from source_cloudwatch_logs.source import SourceCloudwatchLogs


def run() -> None:
    SourceCloudwatchLogs.launch()
