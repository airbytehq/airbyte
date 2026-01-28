/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.dataflow.DestinationLifecycle
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class WriteOperation(
    private val destinationLifecycle: DestinationLifecycle,
) : Operation {
    private val log = KotlinLogging.logger {}

    override fun execute() {
        log.info { "Running destination write..." }
        destinationLifecycle.run()
        log.info { "Destination write complete." }
    }
}
