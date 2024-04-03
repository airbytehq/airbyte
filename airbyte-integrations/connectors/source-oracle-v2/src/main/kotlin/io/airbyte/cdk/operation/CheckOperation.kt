/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.operation

import io.airbyte.cdk.command.ConnectorConfigurationSupplier
import io.airbyte.cdk.command.SourceConnectorConfiguration
import io.airbyte.cdk.consumers.OutputConsumer
import io.airbyte.cdk.integrations.util.ApmTraceUtils
import io.airbyte.cdk.jdbc.MetadataQuerier
import io.airbyte.cdk.jdbc.SourceOperations
import io.airbyte.cdk.jdbc.TableName
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.sql.SQLException
import org.apache.commons.lang3.exception.ExceptionUtils

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(property = CONNECTOR_OPERATION, value = "check")
class CheckOperation(
    val configSupplier: ConnectorConfigurationSupplier<SourceConnectorConfiguration>,
    val sourceOperations: SourceOperations,
    val metadataQuerier: MetadataQuerier,
    val outputConsumer: OutputConsumer,
) : Operation, AutoCloseable {

    override val type = OperationType.CHECK

    /** Wraps [doCheck] in exception handling because CHECK must always exit cleanly. */
    override fun execute() {
        logger.info { "Performing CHECK operation." }
        try {
            doCheck()
            // TODO: check that the exception handling below is correct.
        } catch (e: SQLException) {
            logger.debug(e) { "SQLException while checking config." }
            val message: String = listOfNotNull(
                e.sqlState?.let { "State code: $it" },
                e.errorCode.takeIf { it != 0 }?.let { "Error code: $it" },
                e.message?.let { "Message: $it" },
            ).joinToString(separator = "; ")
            ApmTraceUtils.addExceptionToTrace(e)
            outputConsumer.accept(AirbyteMessage()
                .withType(AirbyteMessage.Type.TRACE)
                .withTrace(AirbyteTraceMessage()
                    .withType(AirbyteTraceMessage.Type.ERROR)
                    .withError(AirbyteErrorTraceMessage()
                        .withFailureType(AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR)
                        .withMessage(message)
                        .withInternalMessage(e.toString())
                        .withStackTrace(ExceptionUtils.getStackTrace(e)))))
            outputConsumer.accept(AirbyteMessage()
                .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                .withConnectionStatus(AirbyteConnectionStatus()
                    .withMessage(message)
                    .withStatus(AirbyteConnectionStatus.Status.FAILED)))
            logger.info { "Config check failed." }
            return
        } catch (e: Exception) {
            logger.debug (e) { "Exception while checking config." }
            ApmTraceUtils.addExceptionToTrace(e)
            outputConsumer.accept(AirbyteMessage()
                .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                .withConnectionStatus(AirbyteConnectionStatus()
                    .withMessage(String.format(COMMON_EXCEPTION_MESSAGE_TEMPLATE, e.message))
                    .withStatus(AirbyteConnectionStatus.Status.FAILED)))
            logger.info { "Config check failed." }
            return
        }
        logger.info { "Config check completed successfully." }
        outputConsumer.accept(AirbyteMessage()
            .withType(AirbyteMessage.Type.CONNECTION_STATUS)
            .withConnectionStatus(AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)))
    }

    override fun close() {
        metadataQuerier.close()
    }

    /**
     * Checks the validity of the provided config:
     * - by completely parsing it,
     * - by opening a connection,
     * - by discovering the available tables,
     * - by querying at least one table successfully.
     */
    private fun doCheck() {
        logger.info { "Validating config internal consistency." }
        configSupplier.get()
        logger.info { "Connecting for config check, querying all table names in config schemas." }
        val tableNames: List<TableName> = metadataQuerier.tableNames()
        logger.info { "Discovered ${tableNames.size} table(s)." }
        for (table in tableNames) {
            val sql: String = sourceOperations.selectStarFromTableLimit0(table)
            logger.info { "Querying $sql for config check." }
            try {
                metadataQuerier.columnMetadata(table, sql)
            } catch (e: SQLException) {
                logger.info {
                    "Query failed with code ${e.errorCode}, SQLState ${e.sqlState};" +
                        " will try to query another table instead."
                }
                logger.debug(e) { "Config check query $sql failed with exception." }
                continue
            }
            logger.info { "Query successful." }
            return
        }
        throw RuntimeException("Unable to query any of the discovered table(s): $tableNames")
    }

    companion object {
        const val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
            "Could not connect with provided configuration. Error: %s"
    }
}
