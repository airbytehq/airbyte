/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.OutputConsumer
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Provider

private val log = KotlinLogging.logger {}

/** [AirbyteConnectorRunner] tells Micronaut to use this [Runnable] as the entry point. */
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class AirbyteConnectorRunnable : Runnable {
    @Value("\${airbyte.connector.metadata.docker-repository}") lateinit var connectorName: String

    @Inject lateinit var operationProvider: Provider<Operation>

    @Value("\${airbyte.connector.operation}") lateinit var operationName: String

    @Inject lateinit var outputConsumer: OutputConsumer

    @Inject lateinit var exceptionHandler: ExceptionHandler

    override fun run() {
        var operation: Operation? = null
        try {
            try {
                operation = operationProvider.get()!!
            } catch (e: Throwable) {
                throw ConfigErrorException("Failed to initialize connector operation", e)
            }
            log.info { "Executing ${operation::class} operation." }
            operation.execute()
        } catch (e: Throwable) {
            log.error(e) {
                if (operation == null) {
                    "Failed connector operation initialization."
                } else {
                    "Failed ${operation::class} operation execution."
                }
            }
            handleOperationException(e)
        } finally {
            log.info { "Flushing output consumer prior to shutdown." }
            outputConsumer.close()
            log.info { "Completed integration: $connectorName." }
        }
    }

    private fun handleOperationException(e: Throwable) {
        if (operationName == "check") {
            // During check, we don't fail the command on uncaught error. We assume the check as
            // failed and return a trace + a connection status message.
            val exception: Throwable? =
                if (e.message == "Failed to initialize connector operation") e.cause else e
            val (errorTraceMessage, connectionStatusMessage) =
                exceptionHandler.handleCheckFailure(exception ?: e)
            outputConsumer.accept(errorTraceMessage)
            outputConsumer.accept(connectionStatusMessage)
        } else {
            outputConsumer.accept(exceptionHandler.handle(e))
            throw e
        }
    }
}
