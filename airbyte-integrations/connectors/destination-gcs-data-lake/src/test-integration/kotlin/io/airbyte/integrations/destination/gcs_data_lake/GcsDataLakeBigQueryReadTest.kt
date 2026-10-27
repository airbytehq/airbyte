/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import com.google.cloud.bigquery.BigQueryOptions
import com.google.cloud.bigquery.QueryJobConfiguration
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.BasePositionDeltaTaskWriter
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergDeleteMode
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableCommitter
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableWriterFactory
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.Operation
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.PositionalDeleteResolutionState
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.RecordWrapper
import io.airbyte.integrations.destination.gcs_data_lake.spec.BigLakeCatalogConfiguration
import java.nio.file.Files
import java.time.OffsetDateTime
import java.util.UUID
import kotlin.test.assertEquals
import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.SupportsNamespaces
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Test

class GcsDataLakeBigQueryReadTest {
    @Test
    fun `BigQuery reads latest deduped row with positional deletes`() {
        val configPath = GcsDataLakeTestUtil.BIGLAKE_CONFIG_PATH
        assumeTrue(Files.isRegularFile(configPath), "BigLake integration credentials are absent")

        val config = GcsDataLakeTestUtil.parseConfig(configPath)
        val bigLake =
            config.gcsCatalogConfiguration.catalogConfiguration as BigLakeCatalogConfiguration
        val catalog = GcsDataLakeTestUtil.getCatalog(config)
        val tableId =
            TableIdentifier.of(
                config.namespace,
                "bigquery_read_${UUID.randomUUID().toString().replace("-", "").take(12)}",
            )
        if (catalog is SupportsNamespaces && !catalog.namespaceExists(tableId.namespace())) {
            catalog.createNamespace(tableId.namespace())
        }
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "id", Types.StringType.get()),
                    Types.NestedField.required(2, "updated_at", Types.TimestampType.withZone()),
                    Types.NestedField.required(3, "value", Types.StringType.get()),
                ),
                setOf(1),
            )
        val table =
            catalog
                .buildTable(tableId, schema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase(),
                )
                .withProperty(TableProperties.FORMAT_VERSION, "2")
                .withPartitionSpec(PartitionSpec.builderFor(schema).day("updated_at").build())
                .create()
        fun record(updatedAt: String, value: String) =
            GenericRecord.create(schema).apply {
                setField("id", "key")
                setField("updated_at", OffsetDateTime.parse(updatedAt))
                setField("value", value)
            }

        try {
            val writerFactory = IcebergTableWriterFactory()
            val initialWriter = writerFactory.create(table, "ab-generation-id-0-e", Append, schema)
            initialWriter.write(record("2025-01-01T12:00:00Z", "old"))
            val initialResult = initialWriter.complete()
            table.newAppend().apply { initialResult.dataFiles().forEach(::appendFile) }.commit()

            val dedupe =
                Dedupe(
                    primaryKey = listOf(listOf("id")),
                    cursor = emptyList(),
                )
            val updateWriter =
                writerFactory.create(
                    table,
                    "ab-generation-id-1-e",
                    dedupe,
                    schema,
                    positionalDeleteRef = config.gcsCatalogConfiguration.mainBranchName,
                    positionalDeleteState = PositionalDeleteResolutionState(),
                    deleteMode = IcebergDeleteMode.POSITIONAL,
                ) as BasePositionDeltaTaskWriter
            updateWriter.write(
                RecordWrapper(
                    record("2025-01-02T12:00:00Z", "latest"),
                    Operation.UPDATE,
                ),
            )
            val updateResult = updateWriter.complete()
            IcebergTableCommitter.commit(
                table,
                config.gcsCatalogConfiguration.mainBranchName,
                updateResult,
                table.currentSnapshot()!!.snapshotId(),
                emptySet(),
                updateWriter.rewrittenDeleteFiles().toSet(),
                resolvesDeletes = true,
            )

            val bigQuery =
                BigQueryOptions.newBuilder()
                    .setProjectId(config.projectId)
                    .setCredentials(config.googleCredentials)
                    .build()
                    .service
            val tableName =
                "`${config.projectId}.${bigLake.catalogName}." +
                    "${tableId.namespace()}.${tableId.name()}`"
            val rows =
                bigQuery
                    .query(
                        QueryJobConfiguration.newBuilder(
                                "SELECT id, value FROM $tableName WHERE id = 'key'",
                            )
                            .setUseLegacySql(false)
                            .build(),
                    )
                    .iterateAll()
                    .toList()

            assertEquals(1, rows.size)
            assertEquals("latest", rows.single().get("value").stringValue)
        } finally {
            catalog.dropTable(tableId)
        }
    }
}
