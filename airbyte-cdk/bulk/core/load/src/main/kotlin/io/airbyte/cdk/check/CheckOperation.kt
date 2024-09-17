/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.check

import io.airbyte.cdk.Operation
import io.airbyte.cdk.output.ExceptionHandler
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(property = Operation.PROPERTY, value = "check")
@Requires(env = ["destination"])
class CheckOperation(
    private val destination: DestinationCheck,
    private val exceptionHandler: ExceptionHandler,
) : Operation {
    override fun execute() {
        try {
            destination.check()
        } catch (e: Exception) {
            exceptionHandler.handle(e)
        } finally {
            destination.cleanup()
        }
    }
}
