/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import io.airbyte.cdk.AirbyteSourceRunner
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

object BigQuerySource {
    @JvmStatic
    fun main(args: Array<String>) {
        log.info { "Starting source: BigQuerySource" }
        AirbyteSourceRunner.run(*args)
    }
}
