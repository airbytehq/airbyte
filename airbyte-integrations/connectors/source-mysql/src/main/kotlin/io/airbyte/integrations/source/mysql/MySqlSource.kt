/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.AirbyteSourceRunner
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

object MySqlSource {
    @JvmStatic
    fun main(args: Array<String>) {
        AirbyteSourceRunner.run(*args)
    }
}
