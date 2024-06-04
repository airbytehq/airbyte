/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import java.io.IOException
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AirbyteSchemaHistoryStorageTest {
    @Test
    @Throws(IOException::class)
    fun testForContentBiggerThan1MBLimit() {
        val contentReadDirectlyFromFile =
            MoreResources.readResource("dbhistory_greater_than_1_mb.dat")

        val schemaHistoryStorageFromUncompressedContent =
            AirbyteSchemaHistoryStorage.initializeDBHistory(
                AirbyteSchemaHistoryStorage.SchemaHistory(
                    Optional.of(Jsons.jsonNode(contentReadDirectlyFromFile)),
                    false
                ),
                true
            )
        val schemaHistoryFromUncompressedContent =
            schemaHistoryStorageFromUncompressedContent.read()

        Assertions.assertTrue(schemaHistoryFromUncompressedContent.isCompressed)
        Assertions.assertNotNull(schemaHistoryFromUncompressedContent.schema)
        Assertions.assertEquals(
            contentReadDirectlyFromFile,
            schemaHistoryStorageFromUncompressedContent.readUncompressed()
        )

        val schemaHistoryStorageFromCompressedContent =
            AirbyteSchemaHistoryStorage.initializeDBHistory(
                AirbyteSchemaHistoryStorage.SchemaHistory(
                    Optional.of(Jsons.jsonNode(schemaHistoryFromUncompressedContent.schema)),
                    true
                ),
                true
            )
        val schemaHistoryFromCompressedContent = schemaHistoryStorageFromCompressedContent.read()

        Assertions.assertTrue(schemaHistoryFromCompressedContent.isCompressed)
        Assertions.assertNotNull(schemaHistoryFromCompressedContent.schema)
        Assertions.assertEquals(
            schemaHistoryFromUncompressedContent.schema,
            schemaHistoryFromCompressedContent.schema
        )
    }

    @Test
    @Throws(IOException::class)
    fun sizeTest() {
        Assertions.assertEquals(
            5.881045341491699,
            AirbyteSchemaHistoryStorage.calculateSizeOfStringInMB(
                MoreResources.readResource("dbhistory_greater_than_1_mb.dat")
            )
        )
        Assertions.assertEquals(
            0.0038671493530273438,
            AirbyteSchemaHistoryStorage.calculateSizeOfStringInMB(
                MoreResources.readResource("dbhistory_less_than_1_mb.dat")
            )
        )
    }

    @Test
    @Throws(IOException::class)
    fun testForContentLessThan1MBLimit() {
        val contentReadDirectlyFromFile = MoreResources.readResource("dbhistory_less_than_1_mb.dat")

        val schemaHistoryStorageFromUncompressedContent =
            AirbyteSchemaHistoryStorage.initializeDBHistory(
                AirbyteSchemaHistoryStorage.SchemaHistory(
                    Optional.of(Jsons.jsonNode(contentReadDirectlyFromFile)),
                    false
                ),
                true
            )
        val schemaHistoryFromUncompressedContent =
            schemaHistoryStorageFromUncompressedContent.read()

        Assertions.assertFalse(schemaHistoryFromUncompressedContent.isCompressed)
        Assertions.assertNotNull(schemaHistoryFromUncompressedContent.schema)
        Assertions.assertEquals(
            contentReadDirectlyFromFile,
            schemaHistoryFromUncompressedContent.schema
        )

        val schemaHistoryStorageFromCompressedContent =
            AirbyteSchemaHistoryStorage.initializeDBHistory(
                AirbyteSchemaHistoryStorage.SchemaHistory(
                    Optional.of(Jsons.jsonNode(schemaHistoryFromUncompressedContent.schema)),
                    false
                ),
                true
            )
        val schemaHistoryFromCompressedContent = schemaHistoryStorageFromCompressedContent.read()

        Assertions.assertFalse(schemaHistoryFromCompressedContent.isCompressed)
        Assertions.assertNotNull(schemaHistoryFromCompressedContent.schema)
        Assertions.assertEquals(
            schemaHistoryFromUncompressedContent.schema,
            schemaHistoryFromCompressedContent.schema
        )
    }
}
