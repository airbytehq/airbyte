/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import io.airbyte.cdk.AirbyteSourceRunner
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import kotlin.collections.forEachIndexed

private val log = KotlinLogging.logger {}

object DataGenSource {
    @JvmStatic
    fun main(args: Array<String>) {
        // TODO: Remove before merging
        args.forEachIndexed { index, arg ->
            log.info { "***$index $arg" }
            if (index in listOf(2, 4, 6)) {
                log.info { (File(arg).readText()) }
            }
        }

        log.info { "Starting source: DataGenSource" }
        AirbyteSourceRunner.run(*args)
    }
}
