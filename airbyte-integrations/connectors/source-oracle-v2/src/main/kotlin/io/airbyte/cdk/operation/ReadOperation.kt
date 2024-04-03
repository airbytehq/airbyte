/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.operation

import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(property = CONNECTOR_OPERATION, value = "read")
@Requires(env = ["source"])
class ReadOperation : Operation {

    override val type = OperationType.READ

    override fun execute() {
        logger.info { "Performing READ operation." }
        // TODO: implement
    }
}
