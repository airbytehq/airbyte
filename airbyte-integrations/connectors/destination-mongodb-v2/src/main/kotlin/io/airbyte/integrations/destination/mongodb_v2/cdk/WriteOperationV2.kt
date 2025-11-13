/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.cdk

import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.dataflow.DestinationLifecycle
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Primary
@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class WriteOperationV2(
    private val destinationLifecycle: DestinationLifecycle,
) : Operation {
    private val log = KotlinLogging.logger {}

    override fun execute() {
        log.info { "Running MongoDB destination pipeline..." }
        destinationLifecycle.run()
        log.info { "MongoDB destination pipeline complete" }
    }
}
