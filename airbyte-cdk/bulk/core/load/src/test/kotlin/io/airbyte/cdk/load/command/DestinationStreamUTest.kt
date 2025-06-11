/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.load.data.json.JsonSchemaToAirbyteType
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.Field
import io.mockk.every
import io.mockk.impl.annotations.MockK
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test

private const val A_DESTINATION_OBJECT_NAME = "a_destination_object_name"

class DestinationStreamUTest {
    @MockK(relaxed = true) private lateinit var stream: DestinationStream

    @Test
    fun `test should not truncate incremental append syncs`() {
        every { stream.importType } returns Append
        every { stream.minimumGenerationId } returns 1
        every { stream.generationId } returns 2
        assertFalse(stream.shouldBeTruncatedAtEndOfSync())
    }

    @Test
    fun `test should not truncate overwrite append`() {
        every { stream.importType } returns Overwrite
        every { stream.minimumGenerationId } returns 0
        every { stream.generationId } returns 0
        assertFalse(stream.shouldBeTruncatedAtEndOfSync())
    }

    @Test
    fun `test should truncate overwrite`() {
        every { stream.importType } returns Overwrite
        every { stream.minimumGenerationId } returns 1
        every { stream.generationId } returns 1
        assertFalse(stream.shouldBeTruncatedAtEndOfSync())
    }

    @Test
    fun `test given no destination object name when make then no matching keys`() {
        val configuredStream = a_configured_stream()

        val stream = a_stream_factory().make(configuredStream)

        assertNull(stream.destinationObjectName)
        assertNull(stream.matchingKey)
    }

    @Test
    fun `test given destination object name when make then assemble matching keys`() {
        val configuredStream =
            a_configured_stream()
                .withDestinationObjectName(A_DESTINATION_OBJECT_NAME)
                .withPrimaryKey(
                    listOf<List<String>>(
                        listOf<String>("composite_key_1"),
                        listOf<String>("composite_key_2")
                    )
                )

        val stream = a_stream_factory().make(configuredStream)

        assertEquals(stream.matchingKey, listOf("composite_key_1", "composite_key_2"))
        assertEquals(stream.destinationObjectName, A_DESTINATION_OBJECT_NAME)
    }

    @Test
    fun `test given primary key is nested when make then throw error`() {
        val configuredStream =
            a_configured_stream()
                .withDestinationObjectName(A_DESTINATION_OBJECT_NAME)
                .withPrimaryKey(
                    listOf<List<String>>(listOf<String>("nested_key_root", "nested_key_leaf"))
                )

        assertFailsWith<IllegalArgumentException>(
            block = { a_stream_factory().make(configuredStream) }
        )
    }

    @Test
    fun `test given primary key has empty key when make then throw error`() {
        val configuredStream =
            a_configured_stream()
                .withDestinationObjectName(A_DESTINATION_OBJECT_NAME)
                .withPrimaryKey(
                    listOf<List<String>>(listOf<String>("composite_key_1"), listOf<String>())
                )

        assertFailsWith<IllegalArgumentException>(
            block = { a_stream_factory().make(configuredStream) }
        )
    }

    private fun a_stream_factory(): DestinationStreamFactory =
        DestinationStreamFactory(
            JsonSchemaToAirbyteType(JsonSchemaToAirbyteType.UnionBehavior.DEFAULT),
            namespaceMapper = NamespaceMapper(),
        )

    private fun a_configured_stream(): ConfiguredAirbyteStream =
        ConfiguredAirbyteStream()
            .withStream(
                CatalogHelpers.createAirbyteStream(
                    "a_stream_name",
                    "namespace",
                    Field.of("field_name", JsonSchemaType.STRING),
                ),
            )
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withMinimumGenerationId(0L)
            .withGenerationId(1L)
            .withSyncId(2L)
}
