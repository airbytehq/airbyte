# Hermes Agent Guidelines for Airbyte

This folder helps Hermes agents (AI coding assistants) understand and safely contribute to this repository.

## Repository Overview

- **Purpose:** Data integration platform (ELT) for syncing data from sources to destinations
- **Language:** Java, Python, TypeScript
- **Build tool:** gradle, docker
- **Test command:** `gradle test` or Docker-based testing

## What Hermes Should Do

✓ Fix bugs from reported issues labeled `help wanted` or `good-first-issue`  
✓ Add or improve tests for covered code paths  
✓ Improve documentation and error messages  
✓ Refactor code for clarity (small scope)  
✓ Add type hints and improve code consistency  

## What Hermes Should NOT Do

✗ Modify connector implementations without community discussion  
✗ Major architectural changes without consensus  
✗ Add external dependencies  
✗ Modify CI/CD workflows (`.github/workflows/**`)  
✗ Work on issues labeled `blocked-by-upstream` or `needs-discussion`  
✗ Change public APIs or contract behaviors  

## Setup Instructions

```bash
# Install Java 17+ and Docker
java -version
docker --version

# Clone and build
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
gradle build

# For Python components (if needed)
pip install -e .
```

## Verification Commands

Before submitting a PR, Hermes must verify:

```bash
# Format (Gradle spotless)
gradle spotlessApply

# Lint
gradle spotlessCheck

# Tests
gradle test
```

## Key Files to Understand

- `README.md` — project overview and getting started
- `build.gradle` — main build configuration
- `gradle/` — build scripts and plugins
- `airbyte-core/` — core platform code
- `airbyte-connector-*` — connector implementations
- `airbyte-api/` — API definitions
- `tests/` or `src/test/` — test suites

## Issue Labels to Target

Good for Hermes contributions:
- `help wanted` — good for community contributions
- `good-first-issue` — lower barrier to entry
- `bug` — concrete, scoped fixes
- `documentation` — writing improvements

Avoid:
- `blocked-by-upstream` — external blocker
- `needs-discussion` — requires team consensus
- Connector-specific issues (need community discussion)

## Quick Tips

1. Read recent merged PRs to understand patterns
2. Run `gradle test` locally before committing
3. Follow existing code style and patterns
4. Keep PRs focused — one issue per PR
5. Reference the issue number in your commit message
6. For connector changes: involve the community first

---

For more about Hermes Agent, see: https://hermes-agent.nousresearch.com
