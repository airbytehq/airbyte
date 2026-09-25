/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import io.airbyte.cdk.AirbyteSourceRunner
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

object SlackSource {
    @JvmStatic
    fun main(args: Array<String>) {
        log.info { "Starting source: SlackSource" }
        AirbyteSourceRunner.run(*args)
    }
}
