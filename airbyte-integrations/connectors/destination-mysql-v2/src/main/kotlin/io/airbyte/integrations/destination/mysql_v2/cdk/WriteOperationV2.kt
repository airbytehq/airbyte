/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.cdk

import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.dataflow.DestinationLifecycle
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/**
 * Write operation implementation for MySQL v2 destination.
 *
 * This class serves as a minimal adapter between the CDK's operation framework
 * and the destination lifecycle. It delegates all the actual work to the
 * [DestinationLifecycle] which manages the entire sync process.
 */
@Primary
@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class WriteOperationV2(
    private val destinationLifecycle: DestinationLifecycle,
) : Operation {
    private val log = KotlinLogging.logger {}

    override fun execute() {
        log.info { "Starting MySQL v2 write operation..." }
        destinationLifecycle.run()
        log.info { "MySQL v2 write operation completed successfully" }
    }
}
