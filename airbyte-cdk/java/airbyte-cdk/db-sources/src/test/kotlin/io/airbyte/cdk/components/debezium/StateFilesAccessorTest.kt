/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components.debezium

import io.airbyte.commons.json.Jsons
import io.debezium.relational.TableId
import io.debezium.relational.history.HistoryRecord
import io.debezium.relational.history.TableChanges
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import java.io.File
import java.nio.file.Files
import java.time.Instant

class StateFilesAccessorTest {

    @Test
    fun testWorkingDirLifecycle() {
        val dir: File
        StateFilesAccessor().use {
            Assertions.assertNotNull(it.workingDir)
            dir = it.workingDir.toFile()
            Assertions.assertTrue(dir.exists())
            Assertions.assertNotNull(it.offsetFilePath)
            Assertions.assertNotNull(it.schemaFilePath)
            Assertions.assertEquals(it.offsetFilePath.parent.toAbsolutePath(), it.workingDir.toAbsolutePath())
            Assertions.assertEquals(it.schemaFilePath.parent.toAbsolutePath(), it.workingDir.toAbsolutePath())
        }
        Assertions.assertFalse(dir.exists())
    }

    @Test
    fun testWorkingDirContents() {
        StateFilesAccessor().use {
            Assertions.assertNotNull(it.offsetFilePath)
            Assertions.assertNotNull(it.schemaFilePath)
            Assertions.assertEquals(it.offsetFilePath.parent.toAbsolutePath(), it.workingDir.toAbsolutePath())
            Assertions.assertEquals(it.schemaFilePath.parent.toAbsolutePath(), it.workingDir.toAbsolutePath())
            Assertions.assertFalse(it.offsetFilePath.toFile().exists())
            Assertions.assertFalse(it.schemaFilePath.toFile().exists())
        }
    }

    @Test
    fun testOffsetRoundTrip() {
        val key = Jsons.deserialize("""{"key":"k"}""")
        val expectedValue = Jsons.deserialize("""{"key":"k","value":"v"}""")
        val expected = DebeziumComponent.State.Offset(mapOf(Pair(key, expectedValue)))
        val fileContents: ByteArray

        StateFilesAccessor().use {
            it.writeOffset(expected)
            Assertions.assertTrue(it.offsetFilePath.toFile().exists())
            fileContents = Files.readAllBytes(it.offsetFilePath)
        }

        Assertions.assertEquals(149, fileContents.size)

        StateFilesAccessor().use {
            Files.write(it.offsetFilePath, fileContents)
            Assertions.assertTrue(it.offsetFilePath.toFile().exists())
            val actual = it.readUpdatedOffset(DebeziumComponent.State.Offset(mapOf(Pair(key, Jsons.emptyObject()))))
            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testSchemaRoundTrip() {
        val expected = DebeziumComponent.State.Schema(listOf(
                HistoryRecord(
                        mapOf(Pair("source", "wal")),
                        mapOf(Pair("position", "123")),
                        "mydb",
                        "public",
                        "DROP TABLE foo",
                        TableChanges().drop(TableId("mydb", "public", "foo")),
                        Instant.ofEpochSecond(1709185609)),
                HistoryRecord(
                        mapOf(Pair("source", "wal")),
                        mapOf(Pair("position", "456")),
                        "mydb",
                        "public",
                        "DROP TABLE bar",
                        TableChanges().drop(TableId("mydb", "public", "bar")),
                        Instant.ofEpochSecond(1709185610))))
        val fileContents: ByteArray

        StateFilesAccessor().use {
            it.writeSchema(expected)
            Assertions.assertTrue(it.schemaFilePath.toFile().exists())
            fileContents = Files.readAllBytes(it.schemaFilePath)
        }

        Assertions.assertEquals(430, fileContents.size)

        StateFilesAccessor().use {
            Files.write(it.schemaFilePath, fileContents)
            Assertions.assertTrue(it.schemaFilePath.toFile().exists())
            val actual = it.readSchema()
            // Comparisons are slightly more contrived here.
            Assertions.assertEquals(expected.debeziumSchemaHistory.size, actual.debeziumSchemaHistory.size)
            for (idx in 0..< expected.debeziumSchemaHistory.size) {
                val expectedDocument = expected.debeziumSchemaHistory.get(idx).document()
                val actualDocument = actual.debeziumSchemaHistory.get(idx).document()
                Assertions.assertEquals(0, expectedDocument.compareTo(actualDocument))
            }
        }
    }
}