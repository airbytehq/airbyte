/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.ApmTraceUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject

private val log = KotlinLogging.logger {}

/** [AirbyteConnectorRunner] tells Micronaut to use this [Runnable] as the entry point. */
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class AirbyteConnectorRunnable : Runnable {
    @Value("\${airbyte.connector.metadata.docker-repository}") lateinit var connectorName: String

    @Inject lateinit var operation: Operation

    @Inject lateinit var outputConsumer: OutputConsumer

    override fun run() {
        log.info { "Executing ${operation::class} operation." }
        try {
            operation.execute()
        } catch (e: Throwable) {
            log.error(e) { "Failed ${operation::class} operation execution." }
            ApmTraceUtils.addExceptionToTrace(e)
            outputConsumer.acceptTraceOnConfigError(e)
            throw e
        } finally {
            log.info { "Flushing output consumer prior to shutdown." }
            outputConsumer.close()
            log.info { "Completed integration: $connectorName." }
        }
    }
}
