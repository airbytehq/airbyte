/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.factory.DataSourceFactory.create
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftDestinationHandler
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftRawTableAirbyteMetaMigration
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGenerator
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftState
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSuperLimitationTransformer
import io.airbyte.integrations.destination.redshift.util.RedshiftUtil
import java.time.Duration
import java.util.*
import javax.sql.DataSource

class RedshiftInsertDestination :
    AbstractJdbcDestination<RedshiftState>(
        DRIVER_CLASS,
        REDSHIFT_OPTIMAL_BATCH_SIZE_FOR_FLUSH,
        RedshiftSQLNameTransformer(),
        RedshiftSqlOperations()
    ) {
    override fun toJdbcConfig(redshiftConfig: JsonNode): JsonNode {
        return getJdbcConfig(redshiftConfig)
    }

    override fun getDataSource(config: JsonNode): DataSource {
        val jdbcConfig = getJdbcConfig(config)
        return create(
            jdbcConfig[JdbcUtils.USERNAME_KEY].asText(),
            if (jdbcConfig.has(JdbcUtils.PASSWORD_KEY)) jdbcConfig[JdbcUtils.PASSWORD_KEY].asText()
            else null,
            DRIVER_CLASS,
            jdbcConfig[JdbcUtils.JDBC_URL_KEY].asText(),
            getDefaultConnectionProperties(config),
            Duration.ofMinutes(2)
        )
    }

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    @Throws(Exception::class)
    override fun destinationSpecificTableOperations(database: JdbcDatabase?) {
        RedshiftUtil.checkSvvTableAccess(database!!)
    }

    override fun getDatabase(dataSource: DataSource): JdbcDatabase {
        return DefaultJdbcDatabase(dataSource)
    }

    fun getDatabase(dataSource: DataSource, sourceOperations: JdbcSourceOperations?): JdbcDatabase {
        return DefaultJdbcDatabase(dataSource, sourceOperations)
    }

    override fun getDefaultConnectionProperties(config: JsonNode): Map<String, String> {
        // The following properties can be overriden through jdbcUrlParameters in the config.
        val connectionOptions: MutableMap<String, String> = HashMap()
        // Redshift properties
        // https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-configuration-options.html#jdbc20-connecttimeout-option
        // connectTimeout is different from Hikari pool's connectionTimout, driver defaults to
        // 10seconds so
        // increase it to match hikari's default
        connectionOptions["connectTimeout"] = "120"
        // See RedshiftProperty.LOG_SERVER_ERROR_DETAIL, defaults to true
        connectionOptions["logservererrordetail"] = "false"
        // HikariPool properties
        // https://github.com/brettwooldridge/HikariCP?tab=readme-ov-file#frequently-used
        // TODO: Change data source factory to configure these properties
        connectionOptions.putAll(SSL_JDBC_PARAMETERS)
        return connectionOptions
    }

    override fun getSqlGenerator(config: JsonNode): JdbcSqlGenerator {
        return RedshiftSqlGenerator(super.namingResolver, config)
    }

    override fun getDestinationHandler(
        databaseName: String,
        database: JdbcDatabase,
        rawTableSchema: String
    ): JdbcDestinationHandler<RedshiftState> {
        return RedshiftDestinationHandler(databaseName, database, rawTableSchema)
    }

    override fun getMigrations(
        database: JdbcDatabase,
        databaseName: String,
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<RedshiftState>
    ): List<Migration<RedshiftState>> {
        return java.util.List.of<Migration<RedshiftState>>(
            RedshiftRawTableAirbyteMetaMigration(database, databaseName)
        )
    }

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun getDataTransformer(
        parsedCatalog: ParsedCatalog?,
        defaultNamespace: String?
    ): StreamAwareDataTransformer {
        return RedshiftSuperLimitationTransformer(parsedCatalog, defaultNamespace!!)
    }

    companion object {
        val DRIVER_CLASS: String = DatabaseDriver.REDSHIFT.driverClassName
        @JvmField
        val SSL_JDBC_PARAMETERS: Map<String, String> =
            ImmutableMap.of(
                JdbcUtils.SSL_KEY,
                "true",
                "sslfactory",
                "com.amazon.redshift.ssl.NonValidatingFactory"
            )

        // insert into stmt has ~200 bytes
        // Per record overhead of ~150 bytes for strings in statement like JSON_PARSE.. uuid etc
        // If the flush size allows the max batch of 10k records, then net overhead is ~1.5MB.
        // Lets round it to 2MB for wiggle room and keep a max buffer of 14MB per flush.
        // This will allow not sending record set larger than 14M limiting the batch insert
        // statement.
        private const val REDSHIFT_OPTIMAL_BATCH_SIZE_FOR_FLUSH = 14 * 1024 * 1024L

        fun sshWrappedDestination(): Destination {
            return SshWrappedDestination(
                RedshiftInsertDestination(),
                JdbcUtils.HOST_LIST_KEY,
                JdbcUtils.PORT_LIST_KEY
            )
        }

        fun getJdbcConfig(redshiftConfig: JsonNode): JsonNode {
            val schema =
                Optional.ofNullable(redshiftConfig[JdbcUtils.SCHEMA_KEY])
                    .map { obj: JsonNode -> obj.asText() }
                    .orElse("public")
            val configBuilder =
                ImmutableMap.builder<Any, Any>()
                    .put(JdbcUtils.USERNAME_KEY, redshiftConfig[JdbcUtils.USERNAME_KEY].asText())
                    .put(JdbcUtils.PASSWORD_KEY, redshiftConfig[JdbcUtils.PASSWORD_KEY].asText())
                    .put(
                        JdbcUtils.JDBC_URL_KEY,
                        String.format(
                            "jdbc:redshift://%s:%s/%s",
                            redshiftConfig[JdbcUtils.HOST_KEY].asText(),
                            redshiftConfig[JdbcUtils.PORT_KEY].asText(),
                            redshiftConfig[JdbcUtils.DATABASE_KEY].asText()
                        )
                    )
                    .put(JdbcUtils.SCHEMA_KEY, schema)

            if (redshiftConfig.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
                configBuilder.put(
                    JdbcUtils.JDBC_URL_PARAMS_KEY,
                    redshiftConfig[JdbcUtils.JDBC_URL_PARAMS_KEY]
                )
            }

            return jsonNode(configBuilder.build())
        }
    }
}
