/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.Append
import java.nio.file.Files
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.FileContent
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.types.Types
import org.apache.logging.log4j.Level
import org.apache.logging.log4j.LogManager
import org.apache.logging.log4j.core.LogEvent
import org.apache.logging.log4j.core.LoggerContext
import org.apache.logging.log4j.core.appender.AbstractAppender
import org.apache.logging.log4j.core.layout.PatternLayout
import org.assertj.core.api.Assertions.assertThat
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

        val (index, warningMessages) =
            captureWarnings {
                PositionalDeleteIndexBuilder()
                    .build(
                        table = table,
                        ref = "staging",
                        schema = schema,
                        identifierFieldIds = schema.identifierFieldIds(),
                    )
            }
        assertThat(warningMessages).anyMatch {
            it.contains("Positional delete mode found 1 existing equality-delete file(s)")
        }
        assertThat(warningMessages).anyMatch { it.contains("delete-file-threshold=1") }
        val firstUpdateWriter =
            writerFactory.create(
                table,
                "ab-generation-id-1-e",
                importType,
                schema,
                index,
            )
        firstUpdateWriter.write(RecordWrapper(record(schema, "1", "one-updated"), Operation.UPDATE))
        firstUpdateWriter.write(RecordWrapper(record(schema, "2", "ignored"), Operation.DELETE))
        firstUpdateWriter.write(RecordWrapper(record(schema, "3", "three"), Operation.INSERT))
        commitRowDelta(table, "staging", firstUpdateWriter.complete())
        val firstPositionalSnapshotId = table.refs()["staging"]!!.snapshotId()

        val secondUpdateWriter =
            writerFactory.create(
                table,
                "ab-generation-id-2-e",
                importType,
                schema,
                index,
            )
        secondUpdateWriter.write(
            RecordWrapper(record(schema, "3", "three-updated"), Operation.UPDATE)
        )
        secondUpdateWriter.write(RecordWrapper(record(schema, "1", "ignored"), Operation.DELETE))
        commitRowDelta(table, "staging", secondUpdateWriter.complete())
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

        val rows =
            IcebergGenerics.read(table).useSnapshot(stagingSnapshotId).build().use { records ->
                records.map { it.getField("id") to it.getField("name") }.toSet()
            }
        assertThat(rows).containsExactlyInAnyOrder("3" to "three-updated")
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

    private fun record(schema: Schema, id: String, name: String): GenericRecord =
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
