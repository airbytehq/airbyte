/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import io.airbyte.cdk.AirbyteDestinationRunner
import net.snowflake.client.log.SLF4JLogger

fun main(args: Array<String>) {
    // Force the Snowflake JDBC client to use SLF4J so that we can control the output
    System.setProperty("net.snowflake.jdbc.loggerImpl", SLF4JLogger::class.java.name)

    AirbyteDestinationRunner.run(*args)
}
