/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.teradata

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.factory.DataSourceFactory
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination
import io.airbyte.cdk.integrations.destination.jdbc.JdbcGenerationHandler
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.map.MoreMaps
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationV1V2Migrator
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.teradata.typing_deduping.TeradataDestinationHandler
import io.airbyte.integrations.destination.teradata.typing_deduping.TeradataGenerationHandler
import io.airbyte.integrations.destination.teradata.typing_deduping.TeradataSqlGenerator
import io.airbyte.integrations.destination.teradata.typing_deduping.TeradataV1V2Migrator
import io.airbyte.integrations.destination.teradata.util.TeradataConstants
import java.io.IOException
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.util.*
import java.util.regex.Pattern
import javax.sql.DataSource
import kotlin.collections.HashMap

/**
 * The TeradataDestination class is responsible for handling the connection to the Teradata database
 * as destination from Airbyte. It extends the AbstractJdbcDestination class and implements the
 * Destination interface, facilitating the configuration and management of database interactions,
 * including setting a query band.
 */
class TeradataDestination :
    AbstractJdbcDestination<MinimumDestinationState>(
        TeradataConstants.DRIVER_CLASS,
        StandardNameTransformer()
    ),
    Destination {
    /**
     * Retrieves the data source for the Teradata database connection.
     *
     * @param config The configuration settings as a JsonNode.
     * @return The DataSource object for the Teradata connection.
     */
    override fun getDataSource(config: JsonNode): DataSource {
        val jdbcConfig = toJdbcConfig(config)
        val connectionProperties = getConnectionProperties(config)
        val dataSource =
            DataSourceFactory.create(
                jdbcConfig[JdbcUtils.USERNAME_KEY]?.asText(),
                jdbcConfig[JdbcUtils.PASSWORD_KEY]?.asText(),
                TeradataConstants.DRIVER_CLASS,
                jdbcConfig[JdbcUtils.JDBC_URL_KEY].asText(),
                connectionProperties,
                getConnectionTimeout(connectionProperties)
            )
        // set session query band
        setQueryBand(getDatabase(dataSource))
        return dataSource
    }

    public override fun getConnectionProperties(config: JsonNode): Map<String, String> {
        return MoreMaps.merge(appendLogMech(config), super.getConnectionProperties(config))
    }
    /** Appends Logging Mechanism to JDBC URL */
    private fun appendLogMech(config: JsonNode): Map<String, String> {
        val logmechParams: MutableMap<String, String> = HashMap()
        if (
            config.has(TeradataConstants.LOG_MECH) &&
                config.get(TeradataConstants.LOG_MECH).has(TeradataConstants.AUTH_TYPE) &&
                config.get(TeradataConstants.LOG_MECH).get(TeradataConstants.AUTH_TYPE).asText() !=
                    TeradataConstants.TD2_LOG_MECH
        ) {
            logmechParams[TeradataConstants.LOG_MECH] =
                config.get(TeradataConstants.LOG_MECH).get(TeradataConstants.AUTH_TYPE).asText()
        }
        return logmechParams
    }
    /**
     * Retrieves the JdbcDatabase instance based on the provided DataSource.
     *
     * @param dataSource The DataSource to create the JdbcDatabase from.
     * @return The JdbcDatabase instance.
     */
    public override fun getDatabase(dataSource: DataSource): JdbcDatabase {
        return DefaultJdbcDatabase(dataSource)
    }
    /**
     * Sets the Teradata session query band to identify the source of SQL requests originating from
     * Airbyte.
     *
     * @param jdbcDatabase The JdbcDatabase instance for which to set the query band.
     */
    private fun setQueryBand(jdbcDatabase: JdbcDatabase) {
        val setQueryBandSql =
            TeradataConstants.QUERY_BAND_SET +
                Companion.queryBand +
                TeradataConstants.QUERY_BAND_SESSION
        jdbcDatabase.execute(setQueryBandSql)
    }

    /**
     * Retrieves the default connection properties for the Teradata database based on the provided
     * configuration.
     *
     * @param config The configuration settings as a JsonNode.
     * @return A map of default connection properties.
     */
    public override fun getDefaultConnectionProperties(config: JsonNode): Map<String, String> {
        val additionalParameters: MutableMap<String, String> = HashMap()
        if (
            config.has(TeradataConstants.PARAM_SSL) &&
                config[TeradataConstants.PARAM_SSL].asBoolean()
        ) {
            if (config.has(TeradataConstants.PARAM_SSL_MODE)) {
                additionalParameters.putAll(
                    obtainConnectionOptions(config[TeradataConstants.PARAM_SSL_MODE])
                )
            } else {
                additionalParameters[TeradataConstants.PARAM_SSLMODE] = TeradataConstants.REQUIRE
            }
        }
        if (config.has(TeradataConstants.QUERY_BAND_KEY)) {
            Companion.queryBand =
                handleUserQueryBandText(
                    config[TeradataConstants.QUERY_BAND_KEY].asText(),
                )
        }
        additionalParameters[TeradataConstants.ENCRYPTDATA] = TeradataConstants.ENCRYPTDATA_ON
        return additionalParameters
    }
    /**
     * Returns a migrator that handles the migration between V1 and V2 versions of the destination.
     * This method is used to obtain an instance of a `DestinationV1V2Migrator` for migrating
     * between versions.
     *
     * @param database The database instance that is used for the migration.
     * @param databaseName The name of the database.
     * @return A `DestinationV1V2Migrator` instance specific to Teradata.
     */
    override fun getV1V2Migrator(
        database: JdbcDatabase,
        databaseName: String
    ): DestinationV1V2Migrator = TeradataV1V2Migrator(database)
    /**
     * Returns the database name extracted from the provided configuration. The database name is
     * derived from the `JdbcUtils.SCHEMA_KEY` key in the JSON configuration.
     *
     * @param config The JSON configuration containing database-related information.
     * @return A string representing the name of the database.
     */
    override fun getDatabaseName(config: JsonNode): String {
        return config[JdbcUtils.SCHEMA_KEY].asText()
    }
    /**
     * Returns a SQL generator that is used to generate SQL statements for interacting with the
     * database. This method provides a Teradata-specific SQL generator.
     *
     * @param config The JSON configuration to guide the SQL generation.
     * @return A `JdbcSqlGenerator` instance that generates SQL statements specific to Teradata.
     */
    override fun getSqlGenerator(config: JsonNode): JdbcSqlGenerator {
        return TeradataSqlGenerator()
    }
    /**
     * Returns the SQL operations for handling various SQL-related tasks, such as executing queries
     * or commands. This method returns the Teradata-specific SQL operations implementation.
     *
     * @param config The JSON configuration to guide the SQL operations.
     * @return A `SqlOperations` instance that provides SQL operations specific to Teradata.
     */
    override fun getSqlOperations(config: JsonNode): SqlOperations {
        return TeradataSqlOperations()
    }
    /**
     * Returns a generation handler that is responsible for generating database-related operations
     * such as schema generation, DDL statements, etc. This method provides a Teradata-specific
     * generation handler.
     *
     * @return A `JdbcGenerationHandler` instance that handles database generation tasks specific to
     * Teradata.
     */
    override fun getGenerationHandler(): JdbcGenerationHandler {
        return TeradataGenerationHandler()
    }
    /**
     * Returns a handler that is used to manage the destination during migration and data
     * processing. This handler is specific to Teradata and will help with raw table schema
     * handling, among other tasks.
     *
     * @param config The JSON configuration containing database and schema information.
     * @param databaseName The name of the database.
     * @param database The database instance used to interact with the destination.
     * @param rawTableSchema The raw table schema in the destination database.
     * @return A `JdbcDestinationHandler` that manages the destination database with specific
     * configurations.
     */
    override fun getDestinationHandler(
        config: JsonNode,
        databaseName: String,
        database: JdbcDatabase,
        rawTableSchema: String
    ): JdbcDestinationHandler<MinimumDestinationState> {
        return TeradataDestinationHandler(database, rawTableSchema, getGenerationHandler())
    }
    /**
     * Returns a list of migration objects that perform database migrations. In this case, an empty
     * list is returned, indicating that no migrations are needed for this particular database.
     *
     * @param database The database instance being migrated.
     * @param databaseName The name of the database being migrated.
     * @param sqlGenerator The SQL generator used for creating SQL statements during migrations.
     * @param destinationHandler The handler used to manage the destination during migration.
     * @return An empty list, as no migrations are specified.
     */
    override fun getMigrations(
        database: JdbcDatabase,
        databaseName: String,
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<MinimumDestinationState>
    ): List<Migration<MinimumDestinationState>> {
        return emptyList()
    }
    /**
     * Indicates whether the destination is considered a V2 destination. This flag can be used to
     * determine whether the system is operating in a V1 or V2 context.
     *
     * @return True if the destination is V2, false otherwise.
     */
    override val isV2Destination: Boolean
        get() = true

    /**
     * Obtains additional connection options like SSL configuration.
     *
     * @param encryption The JsonNode containing SSL parameters.
     * @return A map of additional connection properties.
     */
    private fun obtainConnectionOptions(encryption: JsonNode): Map<String, String> {
        val additionalParameters: MutableMap<String, String> = HashMap()
        if (!encryption.isNull) {
            val method = encryption[TeradataConstants.PARAM_MODE].asText()
            additionalParameters[TeradataConstants.PARAM_SSLMODE] = method

            if (TeradataConstants.VERIFY_CA == method || TeradataConstants.VERIFY_FULL == method) {
                createCertificateFile(encryption[TeradataConstants.CA_CERT_KEY].asText())
                additionalParameters[TeradataConstants.PARAM_SSLCA] =
                    TeradataConstants.CA_CERTIFICATE
            }
        }
        return additionalParameters
    }

    /** Creates certificate file for verify-ca and verify-full ssl connection */
    @Throws(IOException::class)
    private fun createCertificateFile(fileValue: String) {
        PrintWriter(TeradataConstants.CA_CERTIFICATE, StandardCharsets.UTF_8).use { out ->
            out.print(fileValue)
        }
    }
    /**
     * Handles and validates the user-defined query band text.
     *
     * @param queryBandText The user-defined query band text.
     * @return The validated query band text, ensuring required parameters are presentin required
     * format.
     */
    private fun handleUserQueryBandText(queryBandText: String?): String {
        if (queryBandText.isNullOrBlank()) {
            return Companion.queryBand
        }
        var updatedQueryBand = StringBuilder(queryBandText)
        // checking org doesn't exist in query_band, appending 'org=teradata-internal-telem'
        // If it exists, user might have set some value of their own, so doing nothing in that case
        val orgMatcher = Pattern.compile("org\\s*=").matcher(queryBandText)
        if (!orgMatcher.find()) {
            if (queryBandText.isNotBlank() && !queryBandText.endsWith(";")) {
                updatedQueryBand.append(";")
            }
            updatedQueryBand.append(TeradataConstants.DEFAULT_QUERY_BAND_ORG)
        }

        // Ensure appname contains airbyte is present or append it if it exists with different value
        val appNameMatcher = Pattern.compile("appname\\s*=\\s*([^;]*)").matcher(updatedQueryBand)
        if (appNameMatcher.find()) {
            val appNameValue = appNameMatcher.group(1).trim { it <= ' ' }
            if (!appNameValue.lowercase(Locale.getDefault()).contains("airbyte")) {
                updatedQueryBand =
                    StringBuilder(
                        updatedQueryBand
                            .toString()
                            .replace(
                                "appname\\s*=\\s*([^;]*)".toRegex(),
                                "appname=" + appNameValue + "_airbyte",
                            ),
                    )
            }
        } else {
            if (updatedQueryBand.isNotEmpty() && !updatedQueryBand.toString().endsWith(";")) {
                updatedQueryBand.append(";")
            }
            updatedQueryBand.append(TeradataConstants.DEFAULT_QUERY_BAND_APPNAME)
        }
        return updatedQueryBand.toString()
    }
    /**
     * Converts the provided configuration into JDBC configuration settings.
     *
     * @param config The configuration settings as a JsonNode.
     * @return The converted JsonNode containing JDBC configuration.
     */
    override fun toJdbcConfig(config: JsonNode): JsonNode {
        val schema = config[JdbcUtils.SCHEMA_KEY]?.asText() ?: TeradataConstants.DEFAULT_SCHEMA_NAME
        val jdbcUrl = String.format("jdbc:teradata://%s/", config[JdbcUtils.HOST_KEY].asText())
        val userName = config[TeradataConstants.LOG_MECH]?.get(JdbcUtils.USERNAME_KEY)?.asText()
        val password = config[TeradataConstants.LOG_MECH]?.get(JdbcUtils.PASSWORD_KEY)?.asText()
        val configBuilder =
            ImmutableMap.builder<Any, Any>()
                .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl)
                .put(JdbcUtils.SCHEMA_KEY, schema)
        userName?.let { configBuilder.put(JdbcUtils.USERNAME_KEY, it) }
        password?.let { configBuilder.put(JdbcUtils.PASSWORD_KEY, it) }
        config[JdbcUtils.JDBC_URL_PARAMS_KEY]?.asText()?.let {
            configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, it)
        }
        return Jsons.jsonNode(configBuilder.build())
    }

    val queryBand: String
        get() = Companion.queryBand

    companion object {

        private var queryBand = TeradataConstants.DEFAULT_QUERY_BAND

        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            IntegrationRunner(TeradataDestination()).run(args)
        }
    }
}
