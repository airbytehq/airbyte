/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.TimeUnit
import kotlin.system.measureTimeMillis
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.FileContent
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable

/**
 * Measures the optimized positional delete path with the deletion-vector index off and on. Not a
 * correctness test, and off unless `RUN_DELETE_INDEX_BENCHMARK` is set:
 *
 * ```
 * RUN_DELETE_INDEX_BENCHMARK=1 ./gradlew \
 *   :airbyte-cdk:bulk:toolkits:bulk-cdk-toolkit-load-iceberg-parquet:test \
 *   --tests '*DeleteIndexBenchmark*'
 * ```
 */
@EnabledIfEnvironmentVariable(named = "RUN_DELETE_INDEX_BENCHMARK", matches = ".+")
class DeleteIndexBenchmark {
    data class Shape(
        val name: String,
        val dataFiles: Int,
        val rowsPerDataFile: Int,
        val flushes: Int,
        val updatesPerFlush: Int,
        /** Fraction of the data files that updates are confined to. */
        val hotFileFraction: Double,
        /** Flushes per sync; a new sync drops the in-memory index and rereads statistics. */
        val flushesPerSync: Int,
    )

    data class Result(
        val dataFilesOpened: Int,
        val rowsScanned: Long,
        val positionDeleteFilesRead: Int,
        val deleteFiles: Int,
        val deleteFileBytes: Long,
        val wallTimeMillis: Long,
    )

    @Test
    @Timeout(value = 30, unit = TimeUnit.MINUTES)
    fun benchmark() {
        val shapes =
            listOf(
                Shape("20 flushes, one sync, hot files", 4, 500, 20, 20, 0.25, 20),
                Shape("20 flushes, one sync, uniform", 4, 500, 20, 20, 1.0, 20),
                Shape("4 flushes, one sync, hot files", 4, 500, 4, 100, 0.25, 20),
                Shape("20 flushes, 10 syncs, hot files", 4, 500, 20, 20, 0.25, 2),
                Shape("20 flushes, one sync, wide table", 16, 500, 20, 40, 1.0, 20),
                Shape("20 flushes, one sync, high volume", 8, 4000, 20, 200, 0.25, 20),
                Shape("40 flushes, 40 syncs, hot files", 4, 500, 40, 20, 0.25, 1),
                Shape("40 flushes, 40 syncs, uniform", 4, 500, 40, 20, 1.0, 1),
            )
        val rows = mutableListOf<String>()
        rows.add(
            "| shape | index | files opened | rows scanned | delete files read | " +
                "delete files | delete bytes | wall ms |"
        )
        rows.add("| --- | --- | --- | --- | --- | --- | --- | --- |")
        shapes.forEach { shape ->
            listOf(false, true).forEach { indexed ->
                val result = run(shape, indexed)
                rows.add(
                    "| ${shape.name} | ${if (indexed) "on" else "off"} | " +
                        "${result.dataFilesOpened} | ${result.rowsScanned} | " +
                        "${result.positionDeleteFilesRead} | ${result.deleteFiles} | " +
                        "${result.deleteFileBytes} | ${result.wallTimeMillis} |"
                )
            }
        }
        val report = rows.joinToString("\n")
        println("DELETE INDEX BENCHMARK\n$report")
        Files.writeString(Path.of(System.getProperty("java.io.tmpdir"), "dv-benchmark.md"), report)
    }

    private fun run(shape: Shape, indexed: Boolean): Result {
        val warehouse = Files.createTempDirectory("delete-index-bench")
        try {
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
                        FileFormat.PARQUET.name.lowercase(),
                    )
                    .create()
            val writerFactory = IcebergTableWriterFactory()
            repeat(shape.dataFiles) { fileIndex ->
                val writer = writerFactory.create(table, "ab-generation-id-0-e", Append, schema)
                repeat(shape.rowsPerDataFile) { rowIndex ->
                    writer.write(record(schema, key(fileIndex, rowIndex, shape), "initial"))
                }
                val result = writer.complete()
                table.newAppend().apply { result.dataFiles().forEach(::appendFile) }.commit()
            }
            table.manageSnapshots().createBranch(BRANCH).commit()

            var state = PositionalDeleteResolutionState(deleteIndexEnabled = indexed)
            val hotFiles = maxOf(1, (shape.dataFiles * shape.hotFileFraction).toInt())
            var totalDataFilesOpened = 0
            var totalRowsScanned = 0L
            var totalDeleteFilesRead = 0
            val wallTime = measureTimeMillis {
                repeat(shape.flushes) { flush ->
                    if (flush > 0 && flush % shape.flushesPerSync == 0) {
                        totalDataFilesOpened += state.dataFilesOpened.get()
                        totalRowsScanned += state.rowsScanned.get()
                        totalDeleteFilesRead += state.positionDeleteFilesRead.get()
                        state = PositionalDeleteResolutionState(deleteIndexEnabled = indexed)
                    }
                    flush(
                        table,
                        schema,
                        writerFactory,
                        state,
                        generation = flush + 1,
                        keys =
                            (0 until shape.updatesPerFlush).map { update ->
                                val fileIndex = (flush + update) % hotFiles
                                val rowIndex =
                                    (flush * shape.updatesPerFlush + update) % shape.rowsPerDataFile
                                key(fileIndex, rowIndex, shape)
                            },
                    )
                }
            }
            totalDataFilesOpened += state.dataFilesOpened.get()
            totalRowsScanned += state.rowsScanned.get()
            totalDeleteFilesRead += state.positionDeleteFilesRead.get()

            table.refresh()
            val deleteFiles =
                table.newScan().useSnapshot(table.refs()[BRANCH]!!.snapshotId()).planFiles().use {
                    tasks ->
                    tasks
                        .flatMap { task -> task.deletes() }
                        .filter { it.content() == FileContent.POSITION_DELETES }
                        .associateBy { it.location().toString() }
                }
            return Result(
                dataFilesOpened = totalDataFilesOpened,
                rowsScanned = totalRowsScanned,
                positionDeleteFilesRead = totalDeleteFilesRead,
                deleteFiles = deleteFiles.size,
                deleteFileBytes = deleteFiles.values.sumOf { it.fileSizeInBytes() },
                wallTimeMillis = wallTime,
            )
        } finally {
            warehouse.toFile().deleteRecursively()
        }
    }

    private fun flush(
        table: Table,
        schema: Schema,
        writerFactory: IcebergTableWriterFactory,
        state: PositionalDeleteResolutionState,
        generation: Int,
        keys: List<String>,
    ) {
        val plannedSnapshotId = table.refs()[BRANCH]!!.snapshotId()
        val writer =
            writerFactory.create(
                table,
                "ab-generation-id-$generation-e",
                Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
                schema,
                positionalDeleteRef = BRANCH,
                positionalDeleteState = state,
            )
        keys.forEach { key ->
            writer.write(
                RecordWrapper(record(schema, key, "updated-$generation"), Operation.UPDATE)
            )
        }
        val result = writer.complete()
        IcebergTableCommitter.commit(
            table,
            BRANCH,
            result,
            plannedSnapshotId,
            emptySet(),
            state.deleteIndex,
        )
        table.refresh()
    }

    private companion object {
        const val BRANCH = "staging"

        fun key(fileIndex: Int, rowIndex: Int, shape: Shape): String =
            "key-${fileIndex * shape.rowsPerDataFile + rowIndex}"

        fun record(schema: Schema, id: String, name: String): GenericRecord =
            GenericRecord.create(schema).apply {
                setField("id", id)
                setField("name", name)
            }
    }
}
