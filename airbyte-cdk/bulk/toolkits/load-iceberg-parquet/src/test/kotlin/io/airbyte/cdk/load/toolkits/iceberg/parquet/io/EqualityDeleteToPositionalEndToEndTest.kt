/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import java.nio.file.Files
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.DeleteFile
import org.apache.iceberg.FileContent
import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.types.Types
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

class EqualityDeleteToPositionalEndToEndTest {

    private val schema =
        Schema(
            listOf(
                Types.NestedField.required(1, "id", Types.StringType.get()),
                Types.NestedField.required(2, "category", Types.StringType.get()),
                Types.NestedField.required(3, "name", Types.StringType.get()),
            ),
            setOf(1),
        )

    private val dedupe = Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList())

    private fun catalog(): HadoopCatalog {
        val warehouse = Files.createTempDirectory("equality-delete-positional-e2e")
        return HadoopCatalog(Configuration(), warehouse.toString())
    }

    private fun createTable(catalog: HadoopCatalog, tableId: TableIdentifier, version: Int): Table {
        if (!catalog.namespaceExists(tableId.namespace())) {
            catalog.createNamespace(tableId.namespace())
        }
        return catalog
            .buildTable(tableId, schema)
            .withPartitionSpec(PartitionSpec.builderFor(schema).identity("category").build())
            .withProperty(TableProperties.DEFAULT_FILE_FORMAT, FileFormat.PARQUET.name.lowercase())
            .withProperty(TableProperties.FORMAT_VERSION, version.toString())
            .create()
    }

    private fun seed(table: Table, rows: List<Triple<String, String, String>>) {
        val writer =
            IcebergTableWriterFactory().create(table, "ab-generation-id-0-e", Append, schema)
        rows.forEach { (id, category, name) -> writer.write(record(id, category, name)) }
        val result = writer.complete()
        table.newAppend().apply { result.dataFiles().forEach(::appendFile) }.commit()
    }

    private fun commitEqualityDeletes(
        table: Table,
        branch: String = "main",
        vararg rows: Triple<String, String, String>,
    ) {
        val writer =
            IcebergTableWriterFactory().create(table, "ab-generation-id-1-e", dedupe, schema)
        rows.forEach { (id, category, name) ->
            writer.write(RecordWrapper(record(id, category, name), Operation.DELETE))
        }
        val result = writer.complete()
        val delta = table.newRowDelta().toBranch(branch)
        result.dataFiles().forEach(delta::addRows)
        result.deleteFiles().forEach(delta::addDeletes)
        delta.commit()
    }

    private fun commitPositionDeletes(table: Table, vararg rows: Triple<String, String, String>) {
        val writer =
            IcebergTableWriterFactory()
                .create(
                    table,
                    "ab-generation-id-2-e",
                    dedupe,
                    schema,
                    positionalDeleteRef = "main",
                    positionalDeleteState = PositionalDeleteResolutionState(),
                    deleteMode = IcebergDeleteMode.POSITIONAL,
                )
        val positionWriter = writer as BasePositionDeltaTaskWriter
        rows.forEach { (id, category, name) ->
            positionWriter.write(RecordWrapper(record(id, category, name), Operation.DELETE))
        }
        val result = positionWriter.complete()
        IcebergTableCommitter.commit(
            table,
            "main",
            result,
            table.currentSnapshot().snapshotId(),
            positionWriter.fullySupersededDataFiles(),
            positionWriter.rewrittenDeleteFiles().toSet(),
            resolvesDeletes = true,
        )
    }

    private fun liveDeleteFiles(table: Table, branch: String = "main"): List<DeleteFile> {
        table.refresh()
        val snapshotId = table.refs()[branch]!!.snapshotId()
        return table
            .snapshot(snapshotId)!!
            .deleteManifests(table.io())
            .flatMap { manifest ->
                org.apache.iceberg.ManifestFiles.readDeleteManifest(
                        manifest,
                        table.io(),
                        table.specs(),
                    )
                    .use { reader -> reader.toList() }
            }
            .distinctBy { it.location() }
    }

    private fun rows(table: Table, branch: String = "main"): List<Triple<String, String, String>> {
        table.refresh()
        val reader =
            IcebergGenerics.read(table).useSnapshot(table.refs()[branch]!!.snapshotId()).build()
        return reader.use { records ->
            records.map {
                Triple(
                    it.getField("id").toString(),
                    it.getField("category").toString(),
                    it.getField("name").toString(),
                )
            }
        }
    }

    private fun record(id: String, category: String, name: String): GenericRecord =
        GenericRecord.create(schema).apply {
            setField("id", id)
            setField("category", category)
            setField("name", name)
        }

    @Test
    fun `converts main branch equality deletes without changing table version or rows`() {
        val catalog = catalog()
        val tableId = TableIdentifier.of("db", "main_equality")
        val table = createTable(catalog, tableId, 2)
        seed(table, listOf(Triple("1", "A", "one"), Triple("2", "A", "two")))
        commitEqualityDeletes(table, "main", Triple("2", "A", "ignored"))
        val rowsBefore = rows(table)

        val converted = IcebergTableUpgrader.convertEqualityDeletesToPositional(catalog, tableId)
        val deletes = liveDeleteFiles(converted)

        assertThat(tableFormatVersion(converted)).isEqualTo(2)
        assertThat(deletes).noneMatch { it.content() == FileContent.EQUALITY_DELETES }
        assertThat(deletes).anyMatch { it.content() == FileContent.POSITION_DELETES }
        assertThat(rows(converted)).containsExactlyInAnyOrderElementsOf(rowsBefore)
    }

    @Test
    fun `preserves pre-existing position deletes`() {
        val catalog = catalog()
        val tableId = TableIdentifier.of("db", "mixed_deletes")
        val table = createTable(catalog, tableId, 2)
        seed(
            table,
            listOf(
                Triple("1", "A", "one"),
                Triple("2", "A", "two"),
                Triple("3", "A", "three"),
            ),
        )
        commitPositionDeletes(table, Triple("3", "A", "ignored"))
        val existingPositionDeleteLocations =
            liveDeleteFiles(table)
                .filter { it.content() == FileContent.POSITION_DELETES }
                .map { it.location() }
                .toSet()
        commitEqualityDeletes(table, "main", Triple("2", "A", "ignored"))
        val rowsBefore = rows(table)

        IcebergTableUpgrader.convertEqualityDeletesToPositional(catalog, tableId)

        val deletes = liveDeleteFiles(table)
        assertThat(deletes).noneMatch { it.content() == FileContent.EQUALITY_DELETES }
        assertThat(deletes.map { it.location() }).containsAll(existingPositionDeleteLocations)
        assertThat(rows(table)).containsExactlyInAnyOrderElementsOf(rowsBefore)
    }

    @Test
    fun `converts equality deletes on retained non-main branches`() {
        val catalog = catalog()
        val tableId = TableIdentifier.of("db", "branch_equality")
        val table = createTable(catalog, tableId, 2)
        seed(table, listOf(Triple("1", "A", "one"), Triple("2", "A", "two")))
        table.manageSnapshots().createBranch("staging").commit()
        commitEqualityDeletes(table, "staging", Triple("2", "A", "ignored"))
        val rowsBefore = rows(table, "staging")

        IcebergTableUpgrader.convertEqualityDeletesToPositional(catalog, tableId)

        assertThat(liveDeleteFiles(table, "staging")).noneMatch {
            it.content() == FileContent.EQUALITY_DELETES
        }
        assertThat(liveDeleteFiles(table, "staging")).anyMatch {
            it.content() == FileContent.POSITION_DELETES
        }
        assertThat(rows(table, "staging")).containsExactlyInAnyOrderElementsOf(rowsBefore)
        assertThat(liveDeleteFiles(table)).isEmpty()
    }

    @Test
    fun `converts equality deletes only within their partition`() {
        val catalog = catalog()
        val tableId = TableIdentifier.of("db", "partition_equality")
        val table = createTable(catalog, tableId, 2)
        seed(
            table,
            listOf(Triple("same", "A", "left"), Triple("same", "B", "right")),
        )
        commitEqualityDeletes(table, "main", Triple("same", "A", "ignored"))
        val rowsBefore = rows(table)

        IcebergTableUpgrader.convertEqualityDeletesToPositional(catalog, tableId)

        assertThat(rowsBefore).containsExactly(Triple("same", "B", "right"))
        assertThat(rows(table)).containsExactlyElementsOf(rowsBefore)
    }

    @Test
    fun `removes equality deletes that apply to no data file`() {
        val catalog = catalog()
        val tableId = TableIdentifier.of("db", "orphan_equality")
        val table = createTable(catalog, tableId, 2)
        val writer =
            IcebergTableWriterFactory().create(table, "ab-generation-id-1-e", dedupe, schema)
        writer.write(RecordWrapper(record("1", "A", "one"), Operation.INSERT))
        writer.write(RecordWrapper(record("2", "A", "ignored"), Operation.DELETE))
        val result = writer.complete()
        val delta = table.newRowDelta()
        result.dataFiles().forEach(delta::addRows)
        result.deleteFiles().forEach(delta::addDeletes)
        delta.commit()
        assertThat(liveDeleteFiles(table)).anyMatch {
            it.content() == FileContent.EQUALITY_DELETES
        }
        val rowsBefore = rows(table)

        IcebergTableUpgrader.convertEqualityDeletesToPositional(catalog, tableId)

        assertThat(liveDeleteFiles(table)).noneMatch {
            it.content() == FileContent.EQUALITY_DELETES
        }
        assertThat(rows(table)).containsExactlyInAnyOrderElementsOf(rowsBefore)
    }

    @Test
    fun `does not create snapshots when there are no equality deletes or the table is v3`() {
        val catalog = catalog()
        val v2Id = TableIdentifier.of("db", "no_equality")
        val v2Table = createTable(catalog, v2Id, 2)
        seed(v2Table, listOf(Triple("1", "A", "one")))
        val v2SnapshotId = v2Table.currentSnapshot().snapshotId()

        val returnedV2 = IcebergTableUpgrader.convertEqualityDeletesToPositional(catalog, v2Id)

        assertThat(returnedV2.currentSnapshot().snapshotId()).isEqualTo(v2SnapshotId)

        val v3Id = TableIdentifier.of("db", "v3_no_equality")
        val v3Table = createTable(catalog, v3Id, 3)
        seed(v3Table, listOf(Triple("1", "A", "one")))
        val v3SnapshotId = v3Table.currentSnapshot().snapshotId()

        val returnedV3 = IcebergTableUpgrader.convertEqualityDeletesToPositional(catalog, v3Id)

        assertThat(returnedV3.currentSnapshot().snapshotId()).isEqualTo(v3SnapshotId)
    }
}
