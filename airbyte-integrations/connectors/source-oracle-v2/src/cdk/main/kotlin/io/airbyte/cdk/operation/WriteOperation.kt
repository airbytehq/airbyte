/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.operation

import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(property = CONNECTOR_OPERATION, value = "write")
@Requires(env = ["destination"])
class WriteOperation : Operation {

    override val type = OperationType.WRITE

    override fun execute() {
        // TODO: implement
    }
}
