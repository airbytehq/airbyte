# Agent Memory

This folder contains reference documentation for AI assistants (like Claude Code) working on the Airbyte codebase.

## Purpose

These documents serve as:
1. **Persistent knowledge** for AI assistants across conversation sessions
2. **Reference guides** for implementing common patterns
3. **Team documentation** that both humans and AI can reference

## Documents

### `dataflow_cdk_destination_guide.md`
Comprehensive guide for implementing Airbyte dataflow CDK destinations. Contains:
- Architecture overview and fundamentals
- Required components and interfaces
- The Snowflake approach (recommended pattern)
- Code examples and patterns
- Best practices and common pitfalls
- Implementation checklist

**Use this when:** Implementing new destination connectors using the dataflow CDK

---

## For AI Assistants

When working on destination connectors:
1. Read the relevant guide in this folder
2. Use Snowflake (`/airbyte-integrations/connectors/destination-snowflake/`) as reference
3. Follow the patterns documented here
4. Ask clarifying questions if requirements differ from documented patterns

## For Humans

These documents are also useful for:
- Onboarding new team members
- Understanding architectural patterns
- Ensuring consistency across connectors
- Quick reference when implementing new connectors
