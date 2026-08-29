/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import java.nio.file.Files
import java.nio.file.Path
import java.util.UUID
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.DataFile
import org.apache.iceberg.DeleteFile
import org.apache.iceberg.FileContent
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.StatisticsFile
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericFileWriterFactory
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.data.Record
import org.apache.iceberg.deletes.PositionDelete
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.io.OutputFileFactory
import org.apache.iceberg.io.WriteResult
import org.apache.iceberg.puffin.StandardBlobTypes
import org.apache.iceberg.types.Types
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

/**
 * Covers the deletion-vector index: that it lets a flush skip reading prior delete files, and that
 * every way it can stop describing the table falls back to reading those files instead.
 */
class DeleteIndexEndToEndTest {
    @Test
    fun `index lets a later flush skip reading prior delete files`() {
        val fixture = fixture(deleteIndexEnabled = true)
        val firstDeletes = fixture.update("1", "one-updated")
        assertThat(firstDeletes).allMatch { it.content() == FileContent.POSITION_DELETES }
        assertThat(fixture.indexedDataFiles()).contains(fixture.initialDataFile.location())

        fixture.update("2", "two-updated")
        assertThat(fixture.state.positionDeleteFilesRead.get()).isZero()

        // A later sync starts with no in-memory state, so this reads the published index back.
        fixture.startNewSync()
        fixture.update("3", "three-updated")
        assertThat(fixture.state.positionDeleteFilesRead.get()).isZero()
        assertThat(fixture.rows())
            .containsExactlyInAnyOrder(
                "1" to "one-updated",
                "2" to "two-updated",
                "3" to "three-updated",
            )
        fixture.close()
    }

    @Test
    fun `no index is written or read when the index is disabled`() {
        val fixture = fixture(deleteIndexEnabled = false)
        fixture.update("1", "one-updated")
        assertThat(fixture.indexStatisticsFiles()).isEmpty()

        fixture.update("2", "two-updated")
        assertThat(fixture.state.positionDeleteFilesRead.get()).isPositive()
        assertThat(fixture.rows())
            .containsExactlyInAnyOrder(
                "1" to "one-updated",
                "2" to "two-updated",
                "3" to "three",
            )
        fixture.close()
    }

    @Test
    fun `a delete file added by another writer invalidates the index`() {
        val fixture = fixture(deleteIndexEnabled = true)
        fixture.update("1", "one-updated")
        // Another writer deletes a row the index does not know about, so the index no longer
        // accounts for every delete file the next scan will plan.
        fixture.deleteRowExternally(position = 2)

        fixture.update("2", "two-updated")
        assertThat(fixture.state.positionDeleteFilesRead.get()).isPositive()
        assertThat(fixture.rows())
            .containsExactlyInAnyOrder("1" to "one-updated", "2" to "two-updated")
        fixture.close()
    }

    @Test
    fun `an unreadable index falls back to reading delete files`() {
        val fixture = fixture(deleteIndexEnabled = true)
        fixture.update("1", "one-updated")
        fixture.corruptIndex()
        fixture.startNewSync()

        fixture.update("2", "two-updated")
        assertThat(fixture.state.positionDeleteFilesRead.get()).isPositive()
        assertThat(fixture.rows())
            .containsExactlyInAnyOrder(
                "1" to "one-updated",
                "2" to "two-updated",
                "3" to "three",
            )
        fixture.close()
    }

    private fun fixture(deleteIndexEnabled: Boolean): Fixture {
        val warehouse = Files.createTempDirectory("delete-index-e2e")
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
        val initialWriter = writerFactory.create(table, "ab-generation-id-0-e", Append, schema)
        listOf("1" to "one", "2" to "two", "3" to "three").forEach { (id, name) ->
            initialWriter.write(record(schema, id, name))
        }
        val initialResult = initialWriter.complete()
        table.newAppend().apply { initialResult.dataFiles().forEach(::appendFile) }.commit()
        table.manageSnapshots().createBranch(BRANCH).commit()
        return Fixture(
            warehouse = warehouse,
            table = table,
            schema = schema,
            writerFactory = writerFactory,
            deleteIndexEnabled = deleteIndexEnabled,
            initialDataFile = initialResult.dataFiles().single(),
        )
    }

    private class Fixture(
        val warehouse: Path,
        val table: Table,
        val schema: Schema,
        val writerFactory: IcebergTableWriterFactory,
        val deleteIndexEnabled: Boolean,
        val initialDataFile: DataFile,
    ) {
        var state = PositionalDeleteResolutionState(deleteIndexEnabled = deleteIndexEnabled)
            private set

        private var generation = 0

        /** Drops the in-memory state, as a later sync of the same stream would. */
        fun startNewSync() {
            state = PositionalDeleteResolutionState(deleteIndexEnabled = deleteIndexEnabled)
        }

        /** Runs one dedupe flush that updates [id], returning the delete files it committed. */
        fun update(id: String, name: String): List<DeleteFile> {
            generation += 1
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
            writer.write(RecordWrapper(record(schema, id, name), Operation.UPDATE))
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
            return result.deleteFiles().toList()
        }

        /** Deletes one row of the initial data file outside of the indexed write path. */
        fun deleteRowExternally(position: Long) {
            val genericWriterFactory =
                GenericFileWriterFactory.Builder(table)
                    .dataSchema(schema)
                    .writerProperties(table.properties())
                    .build()
            val outputFileFactory =
                OutputFileFactory.builderFor(table, 0, 1L)
                    .defaultSpec(table.spec())
                    .operationId(UUID.randomUUID().toString())
                    .format(FileFormat.PARQUET)
                    .suffix("external")
                    .build()
            val writer =
                genericWriterFactory.newPositionDeleteWriter(
                    outputFileFactory.newOutputFile(table.spec(), null),
                    table.spec(),
                    null,
                )
            val delete = PositionDelete.create<Record>()
            delete.set(initialDataFile.location().toString(), position)
            writer.write(delete)
            writer.close()
            commit(WriteResult.builder().addDeleteFiles(writer.result().deleteFiles()).build())
        }

        /** Truncates the index blobs so reading them fails. */
        fun corruptIndex() {
            indexStatisticsFiles().forEach { file ->
                Path.of(java.net.URI.create("file:${file.path()}").path).toFile().writeText("")
            }
        }

        fun indexStatisticsFiles(): List<StatisticsFile> {
            table.refresh()
            return table.statisticsFiles().filter { file ->
                file.blobMetadata().any { it.type() == StandardBlobTypes.DV_V1 }
            }
        }

        fun indexedDataFiles(): Set<String> =
            indexStatisticsFiles()
                .flatMap { file -> file.blobMetadata() }
                .mapNotNull { it.properties()[DeleteIndexStatistics.REFERENCED_DATA_FILE_PROPERTY] }
                .toSet()

        fun rows(): Set<Pair<Any?, Any?>> =
            IcebergGenerics.read(table)
                .useSnapshot(table.refs()[BRANCH]!!.snapshotId())
                .build()
                .use { records -> records.map { it.getField("id") to it.getField("name") }.toSet() }

        fun close() {
            warehouse.toFile().deleteRecursively()
        }

        private fun commit(result: WriteResult) {
            table
                .newRowDelta()
                .toBranch(BRANCH)
                .validateFromSnapshot(table.refs()[BRANCH]!!.snapshotId())
                .validateDeletedFiles()
                .validateNoConflictingDataFiles()
                .validateNoConflictingDeleteFiles()
                .apply {
                    result.dataFiles().forEach(::addRows)
                    result.deleteFiles().forEach(::addDeletes)
                }
                .commit()
            table.refresh()
        }
    }

    private companion object {
        const val BRANCH = "staging"

        fun record(schema: Schema, id: String, name: String): GenericRecord =
            GenericRecord.create(schema).apply {
                setField("id", id)
                setField("name", name)
            }
    }
}
