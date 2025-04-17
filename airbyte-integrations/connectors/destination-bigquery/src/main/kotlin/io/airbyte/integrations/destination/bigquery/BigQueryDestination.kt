/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQueryException
import io.airbyte.cdk.AirbyteDestinationRunner
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler.Companion.addThrowableForDeinterpolation
import io.airbyte.cdk.load.command.aws.AwsToolkitConstants

val additionalMicronautEnvs = listOf(AwsToolkitConstants.MICRONAUT_ENVIRONMENT)

fun main(args: Array<String>) {
    val additionalMicronautEnvs = listOf(AwsToolkitConstants.MICRONAUT_ENVIRONMENT)
    addThrowableForDeinterpolation(BigQueryException::class.java)
    AirbyteDestinationRunner.run(*args, additionalMicronautEnvs = additionalMicronautEnvs)
}
