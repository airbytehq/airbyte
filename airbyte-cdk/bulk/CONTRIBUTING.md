# Contributing to the Kotlin Bulk CDK

Thank you for your interest in contributing to the Airbyte Kotlin Bulk CDK!

## Prerequisites

- **JDK 21** (Java Development Kit) or higher
- **Gradle** (uses the wrapper, no separate installation needed)

Everything else (the Kotlin compiler, KSP, Micronaut) comes from the Gradle build. See [Toolchain](#toolchain) for the pinned versions and the rules that go with them.

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

## Toolchain

The root `build.gradle` and `airbyte-cdk/bulk/gradle.properties` pin the toolchain. If this table disagrees with them, the build files win.

| Tool | Version | Where |
| --- | --- | --- |
| JDK | 21 | `sourceCompatibility`, `targetCompatibility` and Kotlin `jvmTarget` in the root `build.gradle` |
| Kotlin | 2.4.21 (K2 compiler) at language and API level 2.4 | `org.jetbrains.kotlin.jvm` plugin in the root `build.gradle`, `kotlin-bom` in `airbyte-cdk/bulk/build.gradle` |
| KSP | 2.3.10 (KSP2) | `com.google.devtools.ksp` plugin in the root `build.gradle` |
| Micronaut | 4.10.31 | `micronautVersion` in `airbyte-cdk/bulk/gradle.properties` |
| Gradle | 8.14.6 | wrapper |

KSP stays on 2.3.10 on purpose: 2.3.12 changed `effectiveJavaModifiers` and breaks `micronaut-inject-kotlin` before Micronaut 5.3.

### Incremental KSP processing is off

`ksp.incremental=false` in `airbyte-cdk/bulk/gradle.properties` is deliberate. With incremental processing on, KSP2 crashes Micronaut 4.10's `ConfigurationMetadataWriterVisitor` with a `KaInvalidLifetimeOwnerAccessException` ("PSI has changed since creation") whenever a `@ConfigurationProperties` bean sits next to declaration-free Kotlin files, such as the protoc-generated `*Kt.proto.kt` stubs in `bulk-cdk-core-base`. This is [micronaut-core#12677](https://github.com/micronaut-projects/micronaut-core/issues/12677); the fix shipped in Micronaut 5.2 and 5.3, not in 4.10. Incremental processing would save nothing here anyway, because Micronaut's processors are aggregating and every run is a full run. Leave the setting alone.

### Declare KSP and test dependencies per source set

Two toolchain changes removed implicit wiring that the build used to rely on:

- KSP2 no longer applies the `ksp` configuration to the other compilations of a module. `airbyte-cdk/bulk/build.gradle` and `airbyte-bulk-connector.gradle` declare `kspTest`, `kspTestFixtures` and `kspIntegrationTest` for `io.micronaut:micronaut-inject-kotlin`; a module that adds another source set must declare the matching `ksp<SourceSet>` entry itself.
- The Kotlin Gradle plugin (since 2.0.10) no longer propagates `implementation` dependencies into `testFixtures`, nor `testFixturesImplementation` into `test`. Declare `testFixturesImplementation` and `testImplementation` for every library those source sets use directly.

A missing `ksp<SourceSet>` entry does not fail compilation: the `@MicronautTest` beans of that source set vanish without a message and the tests fail later with `NoSuchBeanException`.

### Bean definitions are verified before tests run

The `verifyMicronautBeanDefinitions` task (one per source set, wired into `check` and every `Test` task) loads each KSP-generated `$Definition` class and fails the build if the JVM rejects one. Without it, Micronaut's service loader drops a definition that fails to load and the bean goes missing without a message; the failure surfaces later as a `NoSuchBeanException` at an unrelated injection point, or not at all when the bean is optional.

The known trigger is a Kotlin constructor that combines a default value with a primitive parameter on a bean, such as `class Foo(val retries: Int = 3)`: `micronaut-inject-kotlin` 4.8 through 4.10 emits bytecode for it that the JVM verifier rejects (micronaut-core #11407 and #11502, fixed in 5.2.15 by #13041). Until the Bulk CDK moves to Micronaut 5, give such a parameter a non-primitive type or drop the default and inject the value through configuration. The task tells you which class broke and why.

## Building and checking

```bash
# Build all modules
./gradlew :airbyte-cdk:bulk:bulkCdkBuild

# Run tests
./gradlew :airbyte-cdk:bulk:test
```

CI compiles with `-Werror` (`allWarningsAsErrors = isInCi()` in the root `build.gradle`), for Java and for the `main`, `test` and `testFixtures` Kotlin source sets. A local build does not, so a new warning only shows up after the push. Set `CI=true` to get the same result locally:

```bash
CI=true ./gradlew :airbyte-cdk:bulk:bulkCdkBuild --rerun-tasks
```

## IDE

Use IntelliJ IDEA 2025.1 or newer, where K2 mode is the default and the bundled Kotlin plugin understands language level 2.4. Older releases analyze the sources with the K1 front end and disagree with the compiler on 2.4 language features and on some inferred types. If you turned K2 mode off, turn it back on under Settings > Languages & Frameworks > Kotlin.

## Generating Documentation

The Kotlin Bulk CDK uses [Dokka](https://kotlinlang.org/docs/dokka-introduction.html) to generate API documentation from KDoc comments.

**Published Documentation**: The latest API documentation is available at https://airbyte-kotlin-cdk.vercel.app/

### Generate Documentation Locally

```bash
./gradlew :airbyte-cdk:bulk:dokkaGenerate
```

This generates HTML documentation in `airbyte-cdk/bulk/build/dokka/htmlMultiModule/`.

### View Generated Documentation

```bash
# macOS
open airbyte-cdk/bulk/build/dokka/htmlMultiModule/index.html

# Linux
xdg-open airbyte-cdk/bulk/build/dokka/htmlMultiModule/index.html
```

## More Information

For architecture, publishing, development workflow, and other details, see the [README](README.md).

For general Airbyte contribution guidelines, see the [main contributing guide](../../docs/contributing-to-airbyte/README.md).
