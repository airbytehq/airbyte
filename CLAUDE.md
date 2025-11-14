# Airbyte Repository Guide

## Overview

Airbyte is an open-source data integration platform that provides 600+ connectors for moving data from APIs, databases, and files to various data warehouses and lakes. The repository contains:

- Source and destination connectors (600+)
- Multiple CDKs (Java CDK, Bulk CDK, Python CDK)
- CI/CD automation infrastructure
- Documentation (Docusaurus-based)
- Comprehensive testing frameworks

**Repository Root:** `/home/user/airbyte`  
**License:** MIT (platform code) and ELv2 (enterprise features)  
**Language Mix:** Java, Kotlin, Python, TypeScript, Bash, YAML

---

## 1. Repository Structure

### Major Directories

```
/home/user/airbyte/
├── airbyte-cdk/                 # Connector Development Kits
│   ├── java/                    # Java CDK (legacy, fully featured)
│   ├── bulk/                    # Bulk CDK (Kotlin-based, modern)
│   └── python/                  # Python CDK (moved to separate repo)
├── airbyte-integrations/        # Connectors and bases
│   ├── connectors/              # 600+ individual connectors
│   │   ├── source-*/
│   │   ├── destination-*/
│   │   └── build.gradle         # Root for all Java connectors
│   ├── bases/                   # Shared frameworks
│   │   ├── base/
│   │   ├── base-java/
│   │   ├── base-normalization/
│   │   └── connector-acceptance-test/
│   └── connectors-performance/  # Performance testing harnesses
├── airbyte-ci/                  # CI/CD orchestration
│   ├── connectors/              # Connector-specific CI tools
│   │   ├── pipelines/           # Dagger-based CI pipeline definitions (Python)
│   │   ├── connector_ops/       # Connector operations utilities
│   │   ├── ci_credentials/      # Secrets management
│   │   ├── metadata_service/    # Connector metadata management
│   │   └── live-tests/          # Live integration tests
├── docs/                        # Documentation sources
│   ├── ai-agents/               # AI agents documentation
│   ├── community/               # Community documentation
│   ├── developers/              # Developer guides
│   ├── integrations/            # Connector integration docs
│   ├── platform/                # Platform documentation
│   └── release_notes/           # Release notes
├── docusaurus/                  # Documentation website (TypeScript/React)
├── docker-images/               # Docker image definitions
├── tools/                       # Development tools
│   ├── bin/                     # Executable scripts
│   ├── gradle/                  # Gradle helper scripts
│   ├── schema_generator/        # JSON schema generation
│   └── site/                    # Site generation tools
├── poe-tasks/                   # Poethepoet task definitions
├── buildSrc/                    # Gradle build extensions
├── .github/                     # GitHub Actions workflows
│   └── workflows/               # 50+ workflow YAML files
└── gradle/                      # Gradle wrapper files
```

### Directory Purposes

| Directory | Purpose |
|-----------|---------|
| **airbyte-cdk/** | Provides foundational code for building connectors (Java CDK, Bulk CDK). |
| **airbyte-integrations/connectors/** | Houses 600+ individual connectors (source and destination). |
| **airbyte-integrations/bases/** | Shared test frameworks, normalization, and acceptance tests. |
| **airbyte-ci/connectors/pipelines/** | Dagger-based Python framework for running CI jobs. |
| **docs/** | Documentation source files organized by topic. |
| **docusaurus/** | Documentation website built with Docusaurus (TypeScript). |
| **docker-images/** | Base Docker images for different connector types. |
| **.github/workflows/** | GitHub Actions automation for CI/CD. |

---

## 2. Technology Stack

### Programming Languages

| Language | Use Cases | Key Files |
|----------|-----------|-----------|
| **Java** | Core CDK, database connectors, performance-critical code | `airbyte-cdk/java/`, connectors with `build.gradle` |
| **Kotlin** | Bulk CDK (modern alternative to Java CDK) | `airbyte-cdk/bulk/` |
| **Python** | Declarative/low-code connectors, testing framework | `airbyte-ci/`, connectors with `pyproject.toml` |
| **TypeScript** | Documentation website (Docusaurus) | `docusaurus/` |
| **Bash** | Build scripts, utility scripts | `poe-tasks/`, `tools/bin/` |
| **YAML** | Manifest-based connectors, GitHub Actions, configuration | Connector `manifest.yaml`, `.github/workflows/` |

### Build Systems

#### Gradle (Java/Kotlin)
- **Root Configuration:** `/home/user/airbyte/build.gradle`
- **Settings:** `/home/user/airbyte/settings.gradle`
- **Properties:** `/home/user/airbyte/gradle.properties` (VERSION=0.64.7)
- **JVM Version:** Java 21
- **Key Gradle Plugins:**
  - `airbyte-java-connector` - Custom plugin for Java connector builds
  - `io.airbyte.gradle.docker` - Docker image generation
  - `com.google.devtools.ksp` - Kotlin Symbol Processing
  - `com.github.spotbugs` - Bug detection
  - `org.jetbrains.kotlin.jvm` - Kotlin compilation

```gradle
// build.gradle highlights:
- Targets Java 21, Kotlin 1.9
- Enables JUnit 5 for testing
- Configures Spotbugs for code analysis
- Reproducible archive generation
- Parallel test execution support
```

#### Poetry (Python)
- **Connectors using Poetry:** `destination-amazon-sqs`, `destination-astra`, etc.
- **Example:** `/home/user/airbyte/airbyte-integrations/connectors/destination-amazon-sqs/pyproject.toml`
- **Dependencies:** Python ^3.9,<3.12
- **Scripts Define:** Entry points via `[tool.poetry.scripts]`

```toml
[tool.poetry.dependencies]
python = "^3.9,<3.12"
airbyte-cdk = "==0.68.1"
boto3 = "==1.34.56"

[tool.poetry.scripts]
destination-amazon-sqs = "destination_amazon_sqs.run:run"
```

#### Poetry (Pipelines)
- **Location:** `/home/user/airbyte/airbyte-ci/connectors/pipelines/pyproject.toml`
- **Version:** 5.5.0
- **Python:** ~3.11
- **Key Dependencies:** dagger-io, docker, pygit2, sentry-sdk

#### NPM/pnpm (Documentation)
- **Package Manager:** pnpm (lock file: `docusaurus/pnpm-lock.yaml`)
- **Node Version:** `.nvmrc` specifies version
- **Configuration:** `docusaurus/package.json`

### Key Frameworks & Dependencies

#### Java/Kotlin CDK
- **Testing:** JUnit 5 (5.10.2), Mockito (5.2.1)
- **Database:** JOOQ (3.19.11), HikariCP (5.1.0)
- **HTTP:** Apache HttpComponents
- **CDC:** Debezium (3.0.1.Final)
- **Cloud:** Azure libraries, AWS SDK
- **Build:** Gradle 8.x wrapper

#### Python
- **Testing:** pytest, pytest-cov
- **Code Generation:** jsonschema2pojo
- **Linting:** Ruff (integrated via pre-commit)
- **Type Checking:** mypy
- **CLI:** Click, asyncclick
- **Cloud:** google-cloud-secret-manager
- **Async:** asyncio, trio, anyio

#### CI/CD Tools
- **Dagger:** Container-based CI/CD orchestration (`dagger-io==0.13.3`)
- **Docker:** Container runtime
- **Pytest:** Test discovery and execution
- **Ruff:** Python linting and formatting

---

## 3. Development Workflows

### Build System Execution

#### Gradle Build
```bash
# Build root project
./gradlew build

# Build specific CDK
./gradlew :airbyte-cdk:java:airbyte-cdk:build

# Build specific connector
./gradlew :airbyte-integrations:connectors:source-postgres:build

# Run tests with specific concurrency
./gradlew test -PtestExecutionConcurrency=4

# List all dependencies
./gradlew listAllDependencies
```

#### Poetry Build
```bash
# Install dependencies
poetry install --all-extras

# Run tests
poetry run pytest

# Run specific test suites
poetry run pytest unit_tests
poetry run pytest integration_tests
```

#### Poe Tasks (Unified Interface)
Located in `/home/user/airbyte/poe_tasks.toml` and referenced by all connectors.

**For Poetry Connectors** (`poe-tasks/poetry-connector-tasks.toml`):
```bash
poe install               # Install project + CDK CLI
poe test-all              # Run unit + integration tests
poe format-check          # Check code formatting with Ruff
poe lint-check            # Lint and type check
poe fix-all               # Auto-fix formatting and linting
```

**For Gradle Connectors** (`poe-tasks/gradle-connector-tasks.toml`):
```bash
poe gradle build          # Build connector
poe test-all              # Run all tests (gradle check)
poe gradle test           # Run unit tests
```

### Testing Frameworks

#### Unit Tests
- **Python:** pytest with unittest-style fixtures
- **Java:** JUnit 5 with Mockito
- **Location:** `unit_tests/` (Python), `src/test/` (Java)
- **Execution:** Via `poe test-unit-tests` or `pytest unit_tests`

#### Integration Tests
- **Python:** pytest in `integration_tests/` directory
- **Java:** TestContainers for containerized dependencies
- **Execution:** Via `poe test-integration-tests`
- **Credentials:** Fetched from Google Secrets Manager (GSM)

#### Acceptance Tests
- **Framework:** Connector Acceptance Tests (CAT) - pytest plugin
- **Location:** `/home/user/airbyte/airbyte-integrations/bases/connector-acceptance-test/`
- **Configuration:** `acceptance-test-config.yml` per connector
- **Strictness Levels:** 5 levels from basic to full validation
- **Test Types:** Discovery, schema validation, data conformance, incremental syncs

#### Test Configuration Files
```yaml
# acceptance-test-config.yml structure
tests:
  - test_type: discovery
  - test_type: basic_read
  - test_type: incremental
  - test_type: full_refresh
  - test_type: spec
```

### Code Quality Tools

#### Ruff (Python Linting & Formatting)
- **Configuration:** `/home/user/airbyte/ruff.toml`
- **Target Python:** 3.10
- **Line Length:** 140
- **Enabled Rules:** `I` (isort) - import sorting
- **Formatting:** Double quotes, auto-fixes enabled
- **Execution:** Via pre-commit hooks or `poe format-check`

```toml
[lint]
select = ["I"]  # Only import sorting enforced globally
# Many other rules commented out for gradual adoption

[lint.isort]
known-first-party = ["airbyte", "airbyte_cdk", "connector_ops", "pipelines"]
```

#### Spotbugs (Java Bug Detection)
- **Configuration:** `/home/user/airbyte/build.gradle`
- **Effort Level:** MAX
- **Confidence Level:** HIGH
- **Exclude Filter:** `spotbugs-exclude-filter-file.xml`
- **Reports:** HTML reports in `build/spotbugs/`

#### Pre-Commit Hooks
- **Configuration:** `/home/user/airbyte/.pre-commit-config.yaml`
- **Hooks:**
  1. **Ruff Check** - Linting with fix flag
  2. **Ruff Format** - Code formatting
  3. **Prettier** - JSON/YAML formatting
  4. **addlicense** - Add Apache license headers to Java/Python/Kotlin files
  5. **Spotless** - Format Java files with Maven

#### Maven (Spotless)
- **POM Configuration:** `/home/user/airbyte/spotless-maven-pom.xml`
- **Purpose:** Java code formatting with Google's code style
- **Execution:** Via pre-commit or `mvn -f spotless-maven-pom.xml spotless:apply`

### Testing Execution Flow

```
Developer Makes Changes
    ↓
Pre-commit hooks run (Ruff, Prettier, addlicense, Spotless)
    ↓
Local Tests Run (unit + integration)
    ↓
Push to Feature Branch
    ↓
GitHub Actions: connector-ci-checks.yml
    - Detects modified connectors
    - Runs format/lint checks
    - Builds connector images
    - Runs acceptance tests
    - Runs CAT (Connector Acceptance Tests)
    ↓
[Optional] Manual Regression Tests
    ↓
Merge to Master
    ↓
GitHub Actions: publish_connectors.yml
    - Auto-publishes changed connectors
    - Updates Docker images
```

---

## 4. Connectors Architecture

### Connector Types & Organization

#### 1. Manifest-Only (Low-Code/Declarative)
- **Framework:** Declarative Manifest (YAML-based)
- **Language:** YAML only
- **Example:** `source-stripe` (`manifest.yaml` with 623KB+ configuration)
- **Base Image:** `airbyte/source-declarative-manifest:7.4.1`
- **Development:** No code required, configuration-driven
- **Metadata:** `metadata.yaml` with connector details
- **Testing:** Acceptance tests via YAML configuration

```yaml
# manifest.yaml structure
version: 6.42.1
type: DeclarativeSource
definitions:
  base_stream: ...
  base_requester: ...
  base_paginator: ...
streams:
  - accounts
  - customers
```

#### 2. Python CDK-Based
- **Framework:** Python Connector Development Kit (now external)
- **Language:** Python with pyproject.toml
- **Build:** Poetry
- **Example:** `destination-amazon-sqs`
- **Dependencies:** `airbyte-cdk==<version>`
- **Entry Point:** Defined in `[tool.poetry.scripts]`
- **Testing:** pytest with unit + integration tests

```toml
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.dependencies]
airbyte-cdk = "==0.68.1"

[tool.poetry.scripts]
destination-amazon-sqs = "destination_amazon_sqs.run:run"
```

#### 3. Java CDK-Based (Legacy)
- **Framework:** Java Connector Development Kit
- **Language:** Java/Kotlin
- **Build:** Gradle with custom `airbyte-java-connector` plugin
- **Example:** `source-postgres`
- **CDK Features:** `db-sources`, `db-destinations`, `datastore-postgres`, etc.
- **Testing:** JUnit 5 with Testcontainers
- **Build Configuration Example:**

```gradle
plugins {
    id 'airbyte-java-connector'
    id 'com.github.eirnym.js2p'
    id "io.airbyte.gradle.docker"
    id 'airbyte-connector-docker-convention'
}

airbyteJavaConnector {
    cdkVersionRequired = '0.48.14'
    features = ['db-sources', 'datastore-postgres']
    useLocalCdk = false
}
```

#### 4. Bulk CDK-Based (Modern Kotlin)
- **Framework:** Bulk CDK (newer alternative to Java CDK)
- **Language:** Kotlin
- **Build:** Gradle with Bulk CDK modules
- **Architecture:** Core modules + optional toolkits
- **Modules:** `extract`, `load`, `extract-jdbc`, `load-db`, etc.
- **Status:** Currently incubating, not widely used yet
- **License:** ELv2

### Connector Directory Structure

```
/source-postgres/
├── build.gradle                    # Gradle configuration
├── gradle.properties               # Gradle properties
├── metadata.yaml                   # Connector metadata
├── README.md                       # Documentation
├── icon.svg                        # Connector icon
├── poe_tasks.toml                  # Task definitions
├── acceptance-test-config.yml      # CAT configuration
├── src/
│   ├── main/
│   │   ├── java/io/airbyte/integrations/source/postgres/
│   │   └── resources/
│   └── test-integration/
├── integration_tests/
│   ├── Dockerfile
│   ├── README.md
│   ├── acceptance.py
│   ├── configured_catalog_template.json
│   └── seed.sql
└── make-big-postgres-schema.sh

/source-stripe/
├── metadata.yaml                   # Connector metadata
├── manifest.yaml                   # 623KB+ YAML config
├── acceptance-test-config.yml
├── README.md
├── icon.svg
├── integration_tests/
│   └── test_*.py
├── sample_files/                   # Sample data
└── unit_tests/                     # Unit tests directory
```

### Metadata.yaml Structure

```yaml
# Key fields in metadata.yaml
data:
  ab_internal:
    ql: 400              # Quality level
    sl: 300              # Support level
  connectorType: source/destination
  connectorSubtype: api/database
  definitionId: <UUID>  # Unique connector ID
  dockerImageTag: 1.2.3
  dockerRepository: airbyte/source-postgres
  name: "Postgres"
  license: ELv2
  supportLevel: certified/community/archived
  releaseStage: generally_available/beta/alpha
  tags:
    - cdk:java
    - language:java
    - database
  connectorBuildOptions:
    baseImage: docker.io/airbyte/source-java-connector-base:1.0
```

### Connector Bases (Shared Frameworks)

**Location:** `/home/user/airbyte/airbyte-integrations/bases/`

1. **base/** - Legacy base image
2. **base-java/** - Java connector base
3. **base-normalization/** - dbt-based data normalization
   - Templates for: Snowflake, BigQuery, MySQL, PostgreSQL, DuckDB, ClickHouse, etc.
4. **connector-acceptance-test/** - CAT pytest plugin
   - Location: `/home/user/airbyte/airbyte-integrations/bases/connector-acceptance-test/`
   - Purpose: Standard test suite for all connectors
   - Provides fixtures, configuration parsing, test discovery

### Connectors CI Checks (GitHub Actions)

**Workflow:** `/.github/workflows/connector-ci-checks.yml`

```yaml
# Key Jobs:
1. generate-matrix:       # Detects modified connectors
2. format_and_lint_check: # Linting checks
3. test_connectors:       # CAT + unit tests
4. build_connectors:      # Docker image builds
5. build_normalization:   # Normalization image builds
6. build_acceptance_test: # CAT image build
```

---

## 5. CDK Details

### Java CDK Structure

**Location:** `/home/user/airbyte/airbyte-cdk/java/airbyte-cdk/`

```
core/                   # Base classes (dependencies, core logic)
├── src/main/          # Main implementation
├── src/test/          # Unit tests
└── src/testFixtures/  # Shared test utilities

db-sources/            # Database source utilities
db-destinations/       # Database destination utilities
datastore-postgres/    # PostgreSQL-specific implementations
datastore-mongo/       # MongoDB-specific implementations
datastore-bigquery/    # BigQuery-specific implementations
s3-destinations/       # S3 destination utilities
gcs-destinations/      # GCS destination utilities
azure-destinations/    # Azure destination utilities
typing-deduping/       # Type system and deduplication
dependencies/          # Shared version management (BOMs)
```

**Publishing:**
- Versions managed in: `airbyte-cdk/java/airbyte-cdk/core/src/main/resources/version.properties`
- Published to: `https://airbyte.mycloudrepo.io/public/repositories/airbyte-public-jars/`
- Maven coordinates: `io.airbyte.cdk:*:version`

### Bulk CDK (Kotlin)

**Location:** `/home/user/airbyte/airbyte-cdk/bulk/`

```
core/
├── base/               # Micronaut entry point, core interfaces
├── extract/            # Source extraction framework
└── load/               # Destination loading framework

toolkits/
├── extract-jdbc/       # JDBC-based source extraction
├── extract-cdc/        # Change Data Capture extraction
├── load-db/            # Database destination loading
├── load-s3/            # S3 destination loading
├── load-gcs/           # GCS destination loading
├── load-azure-blob-storage/ # Azure Blob Storage
└── [More toolkits...]
```

**Version Management:** SemVer, auto-published on merge to master
**Changelog:** `airbyte-cdk/bulk/changelog.md`

### Python CDK

**Location:** `/home/user/airbyte/airbyte-cdk/python/README.md`
**Status:** Moved to external repository: `https://github.com/airbytehq/airbyte-python-cdk`

Current repository only contains a stub README pointing to the external repo.

---

## 6. CI/CD Setup

### GitHub Actions Workflows

**Location:** `/home/user/airbyte/.github/workflows/`

#### Key Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **connector-ci-checks.yml** | Pull Request | Runs linting, tests, and builds for modified connectors |
| **publish_connectors.yml** | Push to master or manual | Publishes connectors to registries |
| **java-cdk-tests.yml** | Changes to Java CDK | Tests Java CDK changes |
| **publish-java-cdk-command.yml** | Slash command | Publishes Java CDK version |
| **docker-connector-image-publishing.yml** | After publish | Pushes Docker images to registries |
| **docs-build.yml** | Changes to docs | Builds documentation site |
| **format-fix-command.yml** | Slash command | Auto-fixes formatting issues |
| **regression_tests.yml** | Scheduled | Runs live connector tests |
| **connector-image-build.yml** | Manual or PR | Builds connector Docker images |

#### Connector CI Checks Workflow

```yaml
# .github/workflows/connector-ci-checks.yml
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

jobs:
  generate-matrix:        # Detect modified connectors
  format_and_lint_check:  # Run Ruff, Prettier
  test_connectors:        # Run CAT tests
  build_connectors:       # Build Docker images
  connector-ci-checks-summary: # Final status
```

### Airbyte CI Tool (`airbyte-ci`)

**Location:** `/home/user/airbyte/airbyte-ci/connectors/pipelines/`
**Type:** Dagger-based CI orchestration (Python)
**Version:** 5.5.0
**Installation:** Via Makefile (`make tools.airbyte-ci.install`)

```bash
# Installation
make tools.airbyte-ci.install

# Usage Examples
airbyte-ci connectors --name=source-postgres test
airbyte-ci connectors --name=source-postgres build
airbyte-ci connectors --name=source-postgres check
```

**Components:**

1. **Pipelines Module** - Main CI orchestration
   - Location: `/home/user/airbyte/airbyte-ci/connectors/pipelines/pipelines/`
   - Entry: `cli/airbyte_ci.py`
   - Dagger-based container orchestration

2. **Connector Ops** - Connector utilities
   - Metadata parsing, connector validation
   - Publishing automation

3. **CI Credentials** - Secrets management
   - Google Secrets Manager (GSM) integration
   - Environment setup for tests

4. **Metadata Service** - Connector metadata management
   - Schema: `lib/metadata_service/models/generated/`
   - Metadata validation and generation

5. **Live Tests** - Live connector integration tests
   - Real endpoint testing
   - Data validation

### Dagger Integration

**Configuration:**
- Python 3.11 project using `dagger-io==0.13.3`
- Containerized CI/CD execution
- Supports remote caching (S3)

```python
# Dagger pipeline structure
# pipelines/dagger/containers/*.py define container build steps
# pipelines/airbyte_ci/connectors/*.py define connector-specific operations
```

### Build Cache Strategy

**Gradle Build Cache:**
- **Local Cache:** Enabled in CI with S3 backend
- **S3 Bucket:** `ab-ci-cache` in `us-west-2`
- **Prefix:** `connectors-ci-cache/` (configurable)
- **Config:** `settings.gradle` lines 128-147

```gradle
buildCache {
    local {
        enabled = true
        push = true
    }
    remote(AwsS3BuildCache) {
        enabled = true
        bucket = 'ab-ci-cache'
        region = 'us-west-2'
        prefix = "${System.getProperty('s3BuildCachePrefix', 'connectors')}-ci-cache/"
    }
}
```

---

## 7. Documentation Organization

### Documentation Structure

**Source Directories:**

1. **Platform Docs** (`/home/user/airbyte/docs/platform/`)
   - Architecture, deployment, concepts
   - Organized by topics

2. **Integration Docs** (`/home/user/airbyte/docs/integrations/`)
   - Connector-specific documentation
   - Source and destination guides

3. **Developer Docs** (`/home/user/airbyte/docs/developers/`)
   - Connector development guides
   - API documentation
   - Testing guides

4. **Community Docs** (`/home/user/airbyte/docs/community/`)
   - Community resources
   - Contribution guidelines

5. **AI Agents Docs** (`/home/user/airbyte/docs/ai-agents/`)
   - AI integration documentation

6. **Release Notes** (`/home/user/airbyte/docs/release_notes/`)
   - Version-specific notes

### Website Setup (Docusaurus)

**Location:** `/home/user/airbyte/docusaurus/`

```
├── docusaurus.config.ts     # Main Docusaurus config
├── package.json             # Node dependencies
├── pnpm-lock.yaml          # Lock file (pnpm)
├── sidebar-*.js            # Navigation sidebars
├── src/                    # React components
├── platform_versioned_docs/ # Versioned documentation
├── static/                 # Static assets
├── api-docs/              # API documentation
└── i18n/                  # Internationalization
```

**Build Configuration:**
- **Node Version:** Specified in `.nvmrc`
- **Package Manager:** pnpm
- **Framework:** Docusaurus v2/v3
- **Versioning:** Multi-version support via `platform_versions.json`

**Deployment:**
- **Platform:** Vercel (via `vercel.json`)
- **Build Command:** Configured in Vercel
- **Vale Linting:** `vale.ini` and `vale-ci.ini` for prose checks

### Documentation as Code

**Vale Styles:** `/home/user/airbyte/docs/vale-styles/`
- Custom rules for documentation consistency
- Grammar and style checking

**Markdown Linting:** `.markdownlint.jsonc`
- Formatting rules for Markdown files

**Code Quality:**
- Check script: `/home/user/airbyte/docs/check-docs-git-diff.sh`
- Validates documentation changes in PRs

---

## 8. Key Configuration Files

### Root Configuration Files

| File | Purpose |
|------|---------|
| **build.gradle** | Root Gradle configuration for all Java/Kotlin projects |
| **settings.gradle** | Gradle settings, build cache, plugin management |
| **gradle.properties** | Gradle JVM args, parallelism, VERSION=0.64.7 |
| **poe_tasks.toml** | Root poethepoet task configuration |
| **ruff.toml** | Python linting and formatting rules |
| **.pre-commit-config.yaml** | Git pre-commit hooks |
| **.editorconfig** | Editor formatting standards |
| **pytest.ini** | Pytest configuration |
| **codecov.yml** | Code coverage thresholds (90%) |
| **spotbugs-exclude-filter-file.xml** | Spotbugs exclusions |
| **spotless-maven-pom.xml** | Maven Spotless formatting (Java) |

### Root .gitignore

Excludes:
- `.venv/`, `node_modules/`
- Build artifacts (`build/`, `dist/`)
- IDE files (`.idea/`, `.vscode/`)
- OS files (`*.swp`, `.DS_Store`)
- `pnpm-lock.yaml` files

### Makefile

**Location:** `/home/user/airbyte/Makefile`

**Key Targets:**
```makefile
make tools.install              # Install all development tools
make tools.airbyte-ci.install   # Install airbyte-ci CLI
make tools.pre-commit.install   # Install pre-commit hooks
make tools.git-hooks.install    # Setup git hooks
make version.bulk.cdk           # Check Bulk CDK version
```

### Connector Configuration Files

**Each connector directory contains:**

1. **metadata.yaml** - Connector metadata
2. **build.gradle** or **pyproject.toml** - Build configuration
3. **poe_tasks.toml** - Task references
4. **acceptance-test-config.yml** - CAT configuration
5. **README.md** - Documentation
6. **icon.svg** - Connector icon

### Environment Configuration

**Python Version:** `.python-version` (specified at repo root)

**Version File:** `gradle.properties`
```properties
VERSION=0.64.7  # Main repository version
```

---

## 9. Important Patterns & Conventions

### Connector Naming Convention

```
source-<platform>    # e.g., source-postgres, source-stripe
destination-<platform> # e.g., destination-bigquery
```

### Testing Patterns

**Python Connector Test Structure:**
```
unit_tests/
  ├── __init__.py
  ├── test_*.py
  └── test_source.py

integration_tests/
  ├── __init__.py
  ├── test_*.py
  └── conftest.py
```

**Java Connector Test Structure:**
```
src/test/
  ├── java/io/airbyte/integrations/source/<name>/
  │   ├── integration/
  │   └── unit/
  └── resources/

src/test-integration/
  └── java/...
```

### Metadata-Driven Development

All connectors must have `metadata.yaml`:
```yaml
data:
  definitionId: <UUID>
  name: "<Connector Name>"
  supportLevel: certified|community|archived
  releaseStage: generally_available|beta|alpha
  tags:
    - cdk:java|python|low-code
    - language:java|python|manifest-only
```

### CDK Version Management

**Java CDK:**
- Version file: `airbyte-cdk/java/airbyte-cdk/core/src/main/resources/version.properties`
- Connectors pin version in `build.gradle` via `airbyteJavaConnector { cdkVersionRequired = '...' }`

**Bulk CDK:**
- Version file: `airbyte-cdk/bulk/version.txt` or similar
- Bump via: `/bump-bulk-cdk-version bump=major|minor|patch`

**Python CDK:**
- External repository: https://github.com/airbytehq/airbyte-python-cdk
- Pinned in connector `pyproject.toml` via `airbyte-cdk == "<version>"`

---

## 10. Common Development Tasks

### Setting Up Development Environment

```bash
# 1. Clone repository
git clone https://github.com/airbytehq/airbyte.git
cd airbyte

# 2. Install development tools
make tools.install
make tools.git-hooks.install

# 3. Verify airbyte-ci installation
make tools.airbyte-ci.check
```

### Working with a Specific Connector

```bash
# Navigate to connector
cd airbyte-integrations/connectors/source-postgres

# Install dependencies (Poetry connectors)
poe install

# Run all tests
poe test-all

# Run only unit tests
poe test-unit-tests

# Run only integration tests
poe test-integration-tests

# Check formatting
poe format-check

# Auto-fix formatting
poe fix-all

# Build Docker image
airbyte-ci connectors --name=source-postgres build

# Run acceptance tests
airbyte-ci connectors --name=source-postgres test
```

### Running Java Connector Tests

```bash
cd airbyte-integrations/connectors/source-postgres

# Build
poe gradle build

# Run unit tests
poe gradle test

# Run integration tests
poe gradle integrationTestJava
```

### Building a Connector Image

```bash
# Using airbyte-ci
airbyte-ci connectors --name=source-postgres build

# Using Gradle (Java)
./gradlew :airbyte-integrations:connectors:source-postgres:build

# Using Docker
docker build -t airbyte/source-postgres:latest .
```

### Running Acceptance Tests Locally

```bash
# 1. Install acceptance test framework
cd airbyte-integrations/bases/connector-acceptance-test
poetry install

# 2. Set up GSM credentials
export GCP_GSM_CREDENTIALS='<service-account-json>'

# 3. Fetch connector secrets
ci_credentials connectors/source-postgres write-to-storage

# 4. Run CAT
poetry run pytest -p connector_acceptance_test.plugin \
  --acceptance-test-config=../../connectors/source-postgres
```

### Publishing a Connector

```bash
# Via GitHub Actions slash command (in PR)
/publish-java-cdk                    # Publish Java CDK
/publish-connectors --name=<connector> # Publish specific connector

# Via workflow dispatch in GitHub UI
# Go to Actions > Publish Connectors > Run workflow
```

---

## 11. Repository Insights

### Code Statistics

- **Total Connectors:** 600+
- **Supported Databases:** 30+
- **Supported APIs:** 300+
- **Languages:** Java, Kotlin, Python, TypeScript, Bash
- **Test Frameworks:** pytest, JUnit 5, Testcontainers
- **CI Workflows:** 50+ GitHub Actions workflows

### Key Technologies

| Component | Tech Stack |
|-----------|-----------|
| **Build System** | Gradle (Java/Kotlin), Poetry (Python), npm/pnpm (docs) |
| **Testing** | pytest, JUnit 5, Testcontainers, CAT (custom) |
| **Code Quality** | Ruff, Spotbugs, mypy, Spotless |
| **CI/CD** | GitHub Actions, Dagger, Docker |
| **Documentation** | Docusaurus 2/3, TypeScript/React, Vale |
| **Secrets** | Google Secrets Manager (GSM) |
| **Caching** | S3, Gradle build cache |

### Development Statistics

- **Main Branch:** `master`
- **Pull Request Requirements:**
  - Maintainer write access enabled
  - Pre-commit hooks passing
  - CI/CD green
  - Documentation updated
- **Contribution:** Fork + PR from personal GitHub account required

---

## 12. Troubleshooting & Common Issues

### Gradle Issues

**Issue:** `Gradle could not find dependency`
**Solution:** Check `settings.gradle` repository configuration, ensure S3 cache is accessible

**Issue:** `Java version mismatch`
**Solution:** Ensure Java 21 is installed and JAVA_HOME is set correctly

### Test Failures

**Issue:** Integration tests failing due to missing credentials
**Solution:** 
```bash
export GCP_GSM_CREDENTIALS='<path-to-service-account-json>'
ci_credentials connectors/<connector-name> write-to-storage
```

**Issue:** Docker image build failures
**Solution:** Ensure Docker daemon is running and sufficient disk space available

### Pre-commit Hook Issues

**Issue:** Pre-commit hooks not running
**Solution:**
```bash
make tools.git-hooks.install
git config core.hooksPath .git/hooks
```

**Issue:** Spotless formatting failures
**Solution:**
```bash
brew install maven  # macOS
mvn -f spotless-maven-pom.xml spotless:apply
```

---

## 13. Quick Reference Links

### Key Files & Directories

- Root Gradle Config: `/home/user/airbyte/build.gradle`
- Connector Directory: `/home/user/airbyte/airbyte-integrations/connectors/`
- Java CDK: `/home/user/airbyte/airbyte-cdk/java/airbyte-cdk/`
- Bulk CDK: `/home/user/airbyte/airbyte-cdk/bulk/`
- CI Pipelines: `/home/user/airbyte/airbyte-ci/connectors/pipelines/`
- Documentation: `/home/user/airbyte/docs/`
- Website: `/home/user/airbyte/docusaurus/`
- Workflows: `/home/user/airbyte/.github/workflows/`

### External Links

- **Official Docs:** https://docs.airbyte.com
- **Connector Registry:** https://connectors.airbyte.com
- **GitHub Repository:** https://github.com/airbytehq/airbyte
- **Python CDK (External):** https://github.com/airbytehq/airbyte-python-cdk
- **Slack Community:** https://airbyte.com/community
- **Issues:** https://github.com/airbytehq/airbyte/issues

---

## Last Updated

Generated: November 14, 2025
Repository Version: 0.64.7
Last Commit: Support multiple ts precision decoding (#69326)

---

This guide provides a comprehensive overview of the Airbyte repository structure and development workflows. For specific connector development, refer to the official documentation at https://docs.airbyte.com/connector-development.
