/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.operation

import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(property = CONNECTOR_OPERATION, value = "write")
@Requires(env = ["destination"])
class WriteOperation : Operation {

    override val type = OperationType.WRITE

    override fun execute() {
        logger.info { "Performing WRITE operation." }
        // TODO: implement
    }
}
