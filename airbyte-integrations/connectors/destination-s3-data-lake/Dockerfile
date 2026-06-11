# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom

# Self-contained multi-stage build for the destination-s3-data-lake connector.
#
# Built by Kaniko via the HudHud cicd-reusable-workflows. Kaniko builds only from a
# Dockerfile + git context, so the Gradle build must happen INSIDE the build (builder
# stage below). The Kaniko build context is the repository root, so paths here are
# repo-root relative.

# ---------------------------------------------------------------------------
# Builder stage: compile the connector distribution tar via Gradle.
# ---------------------------------------------------------------------------
# Use the official Gradle image (matches the wrapper's pinned 8.14) so the ~130 MB Gradle
# distribution is already present — we invoke `gradle` instead of `./gradlew` to skip the
# per-build distribution download. Runs as root, so `COPY . .` below needs no chown.
FROM gradle:8.14-jdk21 AS builder

# Airbyte's root settings.gradle includes every connector project and the full local
# CDK, and build.gradle's `allprojects {}` block configures all of them. Configuring
# the whole monorepo needs more heap than Gradle's default, so bump it to avoid OOM.
ENV GRADLE_OPTS="-Dorg.gradle.jvmargs=-Xmx4g -Dorg.gradle.daemon=false -Dorg.gradle.welcome=never"

WORKDIR /build

# Copy the whole repo. Kaniko already fetches the full repo as context, and copying
# everything avoids the root settings.gradle failing on partially-present projects.
# This connector is a Bulk-CDK connector with `cdk = 'local'`, so the in-image build
# compiles against the local airbyte-cdk/bulk source (which COPY . . brings in).
COPY . .

RUN gradle :airbyte-integrations:connectors:destination-s3-data-lake:distTar --no-daemon

# ---------------------------------------------------------------------------
# Runtime stage: package the dist on top of the Airbyte java connector base.
# Mirrors docker-images/Dockerfile.java-connector.
# ---------------------------------------------------------------------------
FROM docker.io/airbyte/java-connector-base:2.0.1@sha256:ec89bd1a89e825514dd2fc8730ba299a3ae1544580a078df0e35c5202c2085b3

# The base image defaults to the non-root `airbyte` user. Switch to root for the
# privileged setup below (chmod/chown, extracting + removing root-owned COPY'd files);
# we drop back to `airbyte` at the end.
USER root

# Set permissions for files provided by the base image
RUN chmod +x /airbyte/base.sh /airbyte/javabase.sh && \
    chown airbyte:airbyte /airbyte/base.sh /airbyte/javabase.sh /airbyte/dd-java-agent.jar

ENV AIRBYTE_ENTRYPOINT="/airbyte/base.sh"
ENV APPLICATION="destination-s3-data-lake"

# Add the connector dist tar and extract it. distTar produces exactly one *.tar in
# the distributions dir; its base name depends on Gradle's archive naming, so match
# it by glob rather than hardcoding.
COPY --from=builder /build/airbyte-integrations/connectors/destination-s3-data-lake/build/distributions/ /tmp/distributions/
RUN set -e; \
    TAR="$(ls /tmp/distributions/*.tar | head -n1)" && \
    tar xf "$TAR" --strip-components=1 -C /airbyte && \
    rm -rf /tmp/distributions && \
    chown -R airbyte:airbyte /airbyte

# Set the non-root user
USER airbyte

# Set entrypoint
ENTRYPOINT ["/airbyte/base.sh"]
