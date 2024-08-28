/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.check

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationJsonObjectBase
import io.airbyte.cdk.command.ConfigurationJsonObjectSupplier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(property = Operation.PROPERTY, value = "check")
@Requires(env = ["source"])
class CheckOperation<T : ConfigurationJsonObjectBase>(
    val configJsonObjectSupplier: ConfigurationJsonObjectSupplier<T>,
    val configFactory: SourceConfigurationFactory<T, out SourceConfiguration>,
    val metadataQuerierFactory: MetadataQuerier.Factory<SourceConfiguration>,
    val outputConsumer: OutputConsumer,
    val exceptionHandler: ExceptionHandler,
) : Operation {
    private val log = KotlinLogging.logger {}

    /** Wraps all checks in exception handling because CHECK must always exit cleanly. */
    override fun execute() {
        try {
            log.info { "Parsing connector configuration JSON object." }
            val pojo: T = configJsonObjectSupplier.get()
            log.info { "Building internal connector configuration object." }
            val config: SourceConfiguration = configFactory.make(pojo)
            log.info { "Connecting for config check." }
            metadataQuerierFactory.session(config).use {
                connectionCheck(it)
                it.extraChecks()
            }
        } catch (e: Exception) {
            log.debug(e) { "Exception while checking config." }
            val errorTraceMessage: AirbyteErrorTraceMessage = exceptionHandler.handle(e)
            errorTraceMessage.failureType = AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR
            outputConsumer.accept(errorTraceMessage)
            val connectionStatusMessage: String =
                String.format(COMMON_EXCEPTION_MESSAGE_TEMPLATE, errorTraceMessage.message)
            outputConsumer.accept(
                AirbyteConnectionStatus()
                    .withMessage(connectionStatusMessage)
                    .withStatus(AirbyteConnectionStatus.Status.FAILED),
            )
            log.info { "Config check failed." }
            return
        }
        log.info { "Config check completed successfully." }
        outputConsumer.accept(
            AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED),
        )
    }

    /**
     * Checks the validity of the provided config:
     * - by discovering the available tables,
     * - by querying at least one table successfully.
     */
    private fun connectionCheck(metadataQuerier: MetadataQuerier) {
        log.info { "Querying all stream names and namespaces." }
        var n = 0
        val namespaces: List<String?> = listOf<String?>(null) + metadataQuerier.streamNamespaces()
        for (namespace in namespaces) {
            for (name in metadataQuerier.streamNames(namespace)) {
                try {
                    metadataQuerier.fields(name, namespace)
                } catch (e: Exception) {
                    log.info(e) {
                        "Query failed on stream '$name' in '${namespace ?: ""}': ${e.message}"
                    }
                    n++
                    continue
                }
                log.info { "Query successful on stream '$name' in '${namespace ?: ""}'." }
                return
            }
        }
        if (n == 0) {
            throw ConfigErrorException("Discovered zero tables.")
        } else {
            throw ConfigErrorException("Unable to query any of the $n discovered table(s).")
        }
    }

    companion object {
        const val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
            "Could not connect with provided configuration. Error: %s"
    }
}
