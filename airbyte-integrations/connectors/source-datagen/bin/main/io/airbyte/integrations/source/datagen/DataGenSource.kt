/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import io.airbyte.cdk.AirbyteSourceRunner
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

object DataGenSource {
    @JvmStatic
    fun main(args: Array<String>) {
        log.info { "Starting source: DataGenSource" }
        AirbyteSourceRunner.run(*args)
    }
}
