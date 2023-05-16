from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class AnalyticsMetric:
    """DataClass for conversation metrics model."""
    client_id: str
    unique_id: str
    media_type: str
    metric_name: str
    interval_start: datetime
    interval_end: datetime
    max: int
    min: int
    count: int
    sum: int

    # Call to return as dict
    dict = asdict
