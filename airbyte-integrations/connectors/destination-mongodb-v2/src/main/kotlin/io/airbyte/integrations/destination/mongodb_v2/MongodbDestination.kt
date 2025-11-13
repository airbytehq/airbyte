/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2

import io.airbyte.cdk.AirbyteDestinationRunner
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

object MongodbDestination {
    @JvmStatic
    fun main(args: Array<String>) {
        logger.info { "Starting destination-mongodb-v2" }
        AirbyteDestinationRunner.run(*args)
        logger.info { "Completed destination-mongodb-v2" }
    }
}
