# Contributing to the Kotlin Bulk CDK

Thank you for your interest in contributing to the Airbyte Kotlin Bulk CDK!

## Prerequisites

- **JDK 21** (Java Development Kit) or higher
- **Gradle** (uses the wrapper, no separate installation needed)

### If you need to install Java

```bash
# Get sdkman (https://sdkman.io/)
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# Verify install
sdk version

# Show available versions
sdk list java | grep 21

# Install the latest and set as default
sdk install java 21.0.9-zulu
sdk default java 21.0.9-zulu
```

## Generating Documentation

The Kotlin Bulk CDK uses [Dokka](https://kotlinlang.org/docs/dokka-introduction.html) to generate API documentation from KDoc comments.

**Published Documentation**: The latest API documentation is available at https://airbyte-kotlin-cdk.vercel.app/

### Generate Documentation Locally

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
