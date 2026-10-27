/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import java.nio.file.Files
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.types.Types
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

class IcebergPartitioningTest {
    private fun schema() =
        Schema(
            listOf(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
                Types.NestedField.required(3, "updated_at", Types.TimestampType.withZone()),
                Types.NestedField.required(4, "year_at", Types.TimestampType.withZone()),
                Types.NestedField.required(5, "month_at", Types.TimestampType.withZone()),
                Types.NestedField.required(6, "hour_at", Types.TimestampType.withZone()),
                Types.NestedField.required(7, "bucket_id", Types.IntegerType.get()),
            ),
        )

    @Test
    fun `builds every partition transform with its argument`() {
        val spec =
            IcebergPartitioning.buildSpec(
                schema(),
                listOf(
                    IcebergPartitionField("id", IcebergPartitionTransform.IDENTITY),
                    IcebergPartitionField("year_at", IcebergPartitionTransform.YEAR),
                    IcebergPartitionField("month_at", IcebergPartitionTransform.MONTH),
                    IcebergPartitionField("updated_at", IcebergPartitionTransform.DAY),
                    IcebergPartitionField("hour_at", IcebergPartitionTransform.HOUR),
                    IcebergPartitionField(
                        "bucket_id",
                        IcebergPartitionTransform.BUCKET,
                        argument = 16,
                    ),
                    IcebergPartitionField("name", IcebergPartitionTransform.TRUNCATE, argument = 3),
                ),
            )

        assertThat(spec.fields().map { it.transform().toString() })
            .containsExactly(
                "identity",
                "year",
                "month",
                "day",
                "hour",
                "bucket[16]",
                "truncate[3]",
            )
    }

    @Test
    fun `skips missing columns and transforms that cannot bind`() {
        val spec =
            IcebergPartitioning.buildSpec(
                schema(),
                listOf(
                    IcebergPartitionField("missing", IcebergPartitionTransform.IDENTITY),
                    IcebergPartitionField("name", IcebergPartitionTransform.DAY),
                    IcebergPartitionField("id", IcebergPartitionTransform.IDENTITY),
                ),
            )

        assertThat(spec.fields().map { it.name() }).containsExactly("id")
    }

    @Test
    fun `evolves the spec additively and is idempotent`() {
        val warehouse = Files.createTempDirectory("iceberg-partition-evolution")
        val catalog = HadoopCatalog(Configuration(), warehouse.toString())
        val tableId = TableIdentifier.of("db", "records")
        catalog.createNamespace(tableId.namespace())
        val table =
            catalog
                .buildTable(tableId, schema())
                .withPartitionSpec(PartitionSpec.builderFor(schema()).identity("name").build())
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase(),
                )
                .create()
        val fields =
            listOf(
                IcebergPartitionField("updated_at", IcebergPartitionTransform.DAY),
                IcebergPartitionField("id", IcebergPartitionTransform.BUCKET, argument = 8),
            )

        assertThat(IcebergPartitioning.evolveSpec(table, fields)).isTrue()
        assertThat(IcebergPartitioning.evolveSpec(table, fields)).isFalse()
        assertThat(table.spec().fields().map { it.transform().toString() })
            .containsExactly("identity", "day", "bucket[8]")

        catalog.dropTable(tableId)
        warehouse.toFile().deleteRecursively()
    }
}
