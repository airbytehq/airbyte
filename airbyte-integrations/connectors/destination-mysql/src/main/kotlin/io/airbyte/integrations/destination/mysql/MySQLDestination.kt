/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.factory.DataSourceFactory
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination
import io.airbyte.cdk.integrations.destination.PropertyNameSimplifyingDataTransformer
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.map.MoreMaps
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationV1V2Migrator
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.mysql.typing_deduping.MysqlDestinationHandler
import io.airbyte.integrations.destination.mysql.typing_deduping.MysqlSqlGenerator
import io.airbyte.integrations.destination.mysql.typing_deduping.MysqlV1V2Migrator
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import java.sql.SQLSyntaxErrorException
import java.util.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class MySQLDestination :
    AbstractJdbcDestination<MinimumDestinationState>(
        DRIVER_CLASS,
        MySQLNameTransformer(),
        MySQLSqlOperations()
    ),
    Destination {
    override val configSchemaKey: String
        get() = JdbcUtils.DATABASE_KEY

    override fun check(config: JsonNode): AirbyteConnectionStatus {
        val dataSource = getDataSource(config)
        try {
            val database = getDatabase(dataSource)
            val mySQLSqlOperations = sqlOperations as MySQLSqlOperations

            val outputSchema: String =
                namingResolver.getIdentifier(config[JdbcUtils.DATABASE_KEY].asText())
            attemptTableOperations(
                outputSchema,
                database,
                namingResolver,
                mySQLSqlOperations,
                false
            )

            mySQLSqlOperations.verifyLocalFileEnabled(database)

            val compatibility = mySQLSqlOperations.isCompatibleVersion(database)
            if (!compatibility.isCompatible) {
                throw RuntimeException(
                    String.format(
                        "Your MySQL version %s is not compatible with Airbyte",
                        compatibility.version
                    )
                )
            }

            return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        } catch (e: ConnectionErrorException) {
            val message =
                ErrorMessage.getErrorMessage(e.stateCode, e.errorCode, e.exceptionMessage, e)
            AirbyteTraceMessageUtility.emitConfigErrorTrace(e, message)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(message)
        } catch (e: Exception) {
            LOGGER.error("Exception while checking connection: ", e)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    """
                    Could not connect with provided configuration. 
                    ${e.message}
                    """.trimIndent()
                )
        } finally {
            try {
                DataSourceFactory.close(dataSource)
            } catch (e: Exception) {
                LOGGER.warn("Unable to close data source.", e)
            }
        }
    }

    public override fun getDefaultConnectionProperties(config: JsonNode): Map<String, String> {
        return if (JdbcUtils.useSsl(config)) {
            DEFAULT_SSL_JDBC_PARAMETERS
        } else {
            DEFAULT_JDBC_PARAMETERS
        }
    }

    override fun toJdbcConfig(config: JsonNode): JsonNode {
        val jdbcUrl =
            String.format(
                "jdbc:mysql://%s:%s",
                config[JdbcUtils.HOST_KEY].asText(),
                config[JdbcUtils.PORT_KEY].asText()
            )

        val configBuilder =
            ImmutableMap.builder<Any, Any>()
                .put(JdbcUtils.USERNAME_KEY, config[JdbcUtils.USERNAME_KEY].asText())
                .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl)

        if (config.has(JdbcUtils.PASSWORD_KEY)) {
            configBuilder.put(JdbcUtils.PASSWORD_KEY, config[JdbcUtils.PASSWORD_KEY].asText())
        }
        if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
            configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config[JdbcUtils.JDBC_URL_PARAMS_KEY])
        }

        return Jsons.jsonNode(configBuilder.build())
    }

    override fun getSqlGenerator(config: JsonNode): JdbcSqlGenerator {
        return MysqlSqlGenerator()
    }

    override fun getDestinationHandler(
        databaseName: String,
        database: JdbcDatabase,
        rawTableSchema: String
    ): JdbcDestinationHandler<MinimumDestinationState> {
        return MysqlDestinationHandler(database, rawTableSchema)
    }

    override fun getMigrations(
        database: JdbcDatabase,
        databaseName: String,
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<MinimumDestinationState>
    ): List<Migration<MinimumDestinationState>> {
        return emptyList()
    }

    override fun getV1V2Migrator(
        database: JdbcDatabase,
        databaseName: String
    ): DestinationV1V2Migrator {
        return MysqlV1V2Migrator(database)
    }

    override fun getDataTransformer(
        parsedCatalog: ParsedCatalog?,
        defaultNamespace: String?
    ): StreamAwareDataTransformer {
        return PropertyNameSimplifyingDataTransformer()
    }

    override val isV2Destination: Boolean
        get() = true

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(MySQLDestination::class.java)
        val DRIVER_CLASS: String = DatabaseDriver.MYSQL.driverClassName

        @JvmField
        val DEFAULT_JDBC_PARAMETERS: Map<String, String> =
            ImmutableMap
                .of( // zero dates by default cannot be parsed into java date objects (they will
                    // throw an error)
                    // in addition, users don't always have agency in fixing them e.g: maybe they
                    // don't own the database
                    // and can't
                    // remove zero date values.
                    // since zero dates are placeholders, we convert them to null by default
                    "zeroDateTimeBehavior",
                    "convertToNull",
                    "allowLoadLocalInfile",
                    "true"
                )

        @JvmField
        val DEFAULT_SSL_JDBC_PARAMETERS: Map<String, String> =
            MoreMaps.merge(
                ImmutableMap.of(
                    "useSSL",
                    "true",
                    "requireSSL",
                    "true",
                    "verifyServerCertificate",
                    "false"
                ),
                DEFAULT_JDBC_PARAMETERS
            )

        fun sshWrappedDestination(): Destination {
            return SshWrappedDestination(
                MySQLDestination(),
                JdbcUtils.HOST_LIST_KEY,
                JdbcUtils.PORT_LIST_KEY
            )
        }

        @Throws(Exception::class)
        fun handleException(e: Exception) {
            if (e is SQLSyntaxErrorException) {
                if (e.message!!.lowercase(Locale.getDefault()).contains("access denied")) {
                    throw ConfigErrorException("Access denied. Please check your configuration", e)
                }
            }

            throw e
        }

        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            val destination = sshWrappedDestination()
            LOGGER.info("starting destination: {}", MySQLDestination::class.java)
            try {
                IntegrationRunner(destination).run(args)
            } catch (e: Exception) {
                handleException(e)
            }
            LOGGER.info("completed destination: {}", MySQLDestination::class.java)
        }
    }
}
