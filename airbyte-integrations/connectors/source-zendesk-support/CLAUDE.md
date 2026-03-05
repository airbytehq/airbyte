# source-zendesk-support

## Unique Behaviors
See [BEHAVIOR.md](./BEHAVIOR.md) for documented unique behaviors:
1. Tickets incremental export uses `generated_timestamp` not `updated_at` — API can return tickets with `updated_at` before the requested `start_time`
2. StateDelegatingStream for ticket_metrics — stateless bulk path (no checkpointing, synthetic `_ab_updated_at` cursor) vs stateful per-ticket path (one API call per ticket)
3. Enterprise-only streams disabled at manifest level (CDK lacks ConditionalStreams)
