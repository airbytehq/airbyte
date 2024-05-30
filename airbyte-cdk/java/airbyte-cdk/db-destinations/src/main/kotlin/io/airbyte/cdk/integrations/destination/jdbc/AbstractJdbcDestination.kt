/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.db.factory.DataSourceFactory
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.db.jdbc.JdbcUtils.parseJdbcParameters
import io.airbyte.cdk.integrations.JdbcConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility.emitConfigErrorTrace
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.getRawNamespaceOverride
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.isDestinationV2
import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.async.deser.IdentityDataTransformer
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcV1V2Migrator
import io.airbyte.cdk.integrations.util.addDefaultNamespaceToStreams
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.map.MoreMaps
import io.airbyte.integrations.base.destination.typing_deduping.*
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.util.*
import java.util.function.Consumer
import javax.sql.DataSource
import org.apache.commons.lang3.NotImplementedException

private val LOGGER = KotlinLogging.logger {}

abstract class AbstractJdbcDestination<DestinationState : MinimumDestinationState>(
    driverClass: String,
    private val optimalBatchSizeBytes: Long,
    protected open val namingResolver: NamingConventionTransformer,
    protected val sqlOperations: SqlOperations,
) : JdbcConnector(driverClass), Destination {

    constructor(
        driverClass: String,
        namingResolver: NamingConventionTransformer,
        sqlOperations: SqlOperations,
    ) : this(
        driverClass,
        JdbcBufferedConsumerFactory.DEFAULT_OPTIMAL_BATCH_SIZE_FOR_FLUSH,
        namingResolver,
        sqlOperations
    )
    protected open val configSchemaKey: String = "schema"

    /**
     * If the destination should always disable type dedupe, override this method to return true. We
     * only type and dedupe if we create final tables.
     *
     * @return whether the destination should always disable type dedupe
     */
    protected open fun shouldAlwaysDisableTypeDedupe(): Boolean {
        return false
    }

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        val dataSource = getDataSource(config)

        try {
            val database = getDatabase(dataSource)
            val outputSchema = namingResolver.getIdentifier(config[JdbcUtils.SCHEMA_KEY].asText())
            attemptTableOperations(outputSchema, database, namingResolver, sqlOperations, false)
            if (isDestinationV2) {
                val v2RawSchema =
                    namingResolver.getIdentifier(
                        getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE)
                            .orElse(JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE),
                    )
                attemptTableOperations(v2RawSchema, database, namingResolver, sqlOperations, false)
                destinationSpecificTableOperations(database)
            }
            return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        } catch (ex: ConnectionErrorException) {
            val message = getErrorMessage(ex.stateCode, ex.errorCode, ex.exceptionMessage, ex)
            emitConfigErrorTrace(ex, message)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(message)
        } catch (e: Exception) {
            LOGGER.error(e) { "Exception while checking connection: " }
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    """
    Could not connect with provided configuration. 
    ${e.message}
    """.trimIndent(),
                )
        } finally {
            try {
                close(dataSource)
            } catch (e: Exception) {
                LOGGER.warn(e) { "Unable to close data source." }
            }
        }
    }

    /**
     * Specific Databases may have additional checks unique to them which they need to perform,
     * override this method to add additional checks.
     *
     * @param database the database to run checks against
     * @throws Exception
     */
    @Throws(Exception::class)
    protected open fun destinationSpecificTableOperations(database: JdbcDatabase?) {}

    /**
     * Subclasses which need to modify the DataSource should override [.modifyDataSourceBuilder]
     * rather than this method.
     */
    @VisibleForTesting
    open fun getDataSource(config: JsonNode): DataSource {
        val jdbcConfig = toJdbcConfig(config)
        val connectionProperties = getConnectionProperties(config)
        val builder =
            DataSourceFactory.DataSourceBuilder(
                    jdbcConfig[JdbcUtils.USERNAME_KEY].asText(),
                    if (jdbcConfig.has(JdbcUtils.PASSWORD_KEY))
                        jdbcConfig[JdbcUtils.PASSWORD_KEY].asText()
                    else null,
                    driverClassName,
                    jdbcConfig[JdbcUtils.JDBC_URL_KEY].asText(),
                )
                .withConnectionProperties(connectionProperties)
                .withConnectionTimeout(getConnectionTimeout(connectionProperties))
        return modifyDataSourceBuilder(builder).build()
    }

    protected open fun modifyDataSourceBuilder(
        builder: DataSourceFactory.DataSourceBuilder
    ): DataSourceFactory.DataSourceBuilder {
        return builder
    }

    @VisibleForTesting
    open fun getDatabase(dataSource: DataSource): JdbcDatabase {
        return DefaultJdbcDatabase(dataSource)
    }

    protected open fun getConnectionProperties(config: JsonNode): Map<String, String> {
        val customProperties = parseJdbcParameters(config, JdbcUtils.JDBC_URL_PARAMS_KEY)
        val defaultProperties = getDefaultConnectionProperties(config)
        assertCustomParametersDontOverwriteDefaultParameters(customProperties, defaultProperties)
        return MoreMaps.merge(customProperties, defaultProperties)
    }

    private fun assertCustomParametersDontOverwriteDefaultParameters(
        customParameters: Map<String, String>,
        defaultParameters: Map<String, String>
    ) {
        for (key in defaultParameters.keys) {
            require(
                !(customParameters.containsKey(key) &&
                    customParameters[key] != defaultParameters[key]),
            ) {
                "Cannot overwrite default JDBC parameter $key"
            }
        }
    }

    protected abstract fun getDefaultConnectionProperties(config: JsonNode): Map<String, String>

    abstract fun toJdbcConfig(config: JsonNode): JsonNode

    protected abstract fun getSqlGenerator(config: JsonNode): JdbcSqlGenerator

    protected abstract fun getDestinationHandler(
        databaseName: String,
        database: JdbcDatabase,
        rawTableSchema: String
    ): JdbcDestinationHandler<DestinationState>

    protected open fun getV1V2Migrator(
        database: JdbcDatabase,
        databaseName: String
    ): DestinationV1V2Migrator = JdbcV1V2Migrator(namingResolver, database, databaseName)

    /**
     * Provide any migrations that the destination needs to run. Most destinations will need to
     * provide an instande of
     * [io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcV1V2Migrator] at minimum.
     */
    protected abstract fun getMigrations(
        database: JdbcDatabase,
        databaseName: String,
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<DestinationState>
    ): List<Migration<DestinationState>>

    /**
     * "database" key at root of the config json, for any other variants in config, override this
     * method.
     *
     * @param config
     * @return
     */
    protected open fun getDatabaseName(config: JsonNode): String {
        return config[JdbcUtils.DATABASE_KEY].asText()
    }

    protected open fun getDataTransformer(
        parsedCatalog: ParsedCatalog?,
        defaultNamespace: String?
    ): StreamAwareDataTransformer {
        return IdentityDataTransformer()
    }

    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        throw NotImplementedException("Should use the getSerializedMessageConsumer instead")
    }

    @Throws(Exception::class)
    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer? {
        val database = getDatabase(getDataSource(config))
        // Short circuit for non-v2 destinations.
        if (!isDestinationV2) {
            return JdbcBufferedConsumerFactory.createAsync(
                outputRecordCollector,
                database,
                sqlOperations,
                namingResolver,
                config,
                catalog,
                null,
                NoopTyperDeduper(),
            )
        }

        val defaultNamespace = config[configSchemaKey].asText()
        addDefaultNamespaceToStreams(catalog, defaultNamespace)
        return getV2MessageConsumer(
            config,
            catalog,
            outputRecordCollector,
            database,
            defaultNamespace,
        )
    }

    private fun isTypeDedupeDisabled(config: JsonNode): Boolean {
        return shouldAlwaysDisableTypeDedupe() ||
            (config.has(DISABLE_TYPE_DEDUPE) &&
                config[DISABLE_TYPE_DEDUPE].asBoolean(
                    false,
                ))
    }

    private fun getV2MessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog?,
        outputRecordCollector: Consumer<AirbyteMessage>,
        database: JdbcDatabase,
        defaultNamespace: String
    ): SerializedAirbyteMessageConsumer {
        val sqlGenerator = getSqlGenerator(config)
        val rawNamespaceOverride = getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE)
        val parsedCatalog =
            rawNamespaceOverride
                .map { override: String -> CatalogParser(sqlGenerator, override) }
                .orElse(CatalogParser(sqlGenerator))
                .parseCatalog(catalog!!)
        val typerDeduper: TyperDeduper =
            buildTyperDeduper(
                config,
                database,
                parsedCatalog,
            )

        return JdbcBufferedConsumerFactory.createAsync(
            outputRecordCollector,
            database,
            sqlOperations,
            namingResolver,
            config,
            catalog,
            defaultNamespace,
            typerDeduper,
            getDataTransformer(parsedCatalog, defaultNamespace),
            optimalBatchSizeBytes,
            parsedCatalog,
        )
    }

    private fun buildTyperDeduper(
        config: JsonNode,
        database: JdbcDatabase,
        parsedCatalog: ParsedCatalog,
    ): TyperDeduper {
        val sqlGenerator = getSqlGenerator(config)
        val databaseName = getDatabaseName(config)
        val v2TableMigrator = NoopV2TableMigrator()
        val migrator = getV1V2Migrator(database, databaseName)
        val destinationHandler: DestinationHandler<DestinationState> =
            getDestinationHandler(
                databaseName,
                database,
                getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE)
                    .orElse(JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE),
            )
        val disableTypeDedupe = isTypeDedupeDisabled(config)
        val migrations = getMigrations(database, databaseName, sqlGenerator, destinationHandler)

        val typerDeduper: TyperDeduper
        if (disableTypeDedupe) {
            typerDeduper =
                if (migrations.isEmpty()) {
                    NoopTyperDeduper()
                } else {
                    NoOpTyperDeduperWithV1V2Migrations(
                        sqlGenerator,
                        destinationHandler,
                        parsedCatalog,
                        migrator,
                        v2TableMigrator,
                        migrations,
                    )
                }
        } else {
            typerDeduper =
                DefaultTyperDeduper(
                    sqlGenerator,
                    destinationHandler,
                    parsedCatalog,
                    migrator,
                    v2TableMigrator,
                    migrations,
                )
        }
        return typerDeduper
    }

    companion object {

        const val RAW_SCHEMA_OVERRIDE: String = "raw_data_schema"

        const val DISABLE_TYPE_DEDUPE: String = "disable_type_dedupe"

        /**
         * This method is deprecated. It verifies table creation, but not insert right to a newly
         * created table. Use attemptTableOperations with the attemptInsert argument instead.
         */
        @JvmStatic
        @Deprecated("")
        @Throws(Exception::class)
        fun attemptSQLCreateAndDropTableOperations(
            outputSchema: String,
            database: JdbcDatabase,
            namingResolver: NamingConventionTransformer,
            sqlOps: SqlOperations
        ) {
            attemptTableOperations(outputSchema, database, namingResolver, sqlOps, false)
        }

        /**
         * Verifies if provided creds has enough permissions. Steps are: 1. Create schema if not
         * exists. 2. Create test table. 3. Insert dummy record to newly created table if
         * "attemptInsert" set to true.
         * 4. Delete table created on step 2.
         *
         * @param outputSchema
         * - schema to tests against.
         * @param database
         * - database to tests against.
         * @param namingResolver
         * - naming resolver.
         * @param sqlOps
         * - SqlOperations object
         * @param attemptInsert
         * - set true if need to make attempt to insert dummy records to newly created table. Set
         * false to skip insert step.
         */
        @JvmStatic
        @Throws(Exception::class)
        fun attemptTableOperations(
            outputSchema: String,
            database: JdbcDatabase,
            namingResolver: NamingConventionTransformer,
            sqlOps: SqlOperations,
            attemptInsert: Boolean
        ) {
            // verify we have write permissions on the target schema by creating a table with a
            // random name,
            // then dropping that table
            try {
                // Get metadata from the database to see whether connection is possible
                database.bufferedResultSetQuery(
                    { conn: Connection -> conn.metaData.catalogs },
                    { queryContext: ResultSet ->
                        JdbcUtils.defaultSourceOperations.rowToJson(queryContext)
                    },
                )

                // verify we have write permissions on the target schema by creating a table with a
                // random name,
                // then dropping that table
                val outputTableName =
                    namingResolver.getIdentifier(
                        "_airbyte_connection_test_" +
                            UUID.randomUUID().toString().replace("-".toRegex(), ""),
                    )
                sqlOps.createSchemaIfNotExists(database, outputSchema)
                sqlOps.createTableIfNotExists(database, outputSchema, outputTableName)
                // verify if user has permission to make SQL INSERT queries
                try {
                    if (attemptInsert) {
                        sqlOps.insertRecords(
                            database,
                            listOf(dummyRecord),
                            outputSchema,
                            outputTableName,
                        )
                    }
                } finally {
                    sqlOps.dropTableIfExists(database, outputSchema, outputTableName)
                }
            } catch (e: SQLException) {
                if (Objects.isNull(e.cause) || e.cause !is SQLException) {
                    throw ConnectionErrorException(e.sqlState, e.errorCode, e.message, e)
                } else {
                    val cause = e.cause as SQLException?
                    throw ConnectionErrorException(e.sqlState, cause!!.errorCode, cause.message, e)
                }
            } catch (e: Exception) {
                throw Exception(e)
            }
        }

        private val dummyRecord: PartialAirbyteMessage
            /**
             * Generates a dummy AirbyteRecordMessage with random values.
             *
             * @return AirbyteRecordMessage object with dummy values that may be used to test insert
             * permission.
             */
            get() {
                val dummyDataToInsert = Jsons.deserialize("{ \"field1\": true }")
                return PartialAirbyteMessage()
                    .withRecord(
                        PartialAirbyteRecordMessage()
                            .withStream("stream1")
                            .withEmittedAt(1602637589000L),
                    )
                    .withSerialized(dummyDataToInsert.toString())
            }
    }
}
