/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import java.lang.management.ManagementFactory
import java.lang.management.MemoryType
import java.nio.file.Files
import java.nio.file.Path
import kotlin.system.measureTimeMillis
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable

/**
 * Measures peak heap of a single positional-delete flush as the records per flush and the Parquet
 * row-group size vary, so the connector's records-per-flush limit can be set from a measured
 * bytes-per-row cost rather than a guess. Reports the failure instead of propagating it when a
 * sweep point exhausts the heap, since finding that ceiling is the point.
 *
 * Run it against a deliberately small heap, which needs a plain JVM rather than the Gradle test
 * JVM's fixed 3 GB:
 *
 * ```
 * java -Xmx512m -cp "$(cat classpath.txt)" \
 *   io.airbyte.cdk.load.toolkits.iceberg.parquet.io.FlushMemoryBenchmark
 * ```
 *
 * The test entry point runs the same sweep at whatever heap the test JVM has, and is off unless
 * `RUN_FLUSH_MEMORY_BENCHMARK` is set.
 */
@EnabledIfEnvironmentVariable(named = "RUN_FLUSH_MEMORY_BENCHMARK", matches = ".+")
class FlushMemoryBenchmark {
    @Test
    fun benchmark() {
        println(sweep())
    }

    companion object {
        private const val BRANCH = "staging"

        /** Rows in each pre-existing data file the flush resolves positions against. */
        private const val ROWS_PER_DATA_FILE = 50_000

        private const val DATA_FILES = 8

        private const val MEGABYTE = 1024L * 1024L

        @JvmStatic
        fun main(args: Array<String>) {
            val report = sweep()
            println(report)
            Files.writeString(
                Path.of(System.getProperty("java.io.tmpdir"), "flush-memory-benchmark.md"),
                report,
            )
        }

        private fun sweep(): String {
            val heapMb = Runtime.getRuntime().maxMemory() / MEGABYTE
            val rowGroupSizesMb = listOf(8L, 128L)
            // Stays under TouchedKeys.MAX_CURRENT_WRITES, which fails the flush outright.
            val rowsPerFlushes = listOf(10_000, 100_000, 400_000, 900_000)
            val rows = mutableListOf<String>()
            rows.add("heap $heapMb MB, $DATA_FILES data files of $ROWS_PER_DATA_FILE rows")
            rows.add(
                "| rows per flush | row group MB | live heap MB | peak heap MB | " +
                    "rows scanned (last batch) | files opened (last batch) | wall ms | outcome |"
            )
            rows.add("| --- | --- | --- | --- | --- | --- | --- | --- |")
            rowGroupSizesMb.forEach { rowGroupMb ->
                rowsPerFlushes.forEach { rowsPerFlush ->
                    val result = measure(rowsPerFlush, rowGroupMb)
                    rows.add(
                        "| $rowsPerFlush | $rowGroupMb | ${result.liveHeapMb} | " +
                            "${result.peakHeapMb} | " +
                            "${result.rowsScanned} | ${result.dataFilesOpened} | " +
                            "${result.wallTimeMillis} | ${result.outcome} |"
                    )
                    println(rows.last())
                }
            }
            return rows.joinToString("\n")
        }

        private data class Result(
            val liveHeapMb: Long,
            val peakHeapMb: Long,
            val rowsScanned: Long,
            val dataFilesOpened: Int,
            val wallTimeMillis: Long,
            val outcome: String,
        )

        private fun measure(rowsPerFlush: Int, rowGroupMb: Long): Result {
            val warehouse = Files.createTempDirectory("flush-memory-bench")
            val state = PositionalDeleteResolutionState(deleteIndexEnabled = false)
            var outcome = "ok"
            var wallTime = 0L
            var liveHeapMb = 0L
            try {
                val table = table(warehouse, rowGroupMb)
                val writerFactory = IcebergTableWriterFactory()
                seed(table, writerFactory)
                resetPeakHeap()
                wallTime = measureTimeMillis {
                    try {
                        flush(table, writerFactory, state, rowsPerFlush) {
                            liveHeapMb = liveHeapBytes() / MEGABYTE
                        }
                    } catch (e: OutOfMemoryError) {
                        outcome = "oom: ${e.message}"
                    } catch (e: IllegalStateException) {
                        outcome = "refused: ${e.message}"
                    }
                }
            } catch (e: OutOfMemoryError) {
                outcome = "oom during setup: ${e.message}"
            } finally {
                warehouse.toFile().deleteRecursively()
            }
            return Result(
                liveHeapMb = liveHeapMb,
                peakHeapMb = peakHeapBytes() / MEGABYTE,
                rowsScanned = state.rowsScanned.get(),
                dataFilesOpened = state.dataFilesOpened.get(),
                wallTimeMillis = wallTime,
                outcome = outcome,
            )
        }

        private fun table(warehouse: Path, rowGroupMb: Long): Table {
            val catalog = HadoopCatalog(Configuration(), warehouse.toString())
            val tableId = TableIdentifier.of("db", "records")
            catalog.createNamespace(tableId.namespace())
            return catalog
                .buildTable(tableId, schema())
                .withProperty(
                    TableProperties.DEFAULT_FILE_FORMAT,
                    FileFormat.PARQUET.name.lowercase()
                )
                .withProperty(
                    TableProperties.PARQUET_ROW_GROUP_SIZE_BYTES,
                    (rowGroupMb * MEGABYTE).toString(),
                )
                .create()
        }

        private fun seed(table: Table, writerFactory: IcebergTableWriterFactory) {
            repeat(DATA_FILES) { fileIndex ->
                val writer = writerFactory.create(table, "ab-generation-id-0-e", Append, schema())
                repeat(ROWS_PER_DATA_FILE) { rowIndex ->
                    writer.write(record(key(fileIndex, rowIndex), "initial"))
                }
                val result = writer.complete()
                table.newAppend().apply { result.dataFiles().forEach(::appendFile) }.commit()
            }
            table.manageSnapshots().createBranch(BRANCH).commit()
        }

        private fun flush(
            table: Table,
            writerFactory: IcebergTableWriterFactory,
            state: PositionalDeleteResolutionState,
            rowsPerFlush: Int,
            onRecordsWritten: () -> Unit,
        ) {
            val plannedSnapshotId = table.refs()[BRANCH]!!.snapshotId()
            val writer =
                writerFactory.create(
                    table,
                    "ab-generation-id-1-e",
                    Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
                    schema(),
                    positionalDeleteRef = BRANCH,
                    positionalDeleteState = state,
                    suppressDeletedPositions = true,
                )
            val existingRows = DATA_FILES * ROWS_PER_DATA_FILE
            repeat(rowsPerFlush) { row ->
                // Cycles through the existing keys so every record resolves a position, then spills
                // into new keys once the table's rows are exhausted.
                val key =
                    if (row < existingRows) {
                        key(row / ROWS_PER_DATA_FILE, row % ROWS_PER_DATA_FILE)
                    } else {
                        "key-new-$row"
                    }
                writer.write(RecordWrapper(record(key, "updated"), Operation.UPDATE))
            }
            onRecordsWritten()
            val result = writer.complete()
            IcebergTableCommitter.commit(
                table,
                BRANCH,
                result,
                plannedSnapshotId,
                emptySet(),
                state.deleteIndex,
            )
        }

        private fun heapPools() =
            ManagementFactory.getMemoryPoolMXBeans().filter { it.type == MemoryType.HEAP }

        private fun resetPeakHeap() {
            System.gc()
            heapPools().forEach { it.resetPeakUsage() }
        }

        private fun peakHeapBytes(): Long = heapPools().sumOf { it.peakUsage?.used ?: 0L }

        /**
         * Retained heap rather than allocation: peak usage counts garbage the collector had no
         * reason to reclaim, which tracks the heap ceiling instead of the flush's own footprint.
         */
        private fun liveHeapBytes(): Long {
            repeat(3) { System.gc() }
            return ManagementFactory.getMemoryMXBean().heapMemoryUsage.used
        }

        private fun schema(): Schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "id", Types.StringType.get()),
                    Types.NestedField.required(2, "name", Types.StringType.get()),
                ),
                setOf(1),
            )

        private fun key(fileIndex: Int, rowIndex: Int): String =
            "key-${fileIndex * ROWS_PER_DATA_FILE + rowIndex}"

        private fun record(id: String, name: String): GenericRecord =
            GenericRecord.create(schema()).apply {
                setField("id", id)
                setField("name", name)
            }
    }
}
