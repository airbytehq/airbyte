/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlob
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.mssql.v2.config.AzureBlobStorageClientCreator
import io.airbyte.integrations.destination.mssql.v2.config.BulkLoadConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.DataSourceFactory
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfigurationFactory
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLSpecification
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import java.math.BigDecimal
import java.nio.file.Files
import java.nio.file.Path
import java.sql.Connection
import java.time.Instant
import java.time.OffsetDateTime
import java.time.temporal.ChronoUnit
import java.util.*
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

abstract class MSSQLAcceptanceTest(
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
        isStreamSchemaRetroactiveForUnknownTypeToString = false,
        dedupBehavior = DedupBehavior(),
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        unionBehavior = UnionBehavior.STRINGIFY,
        supportFileTransfer = false,
        commitDataIncrementally = true,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                numberCanBeLarge = false,
                nestedFloatLosesPrecision = false,
            ),
        unknownTypesBehavior = UnknownTypesBehavior.SERIALIZE,
        nullEqualsUnset = true,
        configUpdater = configUpdater,
    ) {
    @Test
    @Disabled(
        "there's a bug in the connector - https://github.com/airbytehq/airbyte-internal-issues/issues/13042"
    )
    override fun testFunkyCharactersDedup() {
        super.testFunkyCharactersDedup()
    }

    @Test
    @Disabled("there's a bug in the connector")
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }

    @Test
    open fun testBigDecimalScientificNotation() {
        val schema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "number" to FieldType(NumberType, nullable = true),
                ),
            )
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
                importType = Append,
                schema = schema,
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = NamespaceMapper(),
            )

        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(stream, """{"id": 1, "number": 1.5E8}""", emittedAtMs = 100),
            ),
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    data = mapOf("id" to 1, "number" to BigDecimal("150000000")),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }
}

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
    ): Map<String, String> {
        throw UnsupportedOperationException("destination-mssql doesn't support file transfer")
    }
}

object MSSQLDataCleaner : DestinationCleaner {
    private const val CLEANER_CONFIG_FILE = "secrets/azure_bulk_config.json"
    private val mssqlSpecification =
        ValidatedJsonUtils.parseOne(
            MSSQLSpecification::class.java,
            Files.readString(Path.of(CLEANER_CONFIG_FILE)),
        )
    private val config =
        MSSQLConfigurationFactory().makeWithOverrides(mssqlSpecification, emptyMap())

    override fun cleanup() {
        // Cleanup azure blobs if in BulkLoad configuration
        cleanupAzureBlobsIfNeeded()

        // Cleanup older test schemas
        cleanupOldTestSchemas()
    }

    /** Cleans up blobs older than 1 hour if the load configuration is [BulkLoadConfiguration]. */
    private fun cleanupAzureBlobsIfNeeded() {
        val loadConfig = mssqlSpecification.toLoadConfiguration().loadTypeConfiguration
        if (loadConfig !is BulkLoadConfiguration) return

        val azureBlobClient = AzureBlobStorageClientCreator.createAzureBlobClient(loadConfig)
        runBlocking {
            val blobList = mutableListOf<AzureBlob>()
            azureBlobClient.list("").toList(blobList)

            for (blobItem in blobList) {
                try {
                    val properties = azureBlobClient.getProperties(blobItem.key)
                    properties?.let { createdTime ->
                        val hoursSinceCreation =
                            ChronoUnit.HOURS.between(createdTime, OffsetDateTime.now())
                        if (hoursSinceCreation >= 1) {
                            azureBlobClient.delete(blobItem.key)
                        }
                    }
                } catch (e: Exception) {
                    // ignore exception - presumably someone else deleted the blob
                    // before we got to it
                }
            }
        }
    }

    /**
     * Removes any schema whose name is of the form `testYYYYMMDDsomeSuffix` and is exactly one day
     * old (compared to the current local date).
     */
    private fun cleanupOldTestSchemas() {
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

internal class StandardInsertMSSQLAcceptanceTest :
    MSSQLAcceptanceTest(
        configPath = Path.of(CONFIG_FILE),
        configUpdater = InsertConfigUpdater,
        dataDumper =
            MSSQLDataDumper { spec ->
                MSSQLConfigurationFactory().makeWithOverrides(spec, emptyMap())
            },
        dataCleaner = MSSQLDataCleaner,
    ) {

    companion object {
        const val CONFIG_FILE = "secrets/azure_bulk_config.json"
    }
}

/**
 * Rewrites the config JSON so that `load_type` is set to INSERT instead of BULK, allowing the same
 * Azure SQL DB credentials to be reused for the standard INSERT code-path tests.
 */
object InsertConfigUpdater : ConfigurationUpdater {
    override fun update(config: String): String {
        val node = Jsons.deserialize(config) as com.fasterxml.jackson.databind.node.ObjectNode
        node.set<com.fasterxml.jackson.databind.node.ObjectNode>(
            "load_type",
            Jsons.jsonNode(mapOf("load_type" to "INSERT")),
        )
        return Jsons.serialize(node)
    }

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult = DefaultNamespaceResult(config, null)
}

internal class BulkInsertMSSQLAcceptanceTest :
    MSSQLAcceptanceTest(
        configPath = Path.of(CONFIG_FILE),
        configUpdater = FakeConfigurationUpdater,
        dataDumper =
            MSSQLDataDumper { spec ->
                MSSQLConfigurationFactory().makeWithOverrides(spec, emptyMap())
            },
        dataCleaner = MSSQLDataCleaner,
    ) {

    companion object {
        const val CONFIG_FILE = "secrets/azure_bulk_config.json"
    }
}
