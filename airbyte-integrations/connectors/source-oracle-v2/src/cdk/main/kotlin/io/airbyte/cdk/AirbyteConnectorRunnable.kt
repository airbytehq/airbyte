/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.airbyte.cdk.operation.Operation
import io.airbyte.cdk.operation.OperationExecutionException
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject

private val log = KotlinLogging.logger {}

/** [AirbyteConnectorRunner] tells Micronaut to use this [Runnable] as the entry point. */
class AirbyteConnectorRunnable : Runnable {

    @Value("\${micronaut.application.name}") lateinit var connectorName: String
    @Inject lateinit var operation: Operation

    override fun run() {
        log.info { "Executing ${operation.type} operation." }
        try {
            operation.execute()
        } catch (e: OperationExecutionException) {
            log.error(e) { "Failed ${operation.type} operation execution." }
            throw e
        } catch (e: Throwable) {
            log.error(e) { "Failed ${operation.type} operation execution." }
            throw OperationExecutionException(operation.type, cause = e)
        } finally {
            log.info { "Completed integration: $connectorName." }
        }
    }
}
