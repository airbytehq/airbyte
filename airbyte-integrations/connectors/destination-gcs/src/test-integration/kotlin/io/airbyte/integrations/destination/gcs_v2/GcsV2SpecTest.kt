/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.load.spec.SpecTest

/**
 * Snapshot test for the generated connectionSpecification. On the FIRST run (with empty/missing
 * expected-spec-{oss,cloud}.json) the CDK base writes the actual spec to those files and the assert
 * fails; re-run to make it pass, then commit the generated files. Requires NO GCS credentials — it
 * only runs the connector `spec` command via the non-docker CliRunner.
 *
 * We register the "aws" Micronaut env (same as the connector's real runtime) because the storage
 * client is built through S3ClientFactory; it is harmless for `spec`.
 */
class GcsV2SpecTest : SpecTest(additionalMicronautEnvs = GcsV2Destination.additionalMicronautEnvs)
