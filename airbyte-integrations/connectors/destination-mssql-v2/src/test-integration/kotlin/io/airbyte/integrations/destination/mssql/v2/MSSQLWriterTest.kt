/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlob
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.integrations.destination.mssql.v2.config.AzureBlobStorageClientCreator
import io.airbyte.integrations.destination.mssql.v2.config.BulkLoadConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.DataSourceFactory
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfigurationFactory
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLSpecification
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import java.nio.file.Files
import java.nio.file.Path
import java.sql.Connection
import java.time.Instant
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.UUID
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.BeforeAll

abstract class MSSQLWriterTest(
    configPath: Path,
    configUpdater: ConfigurationUpdater,
    dataDumper: DestinationDataDumper,
    dataCleaner: DestinationCleaner,
) :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(configPath),
        configSpecClass = MSSQLSpecification::class.java,
        dataDumper = dataDumper,
        destinationCleaner = dataCleaner,
        isStreamSchemaRetroactive = true,
        supportsDedup = true,
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        unionBehavior = UnionBehavior.STRINGIFY,
        preserveUndeclaredFields = false,
        supportFileTransfer = false,
        commitDataIncrementally = true,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullUnknownTypes = false,
        nullEqualsUnset = true,
        configUpdater = configUpdater,
    )

class MSSQLDataDumper(private val configProvider: (MSSQLSpecification) -> MSSQLConfiguration) :
    DestinationDataDumper {

    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream,
    ): List<OutputRecord> {
        val mssqlSpec = spec as MSSQLSpecification
        val config = configProvider(mssqlSpec)
        val sqlBuilder = MSSQLQueryBuilder(config.schema, stream)
        val dataSource = DataSourceFactory().dataSource(config)
        val output = mutableListOf<OutputRecord>()

        dataSource.connection.use { connection ->
            val sql = SELECT_FROM.toQuery(sqlBuilder.outputSchema, sqlBuilder.tableName)
            sql.executeQuery(connection) { rs ->
                while (rs.next()) {
                    val objectValue = sqlBuilder.readResult(rs, sqlBuilder.finalTableSchema)
                    val record =
                        OutputRecord(
                            rawId =
                                rs.getString(COLUMN_NAME_AB_RAW_ID)?.let { UUID.fromString(it) },
                            extractedAt =
                                Instant.ofEpochMilli(rs.getLong(COLUMN_NAME_AB_EXTRACTED_AT)),
                            loadedAt = null,
                            generationId = rs.getLong(COLUMN_NAME_AB_GENERATION_ID),
                            data = objectValue,
                            airbyteMeta =
                                rs.getString(COLUMN_NAME_AB_META)?.let { metaJson ->
                                    val meta =
                                        Jsons.deserialize(
                                            metaJson,
                                            AirbyteRecordMessageMeta::class.java
                                        )
                                    OutputRecord.Meta(
                                        changes =
                                            meta.changes.map { change ->
                                                Meta.Change(
                                                    field = change.field,
                                                    change = change.change,
                                                    reason = change.reason,
                                                )
                                            },
                                        syncId =
                                            meta.additionalProperties["sync_id"]
                                                ?.toString()
                                                ?.toLong()
                                    )
                                }
                        )
                    output.add(record)
                }
            }
        }
        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream,
    ): List<String> {
        throw UnsupportedOperationException("destination-mssql doesn't support file transfer")
    }
}

class MSSQLDataCleaner(
    private val shouldCleanUp: Boolean,
    private val mssqlSpecification: MSSQLSpecification?,
    private val configProvider: (MSSQLSpecification) -> MSSQLConfiguration
) : DestinationCleaner {

    private val dateFormatter = DateTimeFormatter.ofPattern("yyyyMMdd")

    override fun cleanup() {
        if (!shouldCleanUp || mssqlSpecification == null) return

        // Cleanup azure blobs if in BulkLoad configuration
        cleanupAzureBlobsIfNeeded()

        // Cleanup older test schemas
        cleanupOldTestSchemas()
    }

    /** Cleans up blobs older than 1 hour if the load configuration is [BulkLoadConfiguration]. */
    private fun cleanupAzureBlobsIfNeeded() {
        val loadConfig = mssqlSpecification!!.toLoadConfiguration().loadTypeConfiguration
        if (loadConfig !is BulkLoadConfiguration) return

        val azureBlobClient = AzureBlobStorageClientCreator.createAzureBlobClient(loadConfig)
        runBlocking {
            val blobList = mutableListOf<AzureBlob>()
            azureBlobClient.list("").toList(blobList)

            for (blobItem in blobList) {
                val properties = azureBlobClient.getProperties(blobItem.key)
                properties?.let { createdTime ->
                    val hoursSinceCreation =
                        ChronoUnit.HOURS.between(createdTime, OffsetDateTime.now())
                    if (hoursSinceCreation >= 1) {
                        azureBlobClient.delete(blobItem.key)
                    }
                }
            }
        }
    }

    /**
     * Removes any schema whose name is of the form `testYYYYMMDDsomeSuffix` and is exactly one day
     * old (compared to the current local date).
     */
    private fun cleanupOldTestSchemas() {
        val config = configProvider(mssqlSpecification!!)
        val dataSource = DataSourceFactory().dataSource(config)

        dataSource.connection.use { conn ->
            try {
                val query = "SELECT name FROM sys.schemas WHERE name LIKE 'test%'"

                conn.createStatement().use { stmt ->
                    val rs = stmt.executeQuery(query)
                    val schemasToDelete = mutableListOf<String>()

                    while (rs.next()) {
                        val schemaName = rs.getString("name") ?: continue

                        // Ensure the schema name can contain "test" + 8-digit date => length >= 12
                        if (schemaName.length >= 12) {
                            if (
                                IntegrationTest.randomizedNamespaceRegex.matches(schemaName) &&
                                    IntegrationTest.isNamespaceOld(schemaName, 1)
                            ) {
                                schemasToDelete.add(schemaName)
                            }
                        }
                    }

                    for (schemaName in schemasToDelete) {
                        dropAllTablesInSchema(conn, schemaName)
                        dropSchema(conn, schemaName)
                    }
                }

                conn.commit()
            } catch (ex: Exception) {
                conn.rollback()
                throw ex
            }
        }
    }

    /** Drops all tables in the specified schema using dynamic SQL. */
    private fun dropAllTablesInSchema(conn: Connection, schemaName: String) {
        val dropTablesSql =
            """
            DECLARE @sql NVARCHAR(MAX) = N'';
            SELECT @sql += 'DROP TABLE ' + QUOTENAME(s.name) + '.' + QUOTENAME(t.name) + ';'
            FROM sys.schemas s
            JOIN sys.tables t ON s.schema_id = t.schema_id
            WHERE s.name = '$schemaName';
            EXEC sp_executesql @sql;
        """.trimIndent()

        conn.createStatement().use { stmt -> stmt.execute(dropTablesSql) }
    }

    /** Drops the specified schema. */
    private fun dropSchema(conn: Connection, schemaName: String) {
        val dropSchemaSql = "DROP SCHEMA [$schemaName]"
        conn.createStatement().use { stmt -> stmt.execute(dropSchemaSql) }
    }
}

internal class StandardInsert :
    MSSQLWriterTest(
        configPath = MSSQLTestConfigUtil.getConfigPath("check/valid.json"),
        configUpdater = MSSQLConfigUpdater(),
        dataDumper =
            MSSQLDataDumper { spec ->
                val configOverrides = buildOverridesForTestContainer()
                MSSQLConfigurationFactory().makeWithOverrides(spec, configOverrides)
            },
        dataCleaner =
            MSSQLDataCleaner(
                shouldCleanUp = false,
                mssqlSpecification = null,
            ) { spec ->
                val configOverrides = buildOverridesForTestContainer()
                MSSQLConfigurationFactory().makeWithOverrides(spec, configOverrides)
            },
    ) {

    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            MSSQLContainerHelper.start()
        }

        /** Builds a map of overrides for the test container environment. */
        private fun buildOverridesForTestContainer(): MutableMap<String, String> {
            return mutableMapOf("host" to MSSQLContainerHelper.getHost()).apply {
                MSSQLContainerHelper.getPort()?.let { port -> put("port", port.toString()) }
            }
        }
    }
}

internal class BulkInsert :
    MSSQLWriterTest(
        configPath = Path.of(CONFIG_FILE),
        configUpdater = FakeConfigurationUpdater,
        dataDumper =
            MSSQLDataDumper { spec ->
                MSSQLConfigurationFactory().makeWithOverrides(spec, emptyMap())
            },
        dataCleaner =
            MSSQLDataCleaner(
                shouldCleanUp = true,
                mssqlSpecification =
                    ValidatedJsonUtils.parseOne(
                        MSSQLSpecification::class.java,
                        Files.readString(Path.of(CONFIG_FILE))
                    )
            ) { spec -> MSSQLConfigurationFactory().makeWithOverrides(spec, emptyMap()) },
    ) {

    companion object {
        const val CONFIG_FILE = "secrets/bulk_upload_config.json"
    }
}
