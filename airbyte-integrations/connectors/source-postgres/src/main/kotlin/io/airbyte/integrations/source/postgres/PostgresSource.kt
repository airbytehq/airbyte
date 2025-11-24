/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.AirbyteSourceRunner
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File

private val log = KotlinLogging.logger {}

object PostgresSource {
    @JvmStatic
    fun main(args: Array<String>) {
        // TODO: Remove before merging
        try {
            args.forEachIndexed { index, arg ->
                log.info { "***$index $arg" }
                if (index in listOf(2, 4, 6)) {
                    log.info { (File(arg).readText()) }
                }
            }
        } catch (e: Exception) {
            log.error(e) { "Error during source execution" }
            throw e
        }
        AirbyteSourceRunner.run(*args)
    }
}
