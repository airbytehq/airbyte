# Knowledge Base: airbytehq/airbyte

Generated: 2026-09-22

## Project Summary

Airbyte is an open-source data movement platform for ELT pipelines and AI agents, enabling data transfer from 600+ APIs, databases, and files to warehouses, lakes, and AI applications. Used by data engineers to centralize data and by developers to give AI agents real-time access to business data. Solves the long-tail connector problem through an extensible CDK framework that supports both no-code/low-code connector building and custom development.

## Architecture

**Multi-language monorepo** organized by concern:

- **airbyte-cdk/** — Connector Development Kits in Java/Kotlin and Python, providing base classes and utilities for building connectors
  - `java/airbyte-cdk/` — Java/Kotlin CDK modules
  - `python/` — Python CDK package
  - `bulk/` — Bulk data processing CDK (core + toolkits)
- **airbyte-integrations/** — 600+ source and destination connectors
  - `connectors/` — Individual connector implementations (source-*, destination-*)
  - `bases/` — Shared base images and connector templates
- **buildSrc/** — Custom Gradle plugins and build logic
- **airbyte-ci/** — CI/CD tooling for connector testing and publishing
- **docs/** — Documentation markdown files
- **docusaurus/** — Documentation website builder
- **tools/** — Utility scripts and schema generators

Connectors extend CDK base classes (e.g., `HttpStream`, `AbstractSource` in Python; similar abstractions in Java), implementing stream-specific logic. Each connector is independently versioned with its own `metadata.yaml`, `build.gradle` or `pyproject.toml`, and test suite.

## Key Files & Classes

**Core:**
- `build.gradle` — Root Gradle build configuration with Java 21, Kotlin 1.9, spotbugs, test parallelization
- `settings.gradle` — Multi-repo dependency resolution, CDK/connector project inclusion, S3 build cache
- `ruff.toml` — Python linting/formatting config (isort, pyflakes, line length 140)
- `pytest.ini` — pytest configuration for all Python projects
- `.pre-commit-config.yaml` — Pre-commit hooks: ruff, prettier, license headers, spotless for Java

**CDK:**
- `airbyte-cdk/python/airbyte_cdk/sources/streams/http.py` — `HttpStream` base class for API connectors
- `airbyte-cdk/python/airbyte_cdk/sources/__init__.py` — `AbstractSource` base class
- `airbyte-cdk/python/airbyte_cdk/sources/file_based/config/abstract_file_based_spec.py` — `AbstractFileBasedSpec` base class for file-based connectors (S3, GCS, Azure, local files)
- `airbyte-cdk/java/airbyte-cdk/` — Java CDK modules (multiple sub-projects)

**Connectors (examples):**
- `airbyte-integrations/connectors/source-appsflyer/source_appsflyer/source.py` — Python HTTP source implementation
- `airbyte-integrations/connectors/source-db2/src/main/java/` — Java JDBC source implementation
- `airbyte-integrations/connectors/source-s3/source_s3/v4/config.py` — File-based connector config using `AbstractFileBasedSpec`
- `airbyte-integrations/connectors/source-s3/source_s3/v4/legacy_config_transformer.py` — v3→v4 config migration transformer
- `airbyte-integrations/connectors/source-s3/source_s3/v4/stream_reader.py` — File-based connector stream reader
- `airbyte-integrations/connectors/*/metadata.yaml` — Connector version, support level, documentation links

**Config:**
- `buildSrc/src/` — Custom Gradle plugins (`airbyte-java-connector`, `airbyte-connector-docker-convention`)
- `spotless-maven-pom.xml` — Java/Kotlin formatting via Maven Spotless
- `poetry.lock`, `poe_tasks.toml` — Python dependency management and task runner

**Utils:**
- `Makefile` — Git hooks, pre-commit installation, version checks
- `tools/schema_generator/` — Schema generation utilities

## Code Patterns

**Python:**
- **Naming:** `snake_case` for files, variables, functions; `PascalCase` for classes
- **Imports:** Grouped by stdlib → third-party → first-party (airbyte_cdk, airbyte_protocol), enforced by ruff isort
- **Base classes:** Extend `HttpStream` for API sources, `AbstractSource` for connector entry points, `AbstractFileBasedSpec` for file-based connectors
- **Error handling:** Return error messages via Airbyte protocol, not exceptions to stdout
- **Type hints:** Encouraged but not strictly enforced (ruff allows some untyped code)
- **Docstrings:** Google style (configured in ruff), but many connectors lack comprehensive docs
- **Quote style:** Double quotes (ruff enforced)
- **Line length:** 140 characters

**File-based connectors (S3, GCS, Azure, local files):**
- **Config structure:** Extend `AbstractFileBasedSpec` with connector-specific fields (bucket, credentials, etc.)
- **Stream config:** Define custom stream config by extending `FileBasedStreamConfig` for connector-specific options
- **Parser options:** File format configs (CSV, Parquet, Avro, JSONL) with format-specific options (delimiters, quote chars, null values)
- **CSV parsing:** Uses Python's `csv.DictReader` (not PyArrow) — important for options like `newlines_in_values`
- **Versioned migrations:** When major changes occur (v3→v4), use `legacy_config_transformer.py` pattern to migrate old configs
- **Migration contract:** Config.py must document: "When this Spec is changed, legacy_config_transformer.py must also be modified"
- **Globs:** File matching patterns support multiple globs separated by `|` in legacy configs, converted to list in v4

**Java/Kotlin:**
- **Naming:** `camelCase` for variables/methods, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants
- **Indentation:** 4 spaces (Kotlin), tabs/spaces per `.editorconfig`
- **Conventions:** Kotlin official code style, trailing commas allowed
- **Base classes:** Extend CDK abstractions (source/destination interfaces)
- **Testing:** JUnit 5, Mockito, AssertJ; test fixtures for shared test utilities
- **Annotations:** Spotbugs annotations for null safety

**Both:**
- Each connector has `metadata.yaml` with version, supportLevel (community/certified/archived), dockerImageTag
- Integration tests in `integration_tests/` directory
- Unit tests in `unit_tests/` (Python) or `src/test/` (Java)

## Development Setup

**Prerequisites:**
- Java 21 (for Gradle builds)
- Python 3.10+ (for Python connectors and CDK)
- Poetry (Python dependency management)
- Docker (for connector testing)
- Maven (for Spotless formatting)
- Pre-commit (optional, for git hooks)

**Initial setup:**
```bash
# Install pre-commit hooks (optional)
make tools.git-hooks.install

# For Python connector development
cd airbyte-integrations/connectors/source-<name>
poetry install

# For Java connector development
./gradlew :airbyte-integrations:connectors:source-<name>:build
```

**Common commands:**
- `./gradlew build` — Build all Java projects
- `poetry install` — Install Python dependencies (per connector)
- `poe` — List available poetry tasks (defined in `poe_tasks.toml`)

## Testing

**Framework:** JUnit 5 (Java), pytest (Python)

**Test structure:**
- Java: `src/test/java/` and `src/testFixtures/java/` for shared test utilities
- Python: `unit_tests/` for unit tests, `integration_tests/` for integration tests
- Each connector has `acceptance-test-config.yml` for acceptance test suite

**Running tests:**
```bash
# Java (all projects)
./gradlew test

# Java (specific connector)
./gradlew :airbyte-integrations:connectors:source-db2:test

# Python (specific connector)
cd airbyte-integrations/connectors/source-appsflyer
poetry run pytest unit_tests/
```

**Test configuration:**
- Parallel execution enabled by default in JUnit (class-level concurrency)
- pytest runs with `-vv --capture=no --log-level=INFO --color=yes`
- Test timeout: 1 minute default (configurable via `JunitMethodExecutionTimeout`)
- Java: Max heap 3G (parallel workers) or 8G (single JVM with concurrency)

**Test patterns:**
- Mockito for mocking (Java)
- requests-mock, pytest-mock for Python
- TestContainers for database integration tests (Java)

## Build & CI

**Build system:** Gradle 8.x with custom plugins, Poetry for Python

**Key tools:**
- **Spotbugs** — Static analysis for Java (effort: MAX, confidence: HIGH)
- **Ruff** — Python linting and formatting (replaces black, isort, flake8)
- **Prettier** — JSON/YAML formatting
- **Spotless** — Java/Kotlin auto-formatting via Maven
- **Pre-commit hooks** — Runs ruff, prettier, license headers, spotless

**CI workflows (.github/workflows/):**
- `connector-image-build.yml` — Build connector Docker images
- `publish_connectors.yml` — Publish connectors to registry
- `format_check.yml` — Enforce code formatting
- Various `*-command.yml` — Slash commands for PR automation (e.g., `/publish-connectors`)
- Gradle build cache backed by S3 in CI (`ab-ci-cache` bucket, us-west-2)

**Build features:**
- Reproducible archives (stable timestamps/order)
- Build scans via Develocity
- Parallel test execution
- Incremental builds with up-to-date checks

## Contribution Guidelines

**Location:** Full guidelines at [docs.airbyte.io/contributing-to-airbyte](https://docs.airbyte.io/contributing-to-airbyte)

**Key requirements:**
- **PR permissions:** Must enable "Allow edits from maintainers" checkbox; PR must come from personal fork (not organization fork)
- **Code of Conduct:** See `CODE_OF_CONDUCT.md`
- **First contributions:** Look for [good first issues](https://github.com/airbytehq/airbyte/labels/contributor-program) label
- **Pre-push hooks:** Automatically run formatting/linting before push
- **Commit messages:** No specific format enforced in CONTRIBUTING.md (inferred from git log)
- **Security:** Report vulnerabilities to `security@airbyte.io`, not public issues

**Process:**
1. Fork from personal account
2. Enable maintainer edits on PR
3. Ensure pre-commit hooks pass (formatting, licenses)
4. Maintainers may apply formatting/dependency updates directly
5. Community PRs welcome; Airbyte maintains final approval

## Common Pitfalls

1. **Organization forks block maintainer edits** — GitHub security model prevents "Allow edits from maintainers" on org forks; must use personal fork

2. **Archived connectors excluded from build** — `settings.gradle` filters connectors with `supportLevel: archived` in metadata.yaml; changes to archived connectors won't build

3. **Python/Java connector split** — `settings.gradle` only includes Java connectors (those with `build.gradle`); Python connectors managed separately via Poetry

4. **CDK version pinning** — Each connector specifies `cdkVersionRequired` in build.gradle or `airbyte-cdk` version in pyproject.toml; upgrading CDK requires connector updates

5. **Test parallelism configuration** — Default runs tests across multiple JVM workers (fast but high memory); setting `-PtestExecutionConcurrency=N` switches to single JVM with JUnit concurrency

6. **Pre-commit hook scope** — Only runs on pre-push (not pre-commit); formatters auto-fix but license headers require manual intervention

7. **Multiple repository sources** — Airbyte-controlled repos checked first (slow), whitelisted by group; unexpected dependency resolution if artifact exists in multiple repos

8. **Docker context required** — Connectors run in Docker; local Java/Python runs don't match production behavior without containerization

9. **Metadata.yaml controls inclusion** — Missing or malformed metadata.yaml causes connector to be silently excluded from Gradle build

10. **S3 build cache in CI only** — Local builds don't push to S3 cache; CI requires `S3_BUILD_CACHE_ACCESS_KEY_ID` env var

11. **Silent config field dropping during version migrations** — When migrating connector configs between major versions (e.g., v3→v4), config fields can be silently dropped if not explicitly mapped in `legacy_config_transformer.py`. Pattern to avoid this:
    - **Root cause:** New connector version changes config schema (e.g., switching from PyArrow to csv.DictReader), but legacy transformer doesn't preserve all old fields
    - **Fix:** Always update `legacy_config_transformer.py` when changing config spec (config.py should document this requirement)
    - **Detection:** User configs silently lose options → sync failures with no clear error message
    - **Example:** source-s3 v3→v4 dropped `newlines_in_values` CSV option because transformer didn't copy it from `format_options.newlines_in_values`
    - **Prevention:** When adding/changing config fields, grep for `legacy_config_transformer` and update transformation logic; add test cases in `test_legacy_config_transformer.py` covering the new fields

## Approachable Areas

**Well-documented, good for new contributors:**

1. **Python HTTP API connectors** (`airbyte-integrations/connectors/source-*` without database dependencies)
   - Clear inheritance pattern from `HttpStream`
   - Examples: `source-appsflyer/`, `source-cart/`
   - Comprehensive test coverage with `requests-mock`
   - No-code Connector Builder documentation

2. **File-based connectors** (`airbyte-integrations/connectors/source-s3`, `source-gcs`, `source-azure-blob-storage`)
   - Clear inheritance from `AbstractFileBasedSpec` in file-based CDK
   - Well-defined patterns for format options (CSV, Parquet, Avro, JSONL)
   - Good test coverage in `unit_tests/v4/` directories
   - Examples of legacy config migration in `legacy_config_transformer.py`

3. **Documentation improvements** (`docs/`, `docusaurus/`)
   - Markdown files, straightforward structure
   - Prettier auto-formatting, no complex build

4. **Connector Builder schemas** (`airbyte-integrations/connectors/*/schemas/`)
   - JSON schema definitions for configuration
   - Clear validation patterns

5. **Python CDK utilities** (`airbyte-cdk/python/airbyte_cdk/sources/utils/`)
   - Helper functions for transformations, schema normalization
   - Well-tested, isolated modules

6. **Gradle build improvements** (`buildSrc/`)
   - Custom plugins for connector conventions
   - Clear Kotlin DSL examples

**Areas with good test coverage (confidence in changes):**
- Java CDK modules (extensive JUnit test fixtures)
- Python base streams (unit_tests/ with high coverage)
- Database sources with TestContainers (integration_tests/)
- File-based connectors with unit tests for config transformers and stream readers
