/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.util.Jsons
import io.debezium.relational.TableId
import io.debezium.relational.history.HistoryRecord
import io.debezium.relational.history.TableChanges
import java.io.File
import java.nio.file.Files
import java.time.Instant
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DebeziumStateFilesAccessorTest {

    @Test
    fun testWorkingDirLifecycle() {
        val dir: File
        DebeziumStateFilesAccessor().use {
            Assertions.assertNotNull(it.workingDir)
            dir = it.workingDir.toFile()
            Assertions.assertTrue(dir.exists())
            Assertions.assertNotNull(it.offsetFilePath)
            Assertions.assertNotNull(it.schemaFilePath)
            Assertions.assertEquals(
                it.offsetFilePath.parent.toAbsolutePath(),
                it.workingDir.toAbsolutePath()
            )
            Assertions.assertEquals(
                it.schemaFilePath.parent.toAbsolutePath(),
                it.workingDir.toAbsolutePath()
            )
        }
        Assertions.assertFalse(dir.exists())
    }

    @Test
    fun testWorkingDirContents() {
        DebeziumStateFilesAccessor().use {
            Assertions.assertNotNull(it.offsetFilePath)
            Assertions.assertNotNull(it.schemaFilePath)
            Assertions.assertEquals(
                it.offsetFilePath.parent.toAbsolutePath(),
                it.workingDir.toAbsolutePath()
            )
            Assertions.assertEquals(
                it.schemaFilePath.parent.toAbsolutePath(),
                it.workingDir.toAbsolutePath()
            )
            Assertions.assertFalse(it.offsetFilePath.toFile().exists())
            Assertions.assertFalse(it.schemaFilePath.toFile().exists())
        }
    }

    @Test
    fun testOffsetRoundTrip() {
        val key = Jsons.readTree("""{"key":"k"}""")
        val expectedValue = Jsons.readTree("""{"key":"k","value":"v"}""")
        val expected = DebeziumOffset(mapOf(Pair(key, expectedValue)))
        val fileContents: ByteArray

        DebeziumStateFilesAccessor().use {
            it.writeOffset(expected)
            Assertions.assertTrue(it.offsetFilePath.toFile().exists())
            fileContents = Files.readAllBytes(it.offsetFilePath)
        }

        Assertions.assertEquals(149, fileContents.size)

        DebeziumStateFilesAccessor().use {
            Files.write(it.offsetFilePath, fileContents)
            Assertions.assertTrue(it.offsetFilePath.toFile().exists())
            val actual = it.readUpdatedOffset(DebeziumOffset(mapOf(Pair(key, Jsons.objectNode()))))
            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testSchemaRoundTrip() {
        val expected =
            DebeziumSchemaHistory(
                listOf(
                    HistoryRecord(
                        mapOf(Pair("source", "wal")),
                        mapOf(Pair("position", "123")),
                        "mydb",
                        "public",
                        "DROP TABLE foo",
                        TableChanges().drop(TableId("mydb", "public", "foo")),
                        Instant.ofEpochSecond(1709185609)
                    ),
                    HistoryRecord(
                        mapOf(Pair("source", "wal")),
                        mapOf(Pair("position", "456")),
                        "mydb",
                        "public",
                        "DROP TABLE bar",
                        TableChanges().drop(TableId("mydb", "public", "bar")),
                        Instant.ofEpochSecond(1709185610)
                    )
                )
            )
        val fileContents: ByteArray

        DebeziumStateFilesAccessor().use {
            it.writeSchema(expected)
            Assertions.assertTrue(it.schemaFilePath.toFile().exists())
            fileContents = Files.readAllBytes(it.schemaFilePath)
        }

        Assertions.assertEquals(430, fileContents.size)

        DebeziumStateFilesAccessor().use {
            Files.write(it.schemaFilePath, fileContents)
            Assertions.assertTrue(it.schemaFilePath.toFile().exists())
            val actual = it.readSchema()
            // Comparisons are slightly more contrived here.
            Assertions.assertEquals(expected.wrapped.size, actual.wrapped.size)
            for (idx in 1..expected.wrapped.size) {
                val expectedDocument = expected.wrapped.get(idx - 1).document()
                val actualDocument = actual.wrapped.get(idx - 1).document()
                Assertions.assertEquals(0, expectedDocument.compareTo(actualDocument))
            }
        }
    }
}
