/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium

import io.airbyte.cdk.integrations.debezium.internals.AirbyteFileOffsetBackingStore
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class AirbyteFileOffsetBackingStoreTest {
    @Test
    @Throws(IOException::class)
    fun test() {
        val testRoot = Files.createTempDirectory(Path.of("/tmp"), "offset-store-test")

        val bytes = MoreResources.readBytes("test_debezium_offset.dat")
        val templateFilePath = testRoot.resolve("template_offset.dat")
        IOs.writeFile(templateFilePath, bytes)

        val writeFilePath = testRoot.resolve("offset.dat")
        val secondWriteFilePath = testRoot.resolve("offset_2.dat")

        val offsetStore = AirbyteFileOffsetBackingStore(templateFilePath, Optional.empty())
        val offset = offsetStore.read()

        val offsetStore2 = AirbyteFileOffsetBackingStore(writeFilePath, Optional.empty())
        offsetStore2.persist(Jsons.jsonNode(offset))
        val stateFromOffsetStore2 = offsetStore2.read()

        val offsetStore3 = AirbyteFileOffsetBackingStore(secondWriteFilePath, Optional.empty())
        offsetStore3.persist(Jsons.jsonNode(stateFromOffsetStore2))
        val stateFromOffsetStore3 = offsetStore3.read()

        // verify that, after a round trip through the offset store, we get back the same data.
        Assertions.assertEquals(stateFromOffsetStore2, stateFromOffsetStore3)
        // verify that the file written by the offset store is identical to the template file.
        Assertions.assertTrue(
            com.google.common.io.Files.equal(secondWriteFilePath.toFile(), writeFilePath.toFile())
        )
    }

    @Test
    @Throws(IOException::class)
    fun test2() {
        val testRoot = Files.createTempDirectory(Path.of("/tmp"), "offset-store-test")

        val bytes = MoreResources.readBytes("test_debezium_offset.dat")
        val templateFilePath = testRoot.resolve("template_offset.dat")
        IOs.writeFile(templateFilePath, bytes)

        val writeFilePath = testRoot.resolve("offset.dat")
        val secondWriteFilePath = testRoot.resolve("offset_2.dat")

        val offsetStore = AirbyteFileOffsetBackingStore(templateFilePath, Optional.of("orders"))
        val offset = offsetStore.read()

        val offsetStore2 = AirbyteFileOffsetBackingStore(writeFilePath, Optional.of("orders"))
        offsetStore2.persist(Jsons.jsonNode(offset))
        val stateFromOffsetStore2 = offsetStore2.read()

        val offsetStore3 = AirbyteFileOffsetBackingStore(secondWriteFilePath, Optional.of("orders"))
        offsetStore3.persist(Jsons.jsonNode(stateFromOffsetStore2))
        val stateFromOffsetStore3 = offsetStore3.read()

        // verify that, after a round trip through the offset store, we get back the same data.
        Assertions.assertEquals(stateFromOffsetStore2, stateFromOffsetStore3)
        // verify that the file written by the offset store is identical to the template file.
        Assertions.assertTrue(
            com.google.common.io.Files.equal(secondWriteFilePath.toFile(), writeFilePath.toFile())
        )
    }
}
