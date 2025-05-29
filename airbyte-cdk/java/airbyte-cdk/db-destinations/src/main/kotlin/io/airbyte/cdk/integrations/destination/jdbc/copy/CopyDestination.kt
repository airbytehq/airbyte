/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility.emitConfigErrorTrace
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.github.oshai.kotlinlogging.KotlinLogging
import javax.sql.DataSource

private val LOGGER = KotlinLogging.logger {}

// TODO: Delete this class, this is only used in StarburstGalaxyDestination
abstract class CopyDestination : BaseConnector, Destination {
    /**
     * The default database schema field in the destination config is "schema". To change it, pass
     * the field name to the constructor.
     */
    private var schemaFieldName = "schema"

    constructor()

    constructor(schemaFieldName: String) {
        this.schemaFieldName = schemaFieldName
    }

    /**
     * A self contained method for writing a file to the persistence for testing. This method should
     * try to clean up after itself by deleting the file it creates.
     */
    @Throws(Exception::class) abstract fun checkPersistence(config: JsonNode?)

    abstract val nameTransformer: StandardNameTransformer

    abstract fun getDataSource(config: JsonNode?): DataSource

    abstract fun getDatabase(dataSource: DataSource?): JdbcDatabase

    abstract val sqlOperations: SqlOperations

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        try {
            checkPersistence(config)
        } catch (e: Exception) {
            LOGGER.error(e) { "Exception attempting to access the staging persistence: " }
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    """
    Could not connect to the staging persistence with the provided configuration. 
    ${e.message}
    """.trimIndent()
                )
        }

        val dataSource = getDataSource(config)

        try {
            val database = getDatabase(dataSource)
            val nameTransformer = nameTransformer
            val outputSchema = nameTransformer.convertStreamName(config[schemaFieldName].asText())
            performCreateInsertTestOnDestination(outputSchema, database, nameTransformer)

            return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        } catch (ex: ConnectionErrorException) {
            LOGGER.info { "Exception while checking connection: $ex" }
            val message = getErrorMessage(ex.stateCode, ex.errorCode, ex.exceptionMessage, ex)
            emitConfigErrorTrace(ex, message)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(message)
        } catch (e: Exception) {
            LOGGER.error(e) { "Exception attempting to connect to the warehouse: " }
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    """
    Could not connect to the warehouse with the provided configuration. 
    ${e.message}
    """.trimIndent()
                )
        } finally {
            try {
                close(dataSource)
            } catch (e: Exception) {
                LOGGER.warn(e) { "Unable to close data source." }
            }
        }
    }

    @Throws(Exception::class)
    protected fun performCreateInsertTestOnDestination(
        outputSchema: String,
        database: JdbcDatabase,
        nameTransformer: NamingConventionTransformer
    ) {
        AbstractJdbcDestination.Companion.attemptTableOperations(
            outputSchema,
            database,
            nameTransformer,
            sqlOperations,
            true
        )
    }

    companion object {}
}
