# Contributing to the Bulk CDK

Thank you for your interest in contributing to the Airbyte Bulk CDK! This guide will help you get started with development, testing, and documentation.

## Table of Contents

- [Development Setup](#development-setup)
- [Building the CDK](#building-the-cdk)
- [Running Tests](#running-tests)
- [Generating Documentation](#generating-documentation)
- [Publishing Changes](#publishing-changes)
- [Code Style and Standards](#code-style-and-standards)

## Development Setup

### Prerequisites

- **Java 21**: The Bulk CDK requires Java 21 or higher
- **Gradle**: Uses the Gradle wrapper (no separate installation needed)
- **Kotlin**: The CDK is written in Kotlin (managed by Gradle)

### Project Structure

The Bulk CDK consists of two main components:

- **Core modules** (`core/`): Essential functionality for all connectors
  - `base`: Foundation classes and interfaces
  - `extract`: Source connector functionality
  - `load`: Destination connector functionality

- **Toolkits** (`toolkits/`): Optional modules for specific use cases
  - `extract-cdc`: Change Data Capture support
  - `extract-jdbc`: JDBC-based sources
  - `load-*`: Various destination-specific toolkits

## Building the CDK

### Build All Modules

```bash
./gradlew :airbyte-cdk:bulk:bulkCdkBuild
```

### Build Specific Module

```bash
./gradlew :airbyte-cdk:bulk:core:base:build
```

### Clean Build

```bash
./gradlew :airbyte-cdk:bulk:clean :airbyte-cdk:bulk:bulkCdkBuild
```

## Running Tests

### Run All Tests

```bash
./gradlew :airbyte-cdk:bulk:test
```

### Run Tests for Specific Module

```bash
./gradlew :airbyte-cdk:bulk:core:base:test
```

### Run Tests with Coverage

```bash
./gradlew :airbyte-cdk:bulk:test :airbyte-cdk:bulk:jacocoTestReport
```

## Generating Documentation

The Bulk CDK uses [Dokka](https://kotlinlang.org/docs/dokka-introduction.html) to generate API documentation from KDoc comments in the source code.

### Generate Documentation Locally

```bash
./gradlew :airbyte-cdk:bulk:dokkaHtmlMultiModule
```

This generates HTML documentation in `airbyte-cdk/bulk/build/dokka/htmlMultiModule/`.

### View Generated Documentation

After generating the documentation, you can view it by opening the index file in your browser:

```bash
# macOS
open airbyte-cdk/bulk/build/dokka/htmlMultiModule/index.html

# Linux
xdg-open airbyte-cdk/bulk/build/dokka/htmlMultiModule/index.html

# Windows
start airbyte-cdk/bulk/build/dokka/htmlMultiModule/index.html
```

### Convenience Task

A convenience task is available that generates documentation and prints the output location:

```bash
./gradlew :airbyte-cdk:bulk:dokkaGenerate
```

### Documentation Configuration

The Dokka configuration in `build.gradle` includes:

- **Public API only**: Only public classes and methods are documented
- **External links**: Links to Kotlin stdlib, coroutines, and Micronaut documentation
- **Source links**: Links back to GitHub source code for each documented element
- **Multi-module support**: Aggregates documentation from all core and toolkit modules

### Writing Good Documentation

When contributing code, please include KDoc comments for:

- All public classes and interfaces
- All public methods and properties
- Complex internal logic (use `@suppress` to exclude from public docs if needed)

Example:

```kotlin
/**
 * Manages the lifecycle of a destination connector.
 *
 * This class orchestrates the five-phase loading process:
 * 1. Initialize destination
 * 2. Initialize individual streams
 * 3. Run the data pipeline
 * 4. Finalize individual streams
 * 5. Teardown destination
 *
 * @property config The destination configuration
 * @property catalog The configured catalog of streams to sync
 */
class DestinationLifecycle(
    private val config: DestinationConfiguration,
    private val catalog: ConfiguredAirbyteCatalog
) {
    /**
     * Executes the complete destination lifecycle.
     *
     * @return A summary of the sync results
     * @throws DestinationException if any phase fails
     */
    suspend fun run(): SyncResult {
        // Implementation
    }
}
```

## Publishing Changes

### Version Bumping

Before merging a pull request, you must bump the CDK version and update the changelog.

#### Using Gradle Task

```bash
# Bump patch version (0.1.79 -> 0.1.80)
./gradlew :airbyte-cdk:bulk:bumpVersion --patch --changelog "Fix bug in stream processing"

# Bump minor version (0.1.79 -> 0.2.0)
./gradlew :airbyte-cdk:bulk:bumpVersion --minor --changelog "Add new authentication method"

# Bump major version (0.1.79 -> 1.0.0)
./gradlew :airbyte-cdk:bulk:bumpVersion --major --changelog "Breaking: Redesign state management"
```

#### Using GitHub PR Comment

You can also bump the version by commenting on your PR:

```
/bump-bulk-cdk-version bump=patch changelog="Fix bug in stream processing"
```

### Publishing Process

1. **Bump version** and update changelog (as described above)
2. **Create pull request** with your changes
3. **Get approval** from maintainers
4. **Merge to master** - This automatically triggers the [publish workflow](../../.github/workflows/publish-bulk-cdk.yml)
5. **Verify publication** at the [Maven repository](https://airbyte.mycloudrepo.io/public/repositories/airbyte-public-jars/io/airbyte/bulk-cdk/)

### Version Validation

The build process validates that the version doesn't already exist in the Maven repository. If you see an error like "Version X.Y.Z already exists", you need to bump the version again.

## Code Style and Standards

### Kotlin Style

- Follow [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html)
- Use meaningful variable and function names
- Prefer immutability (`val` over `var`)
- Use data classes for simple data containers

### Dependency Management

The Bulk CDK uses [BOM (Bill of Materials) dependencies](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html#bill-of-materials-bom-poms) to manage versions. When adding dependencies:

1. **Check if a BOM exists** for the library family (e.g., Jackson, Micronaut)
2. **Add the BOM** to the `allprojects` block in `build.gradle` if not present
3. **Add the dependency** without a version number (inherited from BOM)

Example:

```gradle
// In allprojects block
dependencies {
    api platform('com.fasterxml.jackson:jackson-bom:2.17.2')
}

// In your module
dependencies {
    implementation 'com.fasterxml.jackson.core:jackson-databind' // No version!
}
```

### Testing Philosophy

- **Test in the CDK**: Don't rely on connector tests to validate CDK functionality
- **Use dependency injection**: Mock concrete implementations realistically
- **Create fake connectors**: Define entire fake connectors in tests when needed
- **Test thoroughly**: The CDK should be rock-solid before connectors depend on it

### Development Workflow

Unlike the legacy Java CDK, there is no `useLocalCdk = true` option. This is intentional:

1. **Develop CDK changes** in the CDK repository
2. **Test thoroughly** in the CDK (using fake connectors if needed)
3. **Publish the CDK** with a new version
4. **Update connectors** to use the new CDK version

If you need to develop both simultaneously:

1. **Experiment in the connector** (keep CDK and connector code separate)
2. **Hoist mature code** into the Bulk CDK and test it there
3. **Publish CDK changes** and update the connector

## Getting Help

- **Documentation**: See the [README](README.md) for architecture overview
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/airbytehq/airbyte/issues)
- **Slack**: Join the [Airbyte Slack](https://airbyte.com/community) for community support
- **API Docs**: View the published [Bulk CDK API documentation](https://bulk-cdk-docs.vercel.app) (once deployed)

## License

The Bulk CDK is licensed under the Elastic License 2.0. See the [LICENSE](../../LICENSE) file for details.
