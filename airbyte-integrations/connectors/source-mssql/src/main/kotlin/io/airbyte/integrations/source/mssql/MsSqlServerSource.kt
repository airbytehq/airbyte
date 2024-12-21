/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.AirbyteSourceRunner
import io.github.oshai.kotlinlogging.KotlinLogging

object MsSqlServerSource {
    private val log = KotlinLogging.logger {}

    @JvmStatic
    fun main(args: Array<String>) {
        log.info { "SGX parameters = ${args.toList()}" }
        AirbyteSourceRunner.run(*args)
    }
}
