/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import io.airbyte.cdk.AirbyteSourceRunner
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

object DynamoDbSource {
    @JvmStatic
    fun main(args: Array<String>) {
        log.info { "Starting source: DynamoDbSource" }
        AirbyteSourceRunner.run(*args)
    }
}
