/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.AirbyteSourceRunner
import java.lang.Thread.sleep

object MySqlSource {
    @JvmStatic
    fun main(args: Array<String>) {
        sleep(100_000)
        AirbyteSourceRunner.run(*args)
    }
}
