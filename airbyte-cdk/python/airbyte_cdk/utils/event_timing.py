#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("airbyte")


class EventTimer:
    """Simple nanosecond resolution event timer for debugging, initially intended to be used to record streams execution
    time for a source.
       Event nesting follows a LIFO pattern, so finish will apply to the last started event.
    """

    def __init__(self, name):
        self.name = name
        self.events = {}
        self.count = 0
        self.stack = []

    def start_event(self, name):
        """
        Start a new event and push it to the stack.
        """
        self.events[name] = Event(name=name)
        self.count += 1
        self.stack.insert(0, self.events[name])

    def finish_event(self):
        """
        Finish the current event and pop it from the stack.
        """

        if self.stack:
            event = self.stack.pop(0)
            event.finish()
        else:
            logger.warning(f"{self.name} finish_event called without start_event")

    def report(self, order_by="name"):
        """
        :param order_by: 'name' or 'duration'
        """
        if order_by == "name":
            events = sorted(self.events.values(), key=lambda event: event.name)
        elif order_by == "duration":
            events = sorted(self.events.values(), key=lambda event: event.duration)
        text = f"{self.name} runtimes:\n"
        text += "\n".join(str(event) for event in events)
        return text


@dataclass
class Event:
    name: str
    start: float = field(default_factory=time.perf_counter_ns)
    end: Optional[float] = field(default=None)

    @property
    def duration(self) -> float:
        """Returns the elapsed time in seconds or positive infinity if event was never finished"""
        if self.end:
            return (self.end - self.start) / 1e9
        return float("+inf")

    def __str__(self):
        return f"{self.name} {datetime.timedelta(seconds=self.duration)}"

    def finish(self):
        self.end = time.perf_counter_ns()


@contextmanager
def create_timer(name):
    """
    Creates a new EventTimer as a context manager to improve code readability.
    """
    a_timer = EventTimer(name)
    yield a_timer
