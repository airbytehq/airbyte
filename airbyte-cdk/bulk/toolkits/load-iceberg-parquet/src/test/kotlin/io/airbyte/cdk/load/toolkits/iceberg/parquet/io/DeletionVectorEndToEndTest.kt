/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import java.nio.file.Files
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.DeleteFile
import org.apache.iceberg.FileContent
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.types.Types
import org.apache.iceberg.util.ContentFileUtil
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.Test

class DeletionVectorEndToEndTest {

    private val schema =
        Schema(
            listOf(
                Types.NestedField.required(1, "id", Types.StringType.get()),
                Types.NestedField.required(2, "name", Types.StringType.get()),
            ),
            setOf(1),
        )

    private val dedupe =
        Dedupe(
            primaryKey = listOf(listOf("id")),
            cursor = emptyList(),
        )

    private fun catalog(): Pair<HadoopCatalog, java.nio.file.Path> {
        val warehouse = Files.createTempDirectory("deletion-vector-e2e")
        return HadoopCatalog(Configuration(), warehouse.toString()) to warehouse
    }

    private fun createTable(catalog: HadoopCatalog, tableId: TableIdentifier, version: Int): Table {
        if (!catalog.namespaceExists(tableId.namespace())) {
            catalog.createNamespace(tableId.namespace())
        }
        return catalog
            .buildTable(tableId, schema)
            .withProperty(TableProperties.DEFAULT_FILE_FORMAT, FileFormat.PARQUET.name.lowercase())
            .withProperty(TableProperties.FORMAT_VERSION, version.toString())
            .create()
    }

    private fun seed(table: Table, rows: List<Pair<String, String>>) {
        val writer =
            IcebergTableWriterFactory().create(table, "ab-generation-id-0-e", Append, schema)
        rows.forEach { (id, name) -> writer.write(record(id, name)) }
        val result = writer.complete()
        table.newAppend().apply { result.dataFiles().forEach(::appendFile) }.commit()
    }

    private fun commitWriter(table: Table, writer: BasePositionDeltaTaskWriter) {
        val result = writer.complete()
        IcebergTableCommitter.commit(
            table,
            "main",
            result,
            table.currentSnapshot().snapshotId(),
            writer.fullySupersededDataFiles(),
            writer.rewrittenDeleteFiles().toSet(),
            resolvesDeletes = true,
        )
    }

    private fun deleteFiles(table: Table): List<DeleteFile> {
        table.refresh()
        return table.newScan().planFiles().use { tasks ->
            tasks.flatMap { it.deletes() }.distinctBy { it.location().toString() }
        }
    }

    private fun rows(table: Table): List<Pair<String, String>> {
        table.refresh()
        return IcebergGenerics.read(table).build().use { records ->
            records.map { it.getField("id").toString() to it.getField("name").toString() }
        }
    }

    private fun record(id: String, name: String): GenericRecord =
        GenericRecord.create(schema).apply {
            setField("id", id)
            setField("name", name)
        }

    @Test
    fun `v3 dedupe writes deletion vectors across repeated syncs`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records")
        val table = createTable(catalog, tableId, 3)
        assertThat(tableFormatVersion(table)).isEqualTo(3)
        seed(table, listOf("1" to "one", "2" to "two"))

        val writerFactory = IcebergTableWriterFactory()

        // Sync 1: update one row, delete another.
        val first =
            writerFactory.create(
                table,
                "ab-generation-id-1-e",
                dedupe,
                schema,
                positionalDeleteRef = "main",
                positionalDeleteState = PositionalDeleteResolutionState(),
                deleteMode = IcebergDeleteMode.DELETION_VECTOR,
            ) as BasePositionDeltaTaskWriter
        first.write(RecordWrapper(record("1", "one-updated"), Operation.UPDATE))
        first.write(RecordWrapper(record("2", "ignored"), Operation.DELETE))
        first.write(RecordWrapper(record("3", "three"), Operation.INSERT))
        commitWriter(table, first)

        var deletes = deleteFiles(table)
        assertThat(deletes).isNotEmpty
        assertThat(deletes).allMatch { it.format() == FileFormat.PUFFIN }
        assertThat(deletes).allMatch { it.location().endsWith(".puffin") }
        assertThat(deletes).allMatch { it.referencedDataFile() != null }
        assertThat(deletes.map { it.referencedDataFile() }).doesNotHaveDuplicates()
        assertThat(rows(table)).containsExactlyInAnyOrder("1" to "one-updated", "3" to "three")

        // Sync 2: another update plus another delete on the same data file, so the
        // existing DV must be merged and replaced rather than duplicated.
        val second =
            writerFactory.create(
                table,
                "ab-generation-id-2-e",
                dedupe,
                schema,
                positionalDeleteRef = "main",
                positionalDeleteState = PositionalDeleteResolutionState(),
                deleteMode = IcebergDeleteMode.DELETION_VECTOR,
            ) as BasePositionDeltaTaskWriter
        second.write(RecordWrapper(record("1", "one-updated-again"), Operation.UPDATE))
        second.write(RecordWrapper(record("3", "ignored"), Operation.DELETE))
        commitWriter(table, second)

        deletes = deleteFiles(table)
        assertThat(deletes).allMatch { it.format() == FileFormat.PUFFIN }
        assertThat(deletes).allMatch { it.referencedDataFile() != null }
        assertThat(deletes.map { it.referencedDataFile() }).doesNotHaveDuplicates()
        assertThat(rows(table)).containsExactlyInAnyOrder("1" to "one-updated-again")
    }

    @Test
    fun `upgrade converts equality deletes to deletion vectors`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_eq")
        val table = createTable(catalog, tableId, 2)
        seed(table, listOf("1" to "one", "2" to "two"))

        // Produce a legacy equality delete through the standard dedupe writer.
        val equalityWriter =
            IcebergTableWriterFactory().create(table, "ab-generation-id-1-e", dedupe, schema)
        equalityWriter.write(RecordWrapper(record("2", "ignored"), Operation.DELETE))
        equalityWriter.write(RecordWrapper(record("3", "three"), Operation.UPDATE))
        val result = equalityWriter.complete()
        val delta = table.newRowDelta()
        result.dataFiles().forEach { delta.addRows(it) }
        result.deleteFiles().forEach { delta.addDeletes(it) }
        delta.commit()
        assertThat(deleteFiles(table).map { it.content() }).contains(FileContent.EQUALITY_DELETES)
        val preUpgradeRows = rows(table)

        val upgraded = IcebergTableUpgrader.upgradeToV3(catalog, tableId, backup = false)

        assertThat(tableFormatVersion(upgraded)).isEqualTo(3)
        val deletes = deleteFiles(table)
        assertThat(deletes).allMatch { it.format() == FileFormat.PUFFIN }
        assertThat(deletes.map { it.referencedDataFile() }).doesNotHaveDuplicates()
        assertThat(rows(table)).containsExactlyInAnyOrderElementsOf(preUpgradeRows)
    }

    @Test
    fun `upgrade removes a delete file that applies to no data file`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_orphan_eq")
        val table = createTable(catalog, tableId, 2)

        // One commit carrying both the data file and an equality delete at the same
        // sequence number, as a dedupe insert sync produces: the delete applies to no
        // committed data file, so scan-task deletes never list it, but its manifest
        // entry must still be swapped out at v3.
        val equalityWriter =
            IcebergTableWriterFactory().create(table, "ab-generation-id-1-e", dedupe, schema)
        equalityWriter.write(RecordWrapper(record("1", "one"), Operation.INSERT))
        equalityWriter.write(RecordWrapper(record("2", "two"), Operation.DELETE))
        val result = equalityWriter.complete()
        val delta = table.newRowDelta()
        result.dataFiles().forEach { delta.addRows(it) }
        result.deleteFiles().forEach { delta.addDeletes(it) }
        delta.commit()
        assertThat(table.currentSnapshot().deleteManifests(table.io()).isNotEmpty())
        assertThat(deleteFiles(table)).isEmpty()

        val upgraded = IcebergTableUpgrader.upgradeToV3(catalog, tableId, backup = false)

        assertThat(tableFormatVersion(upgraded)).isEqualTo(3)
        val remaining =
            upgraded.currentSnapshot().deleteManifests(table.io()).flatMap { manifest ->
                org.apache.iceberg.ManifestFiles.readDeleteManifest(
                        manifest,
                        table.io(),
                        table.specs(),
                    )
                    .use { reader -> reader.toList() }
            }
        assertThat(remaining).allMatch { ContentFileUtil.isDV(it) }
        assertThat(rows(table)).containsExactlyInAnyOrder("1" to "one")
    }

    @Test
    fun `upgrade converts position deletes to deletion vectors`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_pos")
        val table = createTable(catalog, tableId, 2)
        seed(table, listOf("1" to "one", "2" to "two"))

        // Produce a legacy position delete through the positional writer.
        val positional =
            IcebergTableWriterFactory()
                .create(
                    table,
                    "ab-generation-id-1-e",
                    dedupe,
                    schema,
                    positionalDeleteRef = "main",
                    positionalDeleteState = PositionalDeleteResolutionState(),
                    deleteMode = IcebergDeleteMode.POSITIONAL,
                ) as BasePositionDeltaTaskWriter
        positional.write(RecordWrapper(record("2", "ignored"), Operation.DELETE))
        positional.write(RecordWrapper(record("3", "three"), Operation.UPDATE))
        commitWriter(table, positional)
        assertThat(deleteFiles(table).map { it.content() }).contains(FileContent.POSITION_DELETES)
        val preUpgradeRows = rows(table)

        val upgraded = IcebergTableUpgrader.upgradeToV3(catalog, tableId, backup = false)

        assertThat(tableFormatVersion(upgraded)).isEqualTo(3)
        val deletes = deleteFiles(table)
        assertThat(deletes).allMatch { it.format() == FileFormat.PUFFIN }
        assertThat(rows(table)).containsExactlyInAnyOrderElementsOf(preUpgradeRows)
    }

    @Test
    fun `upgrade with backup registers a readable v2 copy`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_bak")
        val table = createTable(catalog, tableId, 2)
        seed(table, listOf("1" to "one", "2" to "two"))
        val equalityWriter =
            IcebergTableWriterFactory().create(table, "ab-generation-id-1-e", dedupe, schema)
        equalityWriter.write(RecordWrapper(record("2", "ignored"), Operation.DELETE))
        val result = equalityWriter.complete()
        val delta = table.newRowDelta().toBranch("main")
        result.dataFiles().forEach { delta.addRows(it) }
        result.deleteFiles().forEach { delta.addDeletes(it) }
        delta.commit()
        val preUpgradeRows = rows(table)

        IcebergTableUpgrader.upgradeToV3(catalog, tableId, backup = true)

        val backups =
            catalog.listTables(tableId.namespace()).filter {
                it.name().startsWith("${tableId.name()}_v2_backup_")
            }
        assertThat(backups).hasSize(1)
        val backup = catalog.loadTable(backups.single())
        assertThat(tableFormatVersion(backup)).isEqualTo(2)
        assertThat(rows(backup)).containsExactlyInAnyOrderElementsOf(preUpgradeRows)
    }

    @Test
    fun `upgrade converts a mix of equality and position deletes to deletion vectors`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_mixed")
        val table = createTable(catalog, tableId, 2)
        seed(table, listOf("1" to "one", "2" to "two", "3" to "three"))
        val writerFactory = IcebergTableWriterFactory()

        // A legacy equality delete.
        val equalityWriter = writerFactory.create(table, "ab-generation-id-1-e", dedupe, schema)
        equalityWriter.write(RecordWrapper(record("2", "ignored"), Operation.DELETE))
        equalityWriter.write(RecordWrapper(record("4", "four"), Operation.UPDATE))
        val equalityResult = equalityWriter.complete()
        val equalityDelta = table.newRowDelta()
        equalityResult.dataFiles().forEach { equalityDelta.addRows(it) }
        equalityResult.deleteFiles().forEach { equalityDelta.addDeletes(it) }
        equalityDelta.commit()

        // A legacy position delete in a later commit.
        val positional =
            writerFactory.create(
                table,
                "ab-generation-id-2-e",
                dedupe,
                schema,
                positionalDeleteRef = "main",
                positionalDeleteState = PositionalDeleteResolutionState(),
                deleteMode = IcebergDeleteMode.POSITIONAL,
            ) as BasePositionDeltaTaskWriter
        positional.write(RecordWrapper(record("3", "ignored"), Operation.DELETE))
        positional.write(RecordWrapper(record("5", "five"), Operation.UPDATE))
        commitWriter(table, positional)

        val contents = deleteFiles(table).map { it.content() }
        assertThat(contents).contains(FileContent.EQUALITY_DELETES)
        assertThat(contents).contains(FileContent.POSITION_DELETES)
        val preUpgradeRows = rows(table)

        val upgraded = IcebergTableUpgrader.upgradeToV3(catalog, tableId, backup = false)

        assertThat(tableFormatVersion(upgraded)).isEqualTo(3)
        val deletes = deleteFiles(table)
        assertThat(deletes).allMatch { it.format() == FileFormat.PUFFIN }
        assertThat(deletes).allMatch { it.referencedDataFile() != null }
        assertThat(deletes.map { it.referencedDataFile() }).doesNotHaveDuplicates()
        assertThat(rows(table)).containsExactlyInAnyOrderElementsOf(preUpgradeRows)
    }

    @Test
    fun `upgrade works on a non-default branch`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_branch")
        val table = createTable(catalog, tableId, 2)
        seed(table, listOf("1" to "one", "2" to "two"))

        // Commit a legacy equality delete to a non-default branch.
        table.manageSnapshots().createBranch("prod").commit()
        val equalityWriter =
            IcebergTableWriterFactory().create(table, "ab-generation-id-1-e", dedupe, schema)
        equalityWriter.write(RecordWrapper(record("2", "ignored"), Operation.DELETE))
        val result = equalityWriter.complete()
        val delta = table.newRowDelta().toBranch("prod")
        result.deleteFiles().forEach { delta.addDeletes(it) }
        delta.commit()
        table.refresh()

        val upgraded = IcebergTableUpgrader.upgradeToV3(catalog, tableId, backup = false)

        assertThat(tableFormatVersion(upgraded)).isEqualTo(3)
        val remaining =
            upgraded.newScan().useRef("prod").planFiles().use { tasks ->
                tasks.flatMap { it.deletes() }.filter { it.format() != FileFormat.PUFFIN }
            }
        assertThat(remaining).isEmpty()
        val prodRows =
            IcebergGenerics.read(upgraded)
                .useSnapshot(upgraded.refs()["prod"]!!.snapshotId())
                .build()
                .use { records ->
                    records.map { it.getField("id").toString() to it.getField("name").toString() }
                }
        assertThat(prodRows).containsExactlyInAnyOrder("1" to "one")
    }

    @Test
    fun `a failed upgrade leaves the table at v2 with its original delete files`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_fail")
        val table = createTable(catalog, tableId, 2)
        seed(table, listOf("1" to "one", "2" to "two"))

        val equalityWriter =
            IcebergTableWriterFactory().create(table, "ab-generation-id-1-e", dedupe, schema)
        equalityWriter.write(RecordWrapper(record("2", "ignored"), Operation.DELETE))
        val result = equalityWriter.complete()
        val delta = table.newRowDelta()
        result.dataFiles().forEach { delta.addRows(it) }
        result.deleteFiles().forEach { delta.addDeletes(it) }
        delta.commit()
        val originalDeletes = deleteFiles(table).map { it.location() }
        assertThat(originalDeletes).isNotEmpty

        // A catalog that hands back a table whose transactions always fail.
        val failingTable =
            object : Table by table {
                override fun newTransaction(): org.apache.iceberg.Transaction =
                    throw RuntimeException("injected transaction failure")
            }
        val failingCatalog =
            io.mockk.mockk<Catalog> { io.mockk.every { loadTable(tableId) } returns failingTable }

        assertThatThrownBy {
                IcebergTableUpgrader.upgradeToV3(failingCatalog, tableId, backup = false)
            }
            .hasMessageContaining("injected transaction failure")

        table.refresh()
        assertThat(tableFormatVersion(table)).isEqualTo(2)
        assertThat(deleteFiles(table).map { it.location() })
            .containsExactlyInAnyOrderElementsOf(originalDeletes)
    }

    @Test
    fun `delete mode validation rejects mismatched table versions`() {
        val (catalog, _) = catalog()
        val v2Table = createTable(catalog, TableIdentifier.of("db", "v2_table"), 2)
        val v3Table = createTable(catalog, TableIdentifier.of("db", "v3_table"), 3)
        val writerFactory = IcebergTableWriterFactory()

        assertThatThrownBy {
                writerFactory.create(
                    v2Table,
                    "ab-generation-id-1-e",
                    dedupe,
                    schema,
                    deleteMode = IcebergDeleteMode.DELETION_VECTOR,
                )
            }
            .isInstanceOf(ConfigErrorException::class.java)
            .hasMessageContaining("v2")

        assertThatThrownBy {
                writerFactory.create(
                    v3Table,
                    "ab-generation-id-1-e",
                    dedupe,
                    schema,
                    deleteMode = IcebergDeleteMode.POSITIONAL,
                )
            }
            .isInstanceOf(ConfigErrorException::class.java)
            .hasMessageContaining("v3")
    }

    @Test
    fun `upgrade migrates a retained staging branch alongside main`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_staging")
        val table = createTable(catalog, tableId, 2)
        seed(table, listOf("1" to "one", "2" to "two"))
        table.manageSnapshots().createBranch("staging").commit()

        // A failed v2 sync left equality deletes on the staging branch.
        val equalityWriter =
            IcebergTableWriterFactory().create(table, "ab-generation-id-1-e", dedupe, schema)
        equalityWriter.write(RecordWrapper(record("2", "ignored"), Operation.DELETE))
        val result = equalityWriter.complete()
        val delta = table.newRowDelta().toBranch("staging")
        result.dataFiles().forEach { delta.addRows(it) }
        result.deleteFiles().forEach { delta.addDeletes(it) }
        delta.commit()
        table.refresh()

        val upgraded = IcebergTableUpgrader.upgradeToV3(catalog, tableId, backup = false)

        assertThat(tableFormatVersion(upgraded)).isEqualTo(3)
        listOf("main", "staging").forEach { branch ->
            val remaining =
                upgraded.newScan().useRef(branch).planFiles().use { tasks ->
                    tasks.flatMap { it.deletes() }.filter { it.format() != FileFormat.PUFFIN }
                }
            assertThat(remaining).`as`("non-DV deletes on $branch").isEmpty()
            val branchRows =
                IcebergGenerics.read(upgraded)
                    .useSnapshot(upgraded.refs()[branch]!!.snapshotId())
                    .build()
                    .use { records ->
                        records.map {
                            it.getField("id").toString() to it.getField("name").toString()
                        }
                    }
            assertThat(branchRows)
                .`as`("rows on $branch")
                .containsExactlyInAnyOrderElementsOf(
                    // Main never saw the staging-only delete.
                    if (branch == "main") listOf("1" to "one", "2" to "two")
                    else listOf("1" to "one"),
                )
        }
    }

    @Test
    fun `upgrade migrates every branch including ones the caller did not name`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_other_branch")
        val table = createTable(catalog, tableId, 2)
        seed(table, listOf("1" to "one", "2" to "two"))

        // A failed sync left legacy equality deletes on an extra branch.
        table.manageSnapshots().createBranch("other").commit()
        val equalityWriter =
            IcebergTableWriterFactory().create(table, "ab-generation-id-1-e", dedupe, schema)
        equalityWriter.write(RecordWrapper(record("2", "ignored"), Operation.DELETE))
        val result = equalityWriter.complete()
        val delta = table.newRowDelta().toBranch("other")
        result.dataFiles().forEach { delta.addRows(it) }
        result.deleteFiles().forEach { delta.addDeletes(it) }
        delta.commit()
        table.refresh()

        val upgraded = IcebergTableUpgrader.upgradeToV3(catalog, tableId, backup = false)

        assertThat(tableFormatVersion(upgraded)).isEqualTo(3)
        listOf("main", "other").forEach { branch ->
            val remaining =
                upgraded.newScan().useRef(branch).planFiles().use { tasks ->
                    tasks.flatMap { it.deletes() }.filter { it.format() != FileFormat.PUFFIN }
                }
            assertThat(remaining).`as`("non-DV deletes on $branch").isEmpty()
            val branchRows =
                IcebergGenerics.read(upgraded)
                    .useSnapshot(upgraded.refs()[branch]!!.snapshotId())
                    .build()
                    .use { records ->
                        records.map {
                            it.getField("id").toString() to it.getField("name").toString()
                        }
                    }
            assertThat(branchRows)
                .`as`("rows on $branch")
                .containsExactlyInAnyOrderElementsOf(
                    if (branch == "main") listOf("1" to "one", "2" to "two")
                    else listOf("1" to "one"),
                )
        }
    }

    @Test
    fun `upgrade only deletes the partition an equality delete applies to`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_partitioned")
        if (!catalog.namespaceExists(tableId.namespace())) {
            catalog.createNamespace(tableId.namespace())
        }
        val table =
            catalog
                .buildTable(tableId, schema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase(),
                )
                .withProperty(TableProperties.FORMAT_VERSION, "2")
                .withPartitionSpec(
                    org.apache.iceberg.PartitionSpec.builderFor(schema).identity("name").build(),
                )
                .create()
        // The same key exists in two partitions.
        seed(table, listOf("1" to "a", "1" to "b"))

        // The equality delete only applies to partition "a".
        val equalityWriter =
            IcebergTableWriterFactory().create(table, "ab-generation-id-1-e", dedupe, schema)
        equalityWriter.write(RecordWrapper(record("1", "a"), Operation.DELETE))
        val result = equalityWriter.complete()
        val delta = table.newRowDelta()
        result.dataFiles().forEach { delta.addRows(it) }
        result.deleteFiles().forEach { delta.addDeletes(it) }
        delta.commit()
        assertThat(deleteFiles(table).map { it.content() }).contains(FileContent.EQUALITY_DELETES)

        IcebergTableUpgrader.upgradeToV3(catalog, tableId, backup = false)

        assertThat(deleteFiles(table)).allMatch { it.format() == FileFormat.PUFFIN }
        assertThat(rows(table)).containsExactlyInAnyOrder("1" to "b")
    }

    @Test
    fun `v3 dedupe deletes on a timestamp identifier`() {
        val tsSchema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "ts", Types.TimestampType.withoutZone()),
                    Types.NestedField.required(2, "name", Types.StringType.get()),
                ),
                setOf(1),
            )
        fun tsRecord(ts: java.time.LocalDateTime, name: String) =
            GenericRecord.create(tsSchema).apply {
                setField("ts", ts)
                setField("name", name)
            }
        val ts1 = java.time.LocalDateTime.of(2026, 1, 1, 0, 0)
        val ts2 = java.time.LocalDateTime.of(2026, 1, 2, 0, 0)
        val tsDedupe = Dedupe(primaryKey = listOf(listOf("ts")), cursor = emptyList())
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_ts")
        if (!catalog.namespaceExists(tableId.namespace())) {
            catalog.createNamespace(tableId.namespace())
        }
        val table =
            catalog
                .buildTable(tableId, tsSchema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase(),
                )
                .withProperty(TableProperties.FORMAT_VERSION, "3")
                .create()
        val initial =
            IcebergTableWriterFactory().create(table, "ab-generation-id-0-e", Append, tsSchema)
        initial.write(tsRecord(ts1, "one"))
        initial.write(tsRecord(ts2, "two"))
        val initialResult = initial.complete()
        table.newAppend().apply { initialResult.dataFiles().forEach(::appendFile) }.commit()

        val writer =
            IcebergTableWriterFactory()
                .create(
                    table,
                    "ab-generation-id-1-e",
                    tsDedupe,
                    tsSchema,
                    positionalDeleteRef = "main",
                    positionalDeleteState = PositionalDeleteResolutionState(),
                    deleteMode = IcebergDeleteMode.DELETION_VECTOR,
                ) as BasePositionDeltaTaskWriter
        writer.write(RecordWrapper(tsRecord(ts1, "one-updated"), Operation.UPDATE))
        commitWriter(table, writer)

        assertThat(deleteFiles(table)).allMatch { it.format() == FileFormat.PUFFIN }
        table.refresh()
        val rows =
            IcebergGenerics.read(table).build().use { records ->
                records.map { it.getField("name").toString() }.toSet()
            }
        assertThat(rows).containsExactlyInAnyOrder("one-updated", "two")
    }

    @Test
    fun `upgrade resolves timestamp equality keys to deletion vectors`() {
        val tsSchema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "ts", Types.TimestampType.withoutZone()),
                    Types.NestedField.required(2, "name", Types.StringType.get()),
                ),
                setOf(1),
            )
        fun tsRecord(ts: java.time.LocalDateTime, name: String) =
            GenericRecord.create(tsSchema).apply {
                setField("ts", ts)
                setField("name", name)
            }
        val ts1 = java.time.LocalDateTime.of(2026, 1, 1, 0, 0)
        val ts2 = java.time.LocalDateTime.of(2026, 1, 2, 0, 0)
        val tsDedupe = Dedupe(primaryKey = listOf(listOf("ts")), cursor = emptyList())
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_ts_up")
        if (!catalog.namespaceExists(tableId.namespace())) {
            catalog.createNamespace(tableId.namespace())
        }
        val table =
            catalog
                .buildTable(tableId, tsSchema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase(),
                )
                .withProperty(TableProperties.FORMAT_VERSION, "2")
                .create()
        val initial =
            IcebergTableWriterFactory().create(table, "ab-generation-id-0-e", Append, tsSchema)
        initial.write(tsRecord(ts1, "one"))
        initial.write(tsRecord(ts2, "two"))
        val initialResult = initial.complete()
        table.newAppend().apply { initialResult.dataFiles().forEach(::appendFile) }.commit()

        val equalityWriter =
            IcebergTableWriterFactory().create(table, "ab-generation-id-1-e", tsDedupe, tsSchema)
        equalityWriter.write(RecordWrapper(tsRecord(ts1, "ignored"), Operation.DELETE))
        val result = equalityWriter.complete()
        val delta = table.newRowDelta()
        result.dataFiles().forEach { delta.addRows(it) }
        result.deleteFiles().forEach { delta.addDeletes(it) }
        delta.commit()
        assertThat(deleteFiles(table).map { it.content() }).contains(FileContent.EQUALITY_DELETES)

        IcebergTableUpgrader.upgradeToV3(catalog, tableId, backup = false)

        assertThat(deleteFiles(table)).allMatch { it.format() == FileFormat.PUFFIN }
        table.refresh()
        val rows =
            IcebergGenerics.read(table).build().use { records ->
                records.map { it.getField("name").toString() }.toSet()
            }
        assertThat(rows).containsExactlyInAnyOrder("two")
    }

    @Test
    fun `repeated syncs read prior deletion vectors without warnings`() {
        val (catalog, _) = catalog()
        val tableId = TableIdentifier.of("db", "records_dv_reads")
        val table = createTable(catalog, tableId, 3)
        seed(table, listOf("1" to "one", "2" to "two"))
        val writerFactory = IcebergTableWriterFactory()
        val state = PositionalDeleteResolutionState()

        repeat(2) { sync ->
            val writer =
                writerFactory.create(
                    table,
                    "ab-generation-id-${sync + 1}-e",
                    dedupe,
                    schema,
                    positionalDeleteRef = "main",
                    positionalDeleteState = state,
                    deleteMode = IcebergDeleteMode.DELETION_VECTOR,
                ) as BasePositionDeltaTaskWriter
            writer.write(
                RecordWrapper(record("${sync + 1}", "updated-${sync + 1}"), Operation.UPDATE),
            )
            commitWriter(table, writer)
        }

        // The second sync had to read the first sync's DV to merge it.
        assertThat(state.positionDeleteFilesRead.get()).isGreaterThanOrEqualTo(1)
        assertThat(state.unreadablePositionDeleteFiles).isEmpty()
        assertThat(deleteFiles(table)).allMatch { it.format() == FileFormat.PUFFIN }
        assertThat(rows(table)).containsExactlyInAnyOrder("1" to "updated-1", "2" to "updated-2")
    }
}
