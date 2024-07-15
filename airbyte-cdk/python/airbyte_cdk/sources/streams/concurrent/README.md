## Breaking Changes & Limitations

- [bigger scope than Concurrent CDK] checkpointing state was acting on the number of records per slice. This has been changed to consider the number of records per syncs
- `Source.read_state` and `Source._emit_legacy_state_format` are now classmethods to allow for developers to have access to the state before instantiating the source
- send_per_stream_state is always True for Concurrent CDK
- Using stream_state during read_records: The concern is that today, stream_instance.get_updated_state is called on every record and read_records on every slice. The implication is that the argument stream_state passed to read_records will have the value after the last stream_instance.get_updated_state of the previous slice. For Concurrent CDK, this is not possible as slices are processed in an unordered way.
- Cursor fields can only be data-time formatted as epoch. Eventually, we want to move to ISO 8601 as it provides more flexibility but for the first iteration on Stripe, it was easier to use the same format that was already used
