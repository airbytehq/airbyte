# source-zendesk-support

## Unique Behaviors
See [BEHAVIOR.md](./BEHAVIOR.md) for documented unique behaviors:
1. StateDelegatingStream for ticket_metrics (bulk endpoint vs per-ticket incremental)
2. Enterprise-only streams disabled at manifest level (CDK lacks ConditionalStreams)
