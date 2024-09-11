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
    // What is the purpose of this DestinationCheck interface?
    // If CheckOperation is just a stub for now, then it shouldn't exist.
    // If it's not just a stub, then its purpose is very much not clear to me, fwiw.
    private val destination: DestinationCheck,
    private val exceptionHandler: ExceptionHandler,
) : Operation {
    override fun execute() {
        try {
            destination.check()
        } catch (e: Exception) {
            // The output of the ExceptionHandler needs to be fed to an OutputConsumer.
            exceptionHandler.handle(e)
        } finally {
            destination.cleanup()
        }
    }
}
