/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.check

import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.*
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.ApmTraceUtils
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.sql.SQLException
import org.apache.commons.lang3.exception.ExceptionUtils

@Singleton
@Requires(property = Operation.PROPERTY, value = "check")
@Requires(env = ["source"])
class CheckOperation<T : ConfigurationJsonObjectBase>(
    val configJsonObjectSupplier: ConfigurationJsonObjectSupplier<T>,
    val configFactory: SourceConfigurationFactory<T, out SourceConfiguration>,
    val metadataQuerierFactory: MetadataQuerier.Factory<SourceConfiguration>,
    val outputConsumer: OutputConsumer,
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
            metadataQuerierFactory.session(config).use { connectionCheck(it) }
        } catch (e: SQLException) {
            log.debug(e) { "SQLException while checking config." }
            val message: String =
                listOfNotNull(
                        e.sqlState?.let { "State code: $it" },
                        e.errorCode.takeIf { it != 0 }?.let { "Error code: $it" },
                        e.message?.let { "Message: $it" },
                    )
                    .joinToString(separator = "; ")
            ApmTraceUtils.addExceptionToTrace(e)
            outputConsumer.accept(
                AirbyteErrorTraceMessage()
                    .withFailureType(AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR)
                    .withMessage(message)
                    .withInternalMessage(e.toString())
                    .withStackTrace(ExceptionUtils.getStackTrace(e)),
            )
            outputConsumer.accept(
                AirbyteConnectionStatus()
                    .withMessage(message)
                    .withStatus(AirbyteConnectionStatus.Status.FAILED),
            )
            log.info { "Config check failed." }
            return
        } catch (e: Exception) {
            log.debug(e) { "Exception while checking config." }
            ApmTraceUtils.addExceptionToTrace(e)
            outputConsumer.acceptTraceOnConfigError(e)
            outputConsumer.accept(
                AirbyteConnectionStatus()
                    .withMessage(String.format(COMMON_EXCEPTION_MESSAGE_TEMPLATE, e.message))
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
            throw RuntimeException("Discovered zero tables.")
        } else {
            throw RuntimeException("Unable to query any of the $n discovered table(s).")
        }
    }

    companion object {
        const val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
            "Could not connect with provided configuration. Error: %s"
    }
}
