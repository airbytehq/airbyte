/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.getRawNamespaceOverride
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveDestinationRunner
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.jdbc.JdbcCheckOperations
import io.airbyte.cdk.integrations.destination.staging.StagingConsumerFactory.Companion.builder
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper
import io.airbyte.integrations.base.destination.typing_deduping.NoOpTyperDeduperWithV1V2Migrations
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.destination.snowflake.migrations.SnowflakeState
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV1V2Migrator
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV2TableMigrator
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.*
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.function.Consumer
import javax.sql.DataSource
import net.snowflake.client.core.SFSession
import net.snowflake.client.core.SFStatement
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.apache.commons.lang3.StringUtils
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class SnowflakeDestination
@JvmOverloads
constructor(
    private val airbyteEnvironment: String,
    private val nameTransformer: NamingConventionTransformer = SnowflakeSQLNameTransformer(),
) : BaseConnector(), Destination {

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        val snowflakeInternalStagingSqlOperations =
            SnowflakeInternalStagingSqlOperations(nameTransformer)
        val dataSource = getDataSource(config)
        try {
            val database = getDatabase(dataSource)
            val outputSchema = nameTransformer.getIdentifier(config["schema"].asText())
            JdbcCheckOperations.attemptTableOperations(
                outputSchema,
                database,
                nameTransformer,
                snowflakeInternalStagingSqlOperations,
                true,
            )
            attemptStageOperations(
                outputSchema,
                database,
                nameTransformer,
                snowflakeInternalStagingSqlOperations
            )
            return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        } catch (e: Exception) {
            LOGGER.error("Exception while checking connection: ", e)
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
                LOGGER.warn("Unable to close data source.", e)
            }
        }
    }

    private fun getDataSource(config: JsonNode?): DataSource {
        return SnowflakeDatabase.createDataSource(config, airbyteEnvironment)
    }

    private fun getDatabase(dataSource: DataSource?): JdbcDatabase {
        return SnowflakeDatabase.getDatabase(dataSource)
    }

    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer {
        AirbyteExceptionHandler.addAllStringsInConfigForDeinterpolation(config)

        val defaultNamespace = config["schema"].asText()
        for (stream in catalog.streams) {
            if (StringUtils.isEmpty(stream.stream.namespace)) {
                stream.stream.namespace = defaultNamespace
            }
        }

        val retentionPeriodDays =
            SnowflakeSqlOperations.getRetentionPeriodDays(
                config[SnowflakeSqlOperations.RETENTION_PERIOD_DAYS_CONFIG_KEY],
            )

        val sqlGenerator = SnowflakeSqlGenerator(retentionPeriodDays)
        val parsedCatalog: ParsedCatalog
        val typerDeduper: TyperDeduper
        val database = getDatabase(getDataSource(config))
        val databaseName = config[JdbcUtils.DATABASE_KEY].asText()
        val rawTableSchemaName: String
        val catalogParser: CatalogParser
        if (getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).isPresent) {
            rawTableSchemaName = getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).get()
            catalogParser = CatalogParser(sqlGenerator, rawTableSchemaName)
        } else {
            rawTableSchemaName = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
            catalogParser = CatalogParser(sqlGenerator)
        }
        val snowflakeDestinationHandler =
            SnowflakeDestinationHandler(databaseName, database, rawTableSchemaName)
        parsedCatalog = catalogParser.parseCatalog(catalog)
        val migrator = SnowflakeV1V2Migrator(this.nameTransformer, database, databaseName)
        val v2TableMigrator =
            SnowflakeV2TableMigrator(
                database,
                databaseName,
                sqlGenerator,
                snowflakeDestinationHandler
            )
        val disableTypeDedupe =
            config.has(DISABLE_TYPE_DEDUPE) && config[DISABLE_TYPE_DEDUPE].asBoolean(false)
        val migrations = listOf<Migration<SnowflakeState>>()
        typerDeduper =
            if (disableTypeDedupe) {
                NoOpTyperDeduperWithV1V2Migrations(
                    sqlGenerator,
                    snowflakeDestinationHandler,
                    parsedCatalog,
                    migrator,
                    v2TableMigrator,
                    migrations
                )
            } else {
                DefaultTyperDeduper(
                    sqlGenerator,
                    snowflakeDestinationHandler,
                    parsedCatalog,
                    migrator,
                    v2TableMigrator,
                    migrations,
                )
            }

        return builder(
                outputRecordCollector,
                database,
                SnowflakeInternalStagingSqlOperations(nameTransformer),
                nameTransformer,
                config,
                catalog,
                true,
                typerDeduper,
                parsedCatalog,
                defaultNamespace,
                JavaBaseConstants.DestinationColumns.V2_WITHOUT_META,
            )
            .setBufferMemoryLimit(Optional.of(snowflakeBufferMemoryLimit))
            .setOptimalBatchSizeBytes(
                // The per stream size limit is following recommendations from:
                // https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare.html#general-file-sizing-recommendations
                // "To optimize the number of parallel operations for a load,
                // we recommend aiming to produce data files roughly 100-250 MB (or larger) in size
                // compressed."
                (200 * 1024 * 1024).toLong(),
            )
            .build()
            .createAsync()
    }

    override val isV2Destination: Boolean
        get() = true

    @Throws(Exception::class)
    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        throw UnsupportedOperationException("DV2 destination cannot be called by getConsumer")
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(SnowflakeDestination::class.java)
        const val RAW_SCHEMA_OVERRIDE: String = "raw_data_schema"

        const val DISABLE_TYPE_DEDUPE: String = "disable_type_dedupe"
        @JvmField
        val SCHEDULED_EXECUTOR_SERVICE: ScheduledExecutorService =
            Executors.newScheduledThreadPool(1)

        @Throws(Exception::class)
        private fun attemptStageOperations(
            outputSchema: String,
            database: JdbcDatabase,
            namingResolver: NamingConventionTransformer,
            sqlOperations: SnowflakeInternalStagingSqlOperations
        ) {
            // verify we have permissions to create/drop stage

            val outputTableName =
                namingResolver.getIdentifier(
                    "_airbyte_connection_test_" +
                        UUID.randomUUID().toString().replace("-".toRegex(), "")
                )
            val stageName = sqlOperations.getStageName(outputSchema, outputTableName)
            sqlOperations.createStageIfNotExists(database, stageName)

            // try to make test write to make sure we have required role
            try {
                sqlOperations.attemptWriteToStage(outputSchema, stageName, database)
            } finally {
                // drop created tmp stage
                sqlOperations.dropStageIfExists(database, stageName, null)
            }
        }

        private val snowflakeBufferMemoryLimit: Long
            get() = (Runtime.getRuntime().maxMemory() * 0.5).toLong()
    }
}

fun main(args: Array<String>) {
    IntegrationRunner.addOrphanedThreadFilter { t: Thread ->
        for (stackTraceElement in IntegrationRunner.getThreadCreationInfo(t).stack) {
            val stackClassName = stackTraceElement.className
            val stackMethodName = stackTraceElement.methodName
            if (
                SFStatement::class.java.canonicalName == stackClassName &&
                    "close" == stackMethodName ||
                    SFSession::class.java.canonicalName == stackClassName &&
                        "callHeartBeatWithQueryTimeout" == stackMethodName
            ) {
                return@addOrphanedThreadFilter false
            }
        }
        true
    }
    AirbyteExceptionHandler.addThrowableForDeinterpolation(
        SnowflakeSQLException::class.java,
    )
    AdaptiveDestinationRunner.baseOnEnv()
        .withOssDestination {
            SnowflakeDestination(
                OssCloudEnvVarConsts.AIRBYTE_OSS,
            )
        }
        .withCloudDestination {
            SnowflakeDestination(
                OssCloudEnvVarConsts.AIRBYTE_CLOUD,
            )
        }
        .run(args)
    SnowflakeDestination.SCHEDULED_EXECUTOR_SERVICE.shutdownNow()
}
