# CLAUDE.md - Airbyte Repository Guide

## Project Overview

Airbyte is an open-source data integration platform. This monorepo contains the Connector Development Kit (CDK), 150+ connectors (sources and destinations), CI/CD tooling, and documentation.

## Repository Structure

```
airbyte-cdk/           # Core Development Kit (Java CDK, Python CDK, Bulk CDK)
airbyte-integrations/  # Connector implementations (sources & destinations)
airbyte-ci/            # CI/CD systems, Dagger-based pipelines, automation tools
buildSrc/              # Gradle build conventions and plugins
connector-writer/      # Connector scaffolding/template tools
docker-images/         # Docker configuration for connectors
docusaurus/            # Documentation website (Docusaurus, pnpm)
docs/                  # Platform documentation source
poe-tasks/             # Poethepoet task definitions
tools/                 # Development utilities and helpers
```

## Languages & Tech Stack

- **Java 21** / **Kotlin 1.9**: CDK core, Java-based connectors
- **Python 3.10+**: Python connectors, airbyte-ci tooling
- **TypeScript**: Documentation site (Docusaurus)
- **Groovy**: Gradle build scripts

## Build System

### Gradle (Java/Kotlin)

```bash
./gradlew build                          # Build all
./gradlew test                           # Run all tests
./gradlew :module:test                   # Test specific module
./gradlew spotbugsMain                   # Static analysis
```

- JVM settings: 8GB max heap, 4m stack (`gradle.properties`)
- Parallel builds enabled by default
- S3 build cache in CI, local caching for dev

### Poetry (Python connectors)

```bash
cd airbyte-integrations/connectors/<connector-name>
poetry install                           # Install deps
```

### Poethepoet (task runner)

```bash
poe connector <name> <task>              # Run task on a connector
poe source <shortname> <task>            # Shortcut for sources
poe destination <shortname> <task>       # Shortcut for destinations
poe docs-build                           # Build documentation site
poe get-modified-connectors              # List changed connectors
```

Connector-level poe tasks (run from connector directory):
```bash
poe test-all                             # All tests
poe test-unit-tests                      # Unit tests only (unit_tests/)
poe test-integration-tests               # Integration tests (integration_tests/)
poe pytest-fast                          # Fast tests (excludes @slow)
poe check-all                            # All checks
```

## Testing

### Java/Kotlin (JUnit 5)

- Framework: JUnit 5 with AssertJ assertions, Mockito mocking
- Parallel execution at class level, 1-minute default timeout
- Timezone forced to UTC in tests

### Python (pytest)

- Verbose output, log level INFO (`pytest.ini`)
- Coverage via `pytest --cov`

## Code Style & Linting

### Java/Kotlin

- **Spotless**: Google Style Guide formatting via Maven
  - Run: `mvn -f spotless-maven-pom.xml spotless:apply`
- **SpotBugs**: Static analysis (MAX effort, HIGH confidence)
- Kotlin: 4-space indent, 100 char max line length

### Python

- **Ruff**: Formatter + linter
  - Line length: 140 chars, double quotes, target Python 3.10+
  - Linting: currently only isort (`I`) rules enabled
  - Run: `ruff format .` and `ruff check . --fix`
- 4-space indent (`ruff.toml`, `.editorconfig`)

### Pre-commit Hooks

Hooks run on pre-push (not pre-commit):
1. **ruff** - Python linting and formatting
2. **prettier** - JSON/YAML formatting
3. **addlicense** - Apache 2.0 license headers on `.java`, `.kt`, `.py` files
4. **spotless** - Java/Kotlin formatting

Setup: `make tools.install` (installs airbyte-ci + pre-commit)

## Connector Development

Each connector lives in `airbyte-integrations/connectors/<connector-name>/` and has:
- `metadata.yaml` - Connector metadata (name, version, support level, Docker config)
- `build.gradle` (Java) or `pyproject.toml` (Python) - Build configuration
- Java connectors are included in Gradle monorepo; Python connectors use Poetry

Connectors marked as `archived` in metadata are excluded from builds.

## CI/CD

- 45+ GitHub Actions workflows in `.github/workflows/`
- Key workflows: `connector-ci-checks.yml`, `publish_connectors.yml`, `java-cdk-tests.yml`
- Runners: `ubuntu-24.04` default, `linux-24.04-large` for heavy tasks
- Gradle Enterprise build scans enabled when `CI=true`

## Key Commands Quick Reference

```bash
# Setup
make tools.install                       # Install airbyte-ci + pre-commit

# Build
./gradlew build                          # Full Gradle build
./gradlew :airbyte-cdk:java:airbyte-cdk:test  # Test Java CDK

# Python connector workflow
cd airbyte-integrations/connectors/<name>
poetry install
poe test-unit-tests
poe check-all

# From repo root
poe connector source-postgres check-all
poe source postgres test-all

# Formatting
ruff format .                            # Python
ruff check . --fix                       # Python lint fix
mvn -f spotless-maven-pom.xml spotless:apply  # Java/Kotlin

# Pre-commit
pre-commit run --all-files               # Run all hooks
```

## Important Notes

- Version: 0.64.7 (see `gradle.properties`, `.bumpversion.cfg`)
- Java 21 required for builds
- Docker is needed for connector image building and integration tests
- The `settings.gradle` dynamically discovers connectors - only those with `build.gradle` and non-archived `metadata.yaml` are included
- Repository mode is `FAIL_ON_PROJECT_REPOS` to prevent accidental repo additions in subprojects
