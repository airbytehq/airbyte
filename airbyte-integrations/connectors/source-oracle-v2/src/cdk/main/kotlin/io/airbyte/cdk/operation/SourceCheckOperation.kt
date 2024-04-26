/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.operation

import io.airbyte.cdk.command.ConfigurationFactory
import io.airbyte.cdk.command.ConfigurationJsonObjectBase
import io.airbyte.cdk.command.ConfigurationJsonObjectSupplier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.consumers.OutputConsumer
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.integrations.util.ApmTraceUtils
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.sql.SQLException
import org.apache.commons.lang3.exception.ExceptionUtils

private val log = KotlinLogging.logger {}

@Singleton
@Requires(property = CONNECTOR_OPERATION, value = "check")
@Requires(env = ["source"])
class SourceCheckOperation<T : ConfigurationJsonObjectBase>(
    val configJsonObjectSupplier: ConfigurationJsonObjectSupplier<T>,
    val configFactory: ConfigurationFactory<T, out SourceConfiguration>,
    val metadataQuerierFactory: MetadataQuerier.Factory,
    val outputConsumer: OutputConsumer,
) : Operation {

    override val type = OperationType.CHECK

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
                AirbyteTraceMessage()
                    .withType(AirbyteTraceMessage.Type.ERROR)
                    .withError(
                        AirbyteErrorTraceMessage()
                            .withFailureType(AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR)
                            .withMessage(message)
                            .withInternalMessage(e.toString())
                            .withStackTrace(ExceptionUtils.getStackTrace(e))
                    )
            )
            outputConsumer.accept(
                AirbyteConnectionStatus()
                    .withMessage(message)
                    .withStatus(AirbyteConnectionStatus.Status.FAILED)
            )
            log.info { "Config check failed." }
            return
        } catch (e: Exception) {
            log.debug(e) { "Exception while checking config." }
            ApmTraceUtils.addExceptionToTrace(e)
            outputConsumer.accept(
                AirbyteConnectionStatus()
                    .withMessage(String.format(COMMON_EXCEPTION_MESSAGE_TEMPLATE, e.message))
                    .withStatus(AirbyteConnectionStatus.Status.FAILED)
            )
            log.info { "Config check failed." }
            return
        }
        log.info { "Config check completed successfully." }
        outputConsumer.accept(
            AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        )
    }

    /**
     * Checks the validity of the provided config:
     * - by discovering the available tables,
     * - by querying at least one table successfully.
     */
    private fun connectionCheck(metadataQuerier: MetadataQuerier) {
        log.info { "Querying all table names in config schemas." }
        val tableNames: List<TableName> = metadataQuerier.tableNames()
        if (tableNames.isEmpty()) {
            throw RuntimeException("Discovered zero tables.")
        }
        log.info { "Discovered ${tableNames.size} table(s)." }
        for (table in tableNames) {
            try {
                metadataQuerier.columnMetadata(table)
            } catch (e: SQLException) {
                log.info {
                    "Query failed with code ${e.errorCode}, SQLState ${e.sqlState};" +
                        " will try to query another table instead."
                }
                log.debug(e) {
                    "Config check column metadata query for $table failed with exception."
                }
                continue
            }
            log.info { "Query successful." }
            return
        }
        throw RuntimeException("Unable to query any of the discovered table(s): $tableNames")
    }

    companion object {
        const val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
            "Could not connect with provided configuration. Error: %s"
    }
}
