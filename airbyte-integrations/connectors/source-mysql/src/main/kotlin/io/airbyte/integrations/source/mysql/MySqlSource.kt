/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.AirbyteSourceRunner
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File

private val log = KotlinLogging.logger {}
object MySqlSource {
    @JvmStatic
    fun main(args: Array<String>) {
        args.forEachIndexed { index, arg ->
            log.info { "***$index $arg" }
            if (index in listOf(2, 4, 6)) {
                log.info { (File(arg).readText()) }
            }

        }
        AirbyteSourceRunner.run(*args)
    }
}
