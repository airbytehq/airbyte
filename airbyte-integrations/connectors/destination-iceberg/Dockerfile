# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom

# Self-contained multi-stage build for the HudHud destination-iceberg connector.
#
# Unlike Airbyte's upstream pipeline (which pre-builds the dist tar on the host and
# then runs docker-images/Dockerfile.java-connector), this image is built by Kaniko
# via the HudHud cicd-reusable-workflows. Kaniko builds only from a Dockerfile + git
# context, so the Gradle build must happen INSIDE the build (builder stage below).
#
# The Kaniko build context is the repository root, so paths here are repo-root relative.

# ---------------------------------------------------------------------------
# Builder stage: compile the connector distribution tar via Gradle.
# ---------------------------------------------------------------------------
FROM eclipse-temurin:21-jdk AS builder

# Airbyte's root settings.gradle includes every connector project and the full local
# CDK, and build.gradle's `allprojects {}` block configures all of them. Configuring
# the whole monorepo needs more heap than Gradle's default, so bump it to avoid OOM.
ENV GRADLE_OPTS="-Dorg.gradle.jvmargs=-Xmx4g -Dorg.gradle.daemon=false -Dorg.gradle.welcome=never"

WORKDIR /build

# Copy the whole repo. Kaniko already fetches the full repo as context, and copying
# everything avoids the root settings.gradle failing on partially-present connector
# projects. Gradle is lazy, so only the iceberg module + its deps actually compile.
# The connector sets useLocalCdk = false, so the CDK is pulled from remote Maven
# (airbyte.mycloudrepo.io, public) rather than the local airbyte-cdk/ source tree.
COPY . .

RUN ./gradlew :airbyte-integrations:connectors:destination-iceberg:distTar --no-daemon

# ---------------------------------------------------------------------------
# Runtime stage: package the dist on top of the Airbyte java connector base.
# Mirrors docker-images/Dockerfile.java-connector.
# ---------------------------------------------------------------------------
FROM docker.io/airbyte/java-connector-base:2.0.0@sha256:5a1a21c75c5e1282606de9fa539ba136520abe2fbd013058e988bb0297a9f454

# The base image defaults to the non-root `airbyte` user. Switch to root for the
# privileged setup below (chmod/chown, extracting + removing root-owned COPY'd files);
# we drop back to `airbyte` at the end.
USER root

# Set permissions for files provided by the base image
RUN chmod +x /airbyte/base.sh /airbyte/javabase.sh && \
    chown airbyte:airbyte /airbyte/base.sh /airbyte/javabase.sh /airbyte/dd-java-agent.jar

ENV AIRBYTE_ENTRYPOINT="/airbyte/base.sh"
ENV APPLICATION="destination-iceberg"

# Add the connector dist tar and extract it. distTar produces exactly one *.tar in
# the distributions dir; its base name depends on Gradle's archive naming, so match
# it by glob rather than hardcoding (handles destination-iceberg.tar / airbyte-app.tar /
# any versioned name).
COPY --from=builder /build/airbyte-integrations/connectors/destination-iceberg/build/distributions/ /tmp/distributions/
RUN set -e; \
    TAR="$(ls /tmp/distributions/*.tar | head -n1)" && \
    tar xf "$TAR" --strip-components=1 -C /airbyte && \
    rm -rf /tmp/distributions && \
    chown -R airbyte:airbyte /airbyte

# Set the non-root user
USER airbyte

# Set entrypoint
ENTRYPOINT ["/airbyte/base.sh"]
