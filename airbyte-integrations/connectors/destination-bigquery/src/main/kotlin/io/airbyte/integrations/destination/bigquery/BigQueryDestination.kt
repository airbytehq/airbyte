/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.AirbyteDestinationRunner
import io.airbyte.cdk.load.command.aws.AwsToolkitConstants

/**
 * This is needed because the GCS client is, under the hood, using the S3Client.
 *
 * And the S3Client depends on the AWS environment - we're not actually _using the assume role
 * stuff, but the wiring needs to be satisfied.
 */
val additionalMicronautEnvs = listOf(AwsToolkitConstants.MICRONAUT_ENVIRONMENT)

fun main(args: Array<String>) {
    AirbyteDestinationRunner.run(*args, additionalMicronautEnvs = additionalMicronautEnvs)
}
