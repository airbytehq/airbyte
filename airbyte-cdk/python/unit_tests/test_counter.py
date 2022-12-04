#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest import mock

from airbyte_cdk.utils.event_timing import create_timer


def test_counter_init():
    with create_timer("Counter") as timer:
        assert timer.name == "Counter"


def test_counter_start_event():
    with create_timer("Counter") as timer:
        with mock.patch("airbyte_cdk.utils.event_timing.EventTimer.start_event") as mock_start_event:
            timer.start_event("test_event")
            mock_start_event.assert_called_with("test_event")


def test_counter_finish_event():
    with create_timer("Counter") as timer:
        with mock.patch("airbyte_cdk.utils.event_timing.EventTimer.finish_event") as mock_finish_event:
            timer.finish_event("test_event")
            mock_finish_event.assert_called_with("test_event")


def test_timer_multiple_events():
    with create_timer("Counter") as timer:
        for i in range(10):
            timer.start_event("test_event")
            timer.finish_event()
        assert timer.count == 10


def test_report_is_ordered_by_name_by_default():
    names = ["j", "b", "g", "d", "e", "f", "c", "h", "i", "a"]

    with create_timer("Source Counter") as timer:
        for name in names:
            timer.start_event(name)
            timer.finish_event()
        report = timer.report().split("\n")[1:]  # ignore the first line
        report_names = [line.split(" ")[0] for line in report]
        assert report_names == sorted(names)


def test_double_finish_is_safely_ignored():
    with create_timer("Source Counter") as timer:
        timer.start_event("test_event")
        timer.finish_event()
        timer.finish_event()
        assert timer.count == 1
