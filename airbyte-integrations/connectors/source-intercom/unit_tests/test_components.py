from unittest.mock import MagicMock, patch

import pytest
import requests
from components import CursorManager, IntercomErrorHandler, CursorManagerAwarePaginationStrategy, CursorAwareSinglePartitionRouter, IntercomScrollRetriever

from airbyte_cdk.sources.streams.http.error_handlers.response_models import  FailureType, ResponseAction




@pytest.mark.parametrize(
    "rate_limit_header, backoff_time",
    [
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 167}, 0.01),
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 100}, 0.01),
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 83}, 1.5),
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 16}, 8.0),
        ({}, 1.0),
    ],
)
def test_rate_limiter(components_module, rate_limit_header, backoff_time):
    IntercomRateLimiter = components_module.IntercomRateLimiter

    def check_backoff_time(t):
        """A replacer for original `IntercomRateLimiter.backoff_time`"""
        assert backoff_time == t, f"Expected {backoff_time}, got {t}"

    class Requester:
        @IntercomRateLimiter.balance_rate_limit()
        def interpret_response_status(self, response: requests.Response):
            """A stub for the decorator function being tested"""

    with patch.object(IntercomRateLimiter, "backoff_time") as backoff_time_mock:
        # Call `check_backoff_time` instead of original `IntercomRateLimiter.backoff_time` method
        backoff_time_mock.side_effect = check_backoff_time

        requester = Requester()

        # Prepare requester object with headers
        response = requests.models.Response()
        response.headers = rate_limit_header

        # Call a decorated method
        requester.interpret_response_status(response)


@pytest.fixture(autouse=True)
def reset_cursor_manager():
    """Reset CursorManager cursor before each test to isolate state"""
    CursorManager().reset()

def test_cursor_manager():
    # Get the singleton instance
    manager = CursorManager()
    
    # Test initial state
    assert manager.get_cursor() is None
    
    # Test updating cursor
    manager.update_cursor("test_cursor")
    assert manager.get_cursor() == "test_cursor"
    
    # Test resetting cursor
    manager.reset()
    assert manager.get_cursor() is None
    
    # Test singleton behavior
    manager2 = CursorManager()
    manager.update_cursor("another_cursor")
    assert manager2.get_cursor() == "another_cursor"

def test_intercom_error_handler():
    handler = IntercomErrorHandler(config={}, parameters={})
    
    # Test HTTP 500 error resets cursor and retries
    response_500 = requests.Response()
    response_500.status_code = 500
    resolution = handler.interpret_response(response_500)
    assert resolution.response_action == ResponseAction.RETRY
    assert resolution.failure_type == FailureType.transient_error
    assert "HTTP 500" in resolution.error_message
    assert CursorManager().get_cursor() is None  # Cursor should be reset
    
    # Test non-500 error uses default behavior
    response_404 = requests.Response()
    response_404.status_code = 404
    resolution = handler.interpret_response(response_404)
    assert resolution.response_action == ResponseAction.FAIL  # Default behavior for 404

def test_cursor_manager_aware_pagination_strategy():
    strategy = CursorManagerAwarePaginationStrategy(
        cursor_value="initial_cursor",
        stop_condition="",
        config={},
        parameters={}
    )
    
    # Mock response
    response = requests.Response()
    response._content = b'{"scroll_param": "next_token"}'
    
    # Test next_page_token updates cursor
    token = strategy.next_page_token(response, 10, None)
    assert token == "initial_cursor"  # Expected to return the cursor_value template result
    assert CursorManager().get_cursor() == "initial_cursor"

def test_cursor_aware_single_partition_router():
    router = CursorAwareSinglePartitionRouter(parameters={})
    
    # Test with no cursor
    slices = list(router.stream_slices())
    assert len(slices) == 1
    assert slices[0].partition == {"scroll_param": None}
    
    # Test with updated cursor
    CursorManager().update_cursor("test_cursor")
    slices = list(router.stream_slices())
    assert len(slices) == 1
    assert slices[0].partition == {"scroll_param": "test_cursor"}

def test_intercom_scroll_retriever():
    # Mock dependencies
    requester = MagicMock()
    paginator = MagicMock()
    record_selector = MagicMock()
    config = {}
    parameters = {}
    
    retriever = IntercomScrollRetriever(
        name="test_stream",
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        config=config,
        parameters=parameters
    )
    
    # Test stream_slicer is correctly initialized
    assert isinstance(retriever.stream_slicer, CursorAwareSinglePartitionRouter)