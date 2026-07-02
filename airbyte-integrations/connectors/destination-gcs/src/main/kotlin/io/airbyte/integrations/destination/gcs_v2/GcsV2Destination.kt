/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.AirbyteDestinationRunner
import io.airbyte.cdk.load.command.aws.AwsToolkitConstants

/**
 * Mirror of S3V2Destination.
 *
 * CRITICAL: this registers the "aws" Micronaut environment even though this is a GCS connector. It
 * is REQUIRED, not vestigial: [io.airbyte.cdk.load.file.gcs.GcsClientFactory] builds the storage
 * client via [io.airbyte.cdk.load.file.s3.S3ClientFactory] (HMAC over storage.googleapis.com), and
 * destination-bigquery — the existing production consumer of legacy-task-load-gcs — does exactly
 * the same. There is no GcsToolkitConstants env. The AWS beans are @Secondary / property-gated, so
 * no AWS-specific config is required at runtime beyond what GcsClientFactory synthesizes from the
 * HMAC credentials.
 */
class GcsV2Destination {
    companion object {
        val additionalMicronautEnvs = listOf(AwsToolkitConstants.MICRONAUT_ENVIRONMENT)

        @JvmStatic
        fun main(args: Array<String>) {
            AirbyteDestinationRunner.run(*args, additionalMicronautEnvs = additionalMicronautEnvs)
        }
    }
}
