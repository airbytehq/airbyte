/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.Append
import java.nio.file.Files
import kotlin.system.measureTimeMillis
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.FileContent
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.exceptions.CommitFailedException
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.types.TypeUtil
import org.apache.iceberg.types.Types
import org.apache.logging.log4j.Level
import org.apache.logging.log4j.LogManager
import org.apache.logging.log4j.core.LogEvent
import org.apache.logging.log4j.core.LoggerContext
import org.apache.logging.log4j.core.appender.AbstractAppender
import org.apache.logging.log4j.core.layout.PatternLayout
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.Test

class PositionalDeleteEndToEndTest {
    @Test
    @Suppress("DEPRECATION")
    fun `dedupe update and delete produces positional deletes and expected read`() {
        val warehouse = Files.createTempDirectory("positional-delete-e2e")
        val catalog = HadoopCatalog(Configuration(), warehouse.toString())
        val tableId = TableIdentifier.of("db", "records")
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "id", Types.StringType.get()),
                    Types.NestedField.required(2, "name", Types.StringType.get()),
                ),
                setOf(1),
            )
        catalog.createNamespace(tableId.namespace())
        val table =
            catalog
                .buildTable(tableId, schema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase()
                )
                .withProperty(TableProperties.DELETE_TARGET_FILE_SIZE_BYTES, "104857600")
                .create()
        val importType =
            io.airbyte.cdk.load.command.Dedupe(
                primaryKey = listOf(listOf("id")),
                cursor = emptyList(),
            )
        val writerFactory = IcebergTableWriterFactory()

        val initialWriter =
            writerFactory.create(
                table,
                "ab-generation-id-0-e",
                Append,
                schema,
            )
        initialWriter.write(record(schema, "1", "one"))
        val initialResult = initialWriter.complete()
        table.newAppend().apply { initialResult.dataFiles().forEach(::appendFile) }.commit()
        val secondInitialWriter =
            writerFactory.create(
                table,
                "ab-generation-id-0-e",
                Append,
                schema,
            )
        secondInitialWriter.write(record(schema, "2", "two"))
        val secondInitialResult = secondInitialWriter.complete()
        table.newAppend().apply { secondInitialResult.dataFiles().forEach(::appendFile) }.commit()
        table.manageSnapshots().createBranch("staging").commit()
        val equalityWriter =
            writerFactory.create(
                table,
                "ab-generation-id-0-e",
                importType,
                schema,
            )
        equalityWriter.write(RecordWrapper(record(schema, "1", "one-current"), Operation.UPDATE))
        equalityWriter.write(RecordWrapper(record(schema, "2", "two-current"), Operation.UPDATE))
        commitRowDelta(table, "staging", equalityWriter.complete())
        val initialSnapshotId = table.refs()["staging"]!!.snapshotId()

        val positionalState = PositionalDeleteResolutionState()
        val firstUpdateWriter =
            writerFactory.create(
                table,
                "ab-generation-id-1-e",
                importType,
                schema,
                positionalDeleteRef = "staging",
                positionalDeleteState = positionalState,
                maxTouchedKeys = 2,
            )
        val (_, warningMessages) =
            captureWarnings {
                    firstUpdateWriter.write(
                        RecordWrapper(record(schema, "1", "one-updated"), Operation.UPDATE)
                    )
                    firstUpdateWriter.write(
                        RecordWrapper(record(schema, "2", "ignored"), Operation.DELETE)
                    )
                    firstUpdateWriter.write(
                        RecordWrapper(record(schema, "1", "one-updated-again"), Operation.UPDATE)
                    )
                    firstUpdateWriter.write(
                        RecordWrapper(record(schema, "3", "three"), Operation.INSERT)
                    )
                    firstUpdateWriter.write(
                        RecordWrapper(
                            record(schema, StringBuilder("3"), "three-repeated"),
                            Operation.UPDATE
                        )
                    )
                    firstUpdateWriter.write(
                        RecordWrapper(record(schema, "9", "missing"), Operation.DELETE)
                    )
                    firstUpdateWriter.complete()
                }
                .also { commitRowDelta(table, "staging", it.first) }
        assertThat(warningMessages).anyMatch {
            it.contains("Positional delete mode found 1 existing equality-delete file(s)")
        }
        assertThat(warningMessages).anyMatch { it.contains("delete-file-threshold=1") }
        assertThat(positionalState.dataFilesOpened.get()).isLessThan(4)
        val firstPositionalSnapshotId = table.refs()["staging"]!!.snapshotId()

        val secondUpdateWriter =
            writerFactory.create(
                table,
                "ab-generation-id-2-e",
                importType,
                schema,
                positionalDeleteRef = "staging",
                positionalDeleteState = positionalState,
            )
        secondUpdateWriter.write(
            RecordWrapper(record(schema, "3", "three-updated"), Operation.UPDATE)
        )
        val (_, secondWarningMessages) =
            captureWarnings { secondUpdateWriter.complete() }
                .also { commitRowDelta(table, "staging", it.first) }
        assertThat(secondWarningMessages).noneMatch { it.contains("Positional delete mode found") }
        val secondPositionalSnapshotId = table.refs()["staging"]!!.snapshotId()

        val stagingSnapshotId = secondPositionalSnapshotId
        val initialDeleteFiles =
            table.snapshot(initialSnapshotId)!!.addedDeleteFiles(table.io()).toList()
        assertThat(initialDeleteFiles).isNotEmpty
        val initialDeleteContents =
            initialDeleteFiles.map { deleteFile -> deleteFile.content() }.toSet()
        assertThat(initialDeleteContents).containsOnly(FileContent.EQUALITY_DELETES)
        val positionalDeleteFiles =
            listOf(firstPositionalSnapshotId, secondPositionalSnapshotId).flatMap { snapshotId ->
                table.snapshot(snapshotId)!!.addedDeleteFiles(table.io()).toList()
            }
        assertThat(positionalDeleteFiles).isNotEmpty
        val positionalDeleteContents =
            positionalDeleteFiles.map { deleteFile -> deleteFile.content() }.toSet()
        assertThat(positionalDeleteContents).containsOnly(FileContent.POSITION_DELETES)
        assertThat(
                table.snapshot(firstPositionalSnapshotId)!!.addedDeleteFiles(table.io()).toList()
            )
            .allMatch { it.content() == FileContent.POSITION_DELETES }
        assertThat(
                table.snapshot(secondPositionalSnapshotId)!!.addedDeleteFiles(table.io()).toList()
            )
            .allMatch { it.content() == FileContent.POSITION_DELETES }
        assertThat(positionalDeleteFiles).allMatch { it.referencedDataFile() != null }
        assertThat(positionalDeleteFiles.map { it.referencedDataFile() }.toSet())
            .hasSize(positionalDeleteFiles.size)

        val rows =
            IcebergGenerics.read(table).useSnapshot(stagingSnapshotId).build().use { records ->
                records.map { it.getField("id") to it.getField("name") }.toSet()
            }
        assertThat(rows)
            .containsExactlyInAnyOrder(
                "1" to "one-updated-again",
                "3" to "three-updated",
            )
        warehouse.toFile().deleteRecursively()
    }

    @Test
    @Suppress("DEPRECATION")
    fun `suppresses positions across multiple prior position delete files`() {
        val warehouse = Files.createTempDirectory("positional-delete-suppression")
        val catalog = HadoopCatalog(Configuration(), warehouse.toString())
        val tableId = TableIdentifier.of("db", "suppression")
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "id", Types.StringType.get()),
                    Types.NestedField.required(2, "name", Types.StringType.get()),
                ),
                setOf(1),
            )
        catalog.createNamespace(tableId.namespace())
        val table =
            catalog
                .buildTable(tableId, schema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase()
                )
                .create()
        val writerFactory = IcebergTableWriterFactory()
        val initialWriter = writerFactory.create(table, "ab-generation-id-0-e", Append, schema)
        listOf("a", "b", "c").forEach { id -> initialWriter.write(record(schema, id, "old-$id")) }
        val initialResult = initialWriter.complete()
        table.newAppend().apply { initialResult.dataFiles().forEach(::appendFile) }.commit()
        table.manageSnapshots().createBranch("staging").commit()
        val state = PositionalDeleteResolutionState()
        val importType = io.airbyte.cdk.load.command.Dedupe(listOf(listOf("id")), emptyList())

        val firstPlanned = table.refs()["staging"]!!.snapshotId()
        val firstWriter =
            writerFactory.create(
                table,
                "ab-generation-id-1-e",
                importType,
                schema,
                positionalDeleteRef = "staging",
                positionalDeleteState = state,
            )
        firstWriter.write(RecordWrapper(record(schema, "a", "new-a"), Operation.UPDATE))
        val firstResult = firstWriter.complete()
        IcebergTableCommitter.commit(
            table,
            "staging",
            firstResult,
            firstPlanned,
            IcebergTableCommitter.fullySupersededDataFiles(table, firstPlanned, firstResult),
        )

        val secondPlanned = table.refs()["staging"]!!.snapshotId()
        val secondWriter =
            writerFactory.create(
                table,
                "ab-generation-id-2-e",
                importType,
                schema,
                positionalDeleteRef = "staging",
                positionalDeleteState = state,
            )
        secondWriter.write(RecordWrapper(record(schema, "b", "new-b"), Operation.UPDATE))
        val secondResult = secondWriter.complete()
        assertThat(secondResult.deleteFiles()).hasSize(1)
        IcebergTableCommitter.commit(
            table,
            "staging",
            secondResult,
            secondPlanned,
            IcebergTableCommitter.fullySupersededDataFiles(table, secondPlanned, secondResult),
        )

        val thirdPlanned = table.refs()["staging"]!!.snapshotId()
        val thirdWriter =
            writerFactory.create(
                table,
                "ab-generation-id-3-e",
                importType,
                schema,
                positionalDeleteRef = "staging",
                positionalDeleteState = state,
            )
        thirdWriter.write(RecordWrapper(record(schema, "c", "new-c"), Operation.UPDATE))
        val thirdResult = thirdWriter.complete()
        assertThat(thirdResult.deleteFiles()).isEmpty()
        IcebergTableCommitter.commit(
            table,
            "staging",
            thirdResult,
            thirdPlanned,
            IcebergTableCommitter.fullySupersededDataFiles(table, thirdPlanned, thirdResult),
        )

        val rows =
            IcebergGenerics.read(table)
                .useSnapshot(table.refs()["staging"]!!.snapshotId())
                .build()
                .use { records -> records.map { it.getField("name") }.toSet() }
        assertThat(rows).containsExactlyInAnyOrder("new-a", "new-b", "new-c")
        warehouse.toFile().deleteRecursively()
    }

    @Test
    @Suppress("DEPRECATION")
    fun `drops a data file only when every live position is superseded`() {
        val warehouse = Files.createTempDirectory("positional-delete-full-file")
        val catalog = HadoopCatalog(Configuration(), warehouse.toString())
        val tableId = TableIdentifier.of("db", "full_file")
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "id", Types.StringType.get()),
                    Types.NestedField.required(2, "name", Types.StringType.get()),
                ),
                setOf(1),
            )
        catalog.createNamespace(tableId.namespace())
        val table =
            catalog
                .buildTable(tableId, schema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase()
                )
                .create()
        val writerFactory = IcebergTableWriterFactory()
        val initialWriter = writerFactory.create(table, "ab-generation-id-0-e", Append, schema)
        listOf("a", "b").forEach { id -> initialWriter.write(record(schema, id, "old-$id")) }
        val initialResult = initialWriter.complete()
        table.newAppend().apply { initialResult.dataFiles().forEach(::appendFile) }.commit()
        table.manageSnapshots().createBranch("staging").commit()
        val planned = table.refs()["staging"]!!.snapshotId()
        val state = PositionalDeleteResolutionState()
        val writer =
            writerFactory.create(
                table,
                "ab-generation-id-1-e",
                io.airbyte.cdk.load.command.Dedupe(listOf(listOf("id")), emptyList()),
                schema,
                positionalDeleteRef = "staging",
                positionalDeleteState = state,
            )
        writer.write(RecordWrapper(record(schema, "a", "new-a"), Operation.UPDATE))
        writer.write(RecordWrapper(record(schema, "b", "new-b"), Operation.UPDATE))
        val result = writer.complete()
        assertThat(result.deleteFiles()).isEmpty()
        assertThat(result.referencedDataFiles())
            .containsExactly(initialResult.dataFiles().single().location())
        IcebergTableCommitter.commit(
            table,
            "staging",
            result,
            planned,
            IcebergTableCommitter.fullySupersededDataFiles(table, planned, result),
        )
        assertThat(
                table.newScan().useRef("staging").planFiles().use {
                    it.map { task -> task.file() }.toList()
                }
            )
            .noneMatch { it.location() == initialResult.dataFiles().single().location() }
        warehouse.toFile().deleteRecursively()
    }

    @Test
    @Suppress("DEPRECATION")
    fun `rejects a stale planned snapshot`() {
        val warehouse = Files.createTempDirectory("positional-delete-stale-snapshot")
        val catalog = HadoopCatalog(Configuration(), warehouse.toString())
        val tableId = TableIdentifier.of("db", "stale_snapshot")
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "id", Types.StringType.get()),
                    Types.NestedField.required(2, "name", Types.StringType.get()),
                ),
                setOf(1),
            )
        catalog.createNamespace(tableId.namespace())
        val table =
            catalog
                .buildTable(tableId, schema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase()
                )
                .create()
        val writerFactory = IcebergTableWriterFactory()
        val initialWriter = writerFactory.create(table, "ab-generation-id-0-e", Append, schema)
        initialWriter.write(record(schema, "a", "old-a"))
        val initialResult = initialWriter.complete()
        table.newAppend().apply { initialResult.dataFiles().forEach(::appendFile) }.commit()
        table.manageSnapshots().createBranch("staging").commit()
        val planned = table.refs()["staging"]!!.snapshotId()
        val state = PositionalDeleteResolutionState()
        val writer =
            writerFactory.create(
                table,
                "ab-generation-id-1-e",
                io.airbyte.cdk.load.command.Dedupe(listOf(listOf("id")), emptyList()),
                schema,
                positionalDeleteRef = "staging",
                positionalDeleteState = state,
            )
        writer.write(RecordWrapper(record(schema, "a", "new-a"), Operation.UPDATE))
        val result = writer.complete()
        val concurrentWriter = writerFactory.create(table, "ab-generation-id-2-e", Append, schema)
        concurrentWriter.write(record(schema, "b", "concurrent-b"))
        val concurrentResult = concurrentWriter.complete()
        table
            .newAppend()
            .toBranch("staging")
            .apply { concurrentResult.dataFiles().forEach(::appendFile) }
            .commit()
        assertThatThrownBy {
                IcebergTableCommitter.commit(
                    table,
                    "staging",
                    result,
                    planned,
                    IcebergTableCommitter.fullySupersededDataFiles(table, planned, result),
                )
            }
            .isInstanceOf(CommitFailedException::class.java)
        warehouse.toFile().deleteRecursively()
    }

    @Test
    @Suppress("DEPRECATION")
    fun `row position remains physical when an earlier row group is filtered`() {
        val warehouse = Files.createTempDirectory("positional-delete-row-groups")
        val catalog = HadoopCatalog(Configuration(), warehouse.toString())
        val tableId = TableIdentifier.of("db", "row_groups")
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "id", Types.StringType.get()),
                    Types.NestedField.required(2, "name", Types.StringType.get()),
                ),
                setOf(1),
            )
        catalog.createNamespace(tableId.namespace())
        val table =
            catalog
                .buildTable(tableId, schema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase()
                )
                .withProperty(TableProperties.PARQUET_ROW_GROUP_SIZE_BYTES, "1")
                .withProperty(TableProperties.PARQUET_ROW_GROUP_CHECK_MIN_RECORD_COUNT, "1")
                .withProperty(TableProperties.PARQUET_ROW_GROUP_CHECK_MAX_RECORD_COUNT, "1")
                .withProperty(TableProperties.DELETE_TARGET_FILE_SIZE_BYTES, "104857600")
                .create()
        val writerFactory = IcebergTableWriterFactory()
        val initialWriter = writerFactory.create(table, "ab-generation-id-0-e", Append, schema)
        (1..4).forEach { id -> initialWriter.write(record(schema, id.toString(), "old-$id")) }
        val initialResult = initialWriter.complete()
        table.newAppend().apply { initialResult.dataFiles().forEach(::appendFile) }.commit()
        table.manageSnapshots().createBranch("staging").commit()

        val state = PositionalDeleteResolutionState()
        val updateWriter =
            writerFactory.create(
                table = table,
                generationId = "ab-generation-id-1-e",
                importType =
                    io.airbyte.cdk.load.command.Dedupe(
                        primaryKey = listOf(listOf("id")),
                        cursor = emptyList(),
                    ),
                schema = schema,
                positionalDeleteRef = "staging",
                positionalDeleteState = state,
            )
        updateWriter.write(RecordWrapper(record(schema, "4", "new-4"), Operation.UPDATE))
        val result = updateWriter.complete()
        commitRowDelta(table, "staging", result)

        val rows =
            IcebergGenerics.read(table)
                .useSnapshot(table.refs()["staging"]!!.snapshotId())
                .build()
                .use { records -> records.map { it.getField("id") to it.getField("name") }.toSet() }
        assertThat(rows)
            .containsExactlyInAnyOrder(
                "1" to "old-1",
                "2" to "old-2",
                "3" to "old-3",
                "4" to "new-4",
            )
        assertThat(result.deleteFiles()).hasSize(1)
        assertThat(result.deleteFiles().single().content()).isEqualTo(FileContent.POSITION_DELETES)
        warehouse.toFile().deleteRecursively()
    }

    @Test
    @Suppress("DEPRECATION")
    fun `large realistic flush still prunes early row groups`() {
        val warehouse = Files.createTempDirectory("positional-delete-large-in")
        val catalog = HadoopCatalog(Configuration(), warehouse.toString())
        val tableId = TableIdentifier.of("db", "large_in")
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "id", Types.IntegerType.get()),
                    Types.NestedField.required(2, "name", Types.StringType.get()),
                ),
                setOf(1),
            )
        catalog.createNamespace(tableId.namespace())
        val table =
            catalog
                .buildTable(tableId, schema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase()
                )
                .withProperty(TableProperties.PARQUET_ROW_GROUP_SIZE_BYTES, "1")
                .withProperty(TableProperties.PARQUET_ROW_GROUP_CHECK_MIN_RECORD_COUNT, "1")
                .withProperty(TableProperties.PARQUET_ROW_GROUP_CHECK_MAX_RECORD_COUNT, "1")
                .create()
        val writerFactory = IcebergTableWriterFactory()
        val initialWriter = writerFactory.create(table, "ab-generation-id-0-e", Append, schema)
        (1..200).forEach { id -> initialWriter.write(record(schema, id, "early-$id")) }
        (1001..1201).forEach { id -> initialWriter.write(record(schema, id, "old-$id")) }
        val initialResult = initialWriter.complete()
        table.newAppend().apply { initialResult.dataFiles().forEach(::appendFile) }.commit()
        table.manageSnapshots().createBranch("staging").commit()

        val state = PositionalDeleteResolutionState()
        val updateWriter =
            writerFactory.create(
                table = table,
                generationId = "ab-generation-id-1-e",
                importType =
                    io.airbyte.cdk.load.command.Dedupe(
                        primaryKey = listOf(listOf("id")),
                        cursor = emptyList(),
                    ),
                schema = schema,
                positionalDeleteRef = "staging",
                positionalDeleteState = state,
            )
        (1001..1201).forEach { id ->
            updateWriter.write(RecordWrapper(record(schema, id, "new-$id"), Operation.UPDATE))
        }
        val result = updateWriter.complete()
        commitRowDelta(table, "staging", result)

        val rows =
            IcebergGenerics.read(table)
                .useSnapshot(table.refs()["staging"]!!.snapshotId())
                .build()
                .use { records -> records.map { it.getField("id") to it.getField("name") }.toSet() }
        assertThat(rows).hasSize(401)
        assertThat(rows).contains(1 to "early-1")
        assertThat(rows).contains(1201 to "new-1201")
        assertThat(rows).doesNotContain(1201 to "old-1201")
        assertThat(state.dataFilesOpened.get()).isEqualTo(1)
        assertThat(state.rowsScanned.get()).isEqualTo(201)
        assertThat(result.deleteFiles()).hasSize(1)
        warehouse.toFile().deleteRecursively()
    }

    @Test
    fun `monotonic 200 sub-range benchmark`() {
        runSubRangeBenchmark("monotonic", 200)
    }

    @Test
    fun `monotonic 5000 sub-range benchmark`() {
        runSubRangeBenchmark("monotonic", 5_000)
    }

    @Test
    fun `monotonic 50000 sub-range benchmark`() {
        runSubRangeBenchmark("monotonic", 50_000)
    }

    @Test
    fun `clustered 200 sub-range benchmark`() {
        runSubRangeBenchmark("clustered", 200)
    }

    @Test
    fun `clustered 5000 sub-range benchmark`() {
        runSubRangeBenchmark("clustered", 5_000)
    }

    @Test
    fun `clustered 50000 sub-range benchmark`() {
        runSubRangeBenchmark("clustered", 50_000)
    }

    @Test
    fun `uniform 200 sub-range benchmark`() {
        runSubRangeBenchmark("uniform", 200)
    }

    @Test
    fun `uniform 5000 sub-range benchmark`() {
        runSubRangeBenchmark("uniform", 5_000)
    }

    @Test
    fun `uniform 50000 sub-range benchmark`() {
        runSubRangeBenchmark("uniform", 50_000)
    }

    @Suppress("DEPRECATION")
    private fun runSubRangeBenchmark(
        distribution: String,
        size: Int,
    ) {
        val warehouse = Files.createTempDirectory("positional-delete-benchmark")
        val catalog = HadoopCatalog(Configuration(), warehouse.toString())
        val tableId = TableIdentifier.of("db", "benchmark")
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "id", Types.IntegerType.get()),
                    Types.NestedField.required(2, "name", Types.StringType.get()),
                ),
                setOf(1),
            )
        catalog.createNamespace(tableId.namespace())
        val table =
            catalog
                .buildTable(tableId, schema)
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase()
                )
                .withProperty(TableProperties.PARQUET_ROW_GROUP_SIZE_BYTES, "1")
                .withProperty(TableProperties.PARQUET_ROW_GROUP_CHECK_MIN_RECORD_COUNT, "1")
                .withProperty(TableProperties.PARQUET_ROW_GROUP_CHECK_MAX_RECORD_COUNT, "1")
                .create()
        val writer =
            IcebergTableWriterFactory().create(table, "ab-generation-id-0-e", Append, schema)
        (0 until 50_000).forEach { id -> writer.write(record(schema, id, "row-$id")) }
        val result = writer.complete()
        table.newAppend().apply { result.dataFiles().forEach(::appendFile) }.commit()
        table.manageSnapshots().createBranch("staging").commit()
        val keyType = TypeUtil.select(schema, setOf(1)).asStruct()
        listOf(1, 2, 4, 8, 16).forEach { subRanges ->
            val state = PositionalDeleteResolutionState()
            val touched = TouchedKeys(keyType, Int.MAX_VALUE)
            (0 until size).forEach { index ->
                val key = GenericRecord.create(keyType)
                val id =
                    when (distribution) {
                        "monotonic" -> {
                            val inserts = size / 2
                            if (index < inserts) {
                                50_000 - inserts + index
                            } else {
                                val updates = index - inserts
                                val updateRange = 50_000 - inserts
                                50_000 - 1 - (updates * (updates + 1) / 2 % updateRange)
                            }
                        }
                        "clustered" -> (index % 4) * (50_000 / 4) + index / 4
                        else -> index * (50_000 / size)
                    }
                key.setField("id", id)
                touched.markDeleted(key)
            }
            val finder =
                SupersededRowFinder(
                    table,
                    schema,
                    setOf(1),
                    state,
                    0,
                    subRanges,
                )
            val elapsed = measureTimeMillis { finder.find(touched, "staging").count() }
            println(
                "benchmark distribution=$distribution size=$size " +
                    "subRanges=$subRanges rowsScanned=${state.rowsScanned.get()} " +
                    "elapsedMs=$elapsed"
            )
            if (distribution == "clustered" && subRanges == 4) {
                assertThat(state.rowsScanned.get()).isLessThanOrEqualTo(size.toLong())
            }
        }
        warehouse.toFile().deleteRecursively()
    }

    private fun commitRowDelta(
        table: org.apache.iceberg.Table,
        branch: String,
        result: org.apache.iceberg.io.WriteResult,
    ) {
        val validationSnapshotId = table.refs()[branch]!!.snapshotId()
        table
            .newRowDelta()
            .toBranch(branch)
            .validateFromSnapshot(validationSnapshotId)
            .validateDeletedFiles()
            .validateNoConflictingDataFiles()
            .validateNoConflictingDeleteFiles()
            .apply {
                result.dataFiles().forEach(::addRows)
                result.deleteFiles().forEach(::addDeletes)
            }
            .commit()
    }

    private fun record(schema: Schema, id: CharSequence, name: String): GenericRecord =
        GenericRecord.create(schema).apply {
            setField("id", id)
            setField("name", name)
        }

    private fun record(schema: Schema, id: Int, name: String): GenericRecord =
        GenericRecord.create(schema).apply {
            setField("id", id)
            setField("name", name)
        }

    private fun <T> captureWarnings(action: () -> T): Pair<T, List<String>> {
        val context = LogManager.getContext(false) as LoggerContext
        val rootLogger = context.rootLogger
        val appender = CapturingAppender()
        appender.start()
        rootLogger.addAppender(appender)
        val previousLevel = rootLogger.level
        rootLogger.level = Level.WARN
        return try {
            val result = action()
            result to appender.messages.toList()
        } finally {
            rootLogger.level = previousLevel
            rootLogger.removeAppender(appender)
            appender.stop()
        }
    }

    @Suppress("DEPRECATION")
    private class CapturingAppender :
        AbstractAppender(
            "positional-delete-test",
            null,
            PatternLayout.createDefaultLayout(),
            true,
        ) {
        val messages = mutableListOf<String>()

        override fun append(event: LogEvent) {
            messages += event.message.formattedMessage
        }
    }
}
