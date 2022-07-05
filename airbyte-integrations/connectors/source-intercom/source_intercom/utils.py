#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from functools import wraps
from typing import Dict


class EagerlyCachedStreamState:
    """
    This is the placeholder for the tmp stream state for each incremental stream,
    It's empty, once the sync has started and is being updated while sync operation takes place,
    It holds the `temporary stream state values` before they are updated to have the opportunity to reuse this state.
    """

    cached_state: Dict = {}

    @staticmethod
    def stream_state_to_tmp(*args, state_object: Dict = cached_state, **kwargs) -> Dict:
        """
        Method to save the current stream state for future re-use within slicing.
        The method requires having the temporary `state_object` as placeholder.
        Because of the specific of Intercom entities relations, we have the opportunity to fetch the updates,
        for particular stream using the `Incremental Refresh`, inside slicing.
        For example:
            if `Conversation Parts` stream records were updated, then the `Conversations` is updated as well
        """
        # Map the input *args, the sequece should be always keeped up to the input function
        # change the mapping if needed
        stream: object = args[0]  # the self instance of the stream
        current_stream_state: Dict = kwargs["stream_state"] or {}
        # get the current tmp_state_value
        tmp_stream_state_value = state_object.get(stream.name, {}).get(stream.cursor_field, "")
        # Save the curent stream value for current sync, if present.
        if current_stream_state:
            state_object[stream.name] = {stream.cursor_field: current_stream_state.get(stream.cursor_field, "")}
            # Check if we have the saved state and keep the minimun value
            if tmp_stream_state_value:
                state_object[stream.name] = {
                    stream.cursor_field: min(current_stream_state.get(stream.cursor_field, ""), tmp_stream_state_value)
                }

        return state_object

    def cache_stream_state(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            EagerlyCachedStreamState.stream_state_to_tmp(*args, **kwargs)
            return func(*args, **kwargs)

        return decorator
