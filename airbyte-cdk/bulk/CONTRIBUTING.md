# Contributing to the Bulk CDK

Thank you for your interest in contributing to the Airbyte Bulk CDK!

## Prerequisites

- **Java 21** or higher
- **Gradle** (uses the wrapper, no separate installation needed)

## Generating Documentation

The Bulk CDK uses [Dokka](https://kotlinlang.org/docs/dokka-introduction.html) to generate API documentation from KDoc comments.

### Generate Documentation

```bash
./gradlew :airbyte-cdk:bulk:docsGenerate
```

This generates HTML documentation in `airbyte-cdk/bulk/build/dokka/htmlMultiModule/`.

### View Generated Documentation

```bash
# macOS
open airbyte-cdk/bulk/build/dokka/htmlMultiModule/index.html

# Linux
xdg-open airbyte-cdk/bulk/build/dokka/htmlMultiModule/index.html
```

## Other Useful Commands

```bash
# Build all modules
./gradlew :airbyte-cdk:bulk:bulkCdkBuild

# Run tests
./gradlew :airbyte-cdk:bulk:test
```

## More Information

For architecture, publishing, development workflow, and other details, see the [README](README.md).

For general Airbyte contribution guidelines, see the [main contributing guide](../../docs/contributing-to-airbyte/README.md).
