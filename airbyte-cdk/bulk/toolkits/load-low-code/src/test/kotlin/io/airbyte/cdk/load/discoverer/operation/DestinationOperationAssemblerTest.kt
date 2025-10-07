/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.operation

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.discoverer.destinationobject.DestinationObject
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.getBodyOrEmpty
import io.airbyte.cdk.util.Jsons
import io.mockk.every
import io.mockk.mockk
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class DestinationOperationAssemblerTest {

    lateinit var schemaRequester: HttpRequester
    lateinit var insertionMethod: InsertionMethod
    lateinit var property: DiscoveredProperty

    companion object {
        const val PROPERTY_PATH = "propertyPath"
        const val OBJECT_NAME = "objectName"
        val NO_SCHEMA_REQUESTER = null
    }

    @BeforeEach
    fun setUp() {
        schemaRequester = mockk()
        property = mockk(relaxed = true)
        insertionMethod = mockk()
        every { insertionMethod.getImportType() } returns SoftDelete
        every { insertionMethod.requiresMatchingKey() } returns false
        every { insertionMethod.createProperty(any()) } returns property
    }

    @Test
    internal fun `test given object has available properties when assemble then return factory result`() {
        every { property.isAvailable() } returns true
        val assembler =
            DestinationOperationAssembler(
                listOf(PROPERTY_PATH),
                listOf(insertionMethod),
                NO_SCHEMA_REQUESTER,
            )

        val operations =
            assembler.assemble(DestinationObject(OBJECT_NAME, apiRepresentationWithOneProperty()))

        assertEquals(1, operations.size)
    }

    @Test
    internal fun `test given no available properties when assemble then return no operation`() {
        every { property.isAvailable() } returns false
        val assembler =
            DestinationOperationAssembler(
                listOf(PROPERTY_PATH),
                listOf(insertionMethod),
                NO_SCHEMA_REQUESTER,
            )

        val operations =
            assembler.assemble(DestinationObject(OBJECT_NAME, apiRepresentationWithOneProperty()))

        assertEquals(0, operations.size)
    }

    @Test
    internal fun `test given no properties in apiRepresentation and no schema requester when assemble then throw exception`() {
        val assembler =
            DestinationOperationAssembler(
                listOf(PROPERTY_PATH),
                listOf(insertionMethod),
                NO_SCHEMA_REQUESTER,
            )

        assertFailsWith<IllegalStateException> {
            assembler.assemble(DestinationObject(OBJECT_NAME, Jsons.objectNode()))
        }
    }

    @Test
    internal fun `test given no properties in apiRepresentation and schema requester when assemble then fetch schema`() {
        val response = mockk<Response>(relaxed = true)
        every { response.getBodyOrEmpty() } returns
            """{"$PROPERTY_PATH":[{"name": "x", "type": "string"}]}""".byteInputStream()
        every { schemaRequester.send(any()) } returns response
        every { property.isAvailable() } returns true
        val assembler =
            DestinationOperationAssembler(
                listOf(PROPERTY_PATH),
                listOf(insertionMethod),
                schemaRequester,
            )

        val operations = assembler.assemble(DestinationObject(OBJECT_NAME, Jsons.objectNode()))

        assertEquals(1, operations.size)
    }

    @Test
    internal fun `test given matching keys expected but none found when assemble then do not return operation`() {
        every { insertionMethod.requiresMatchingKey() } returns true
        every { property.isMatchingKey() } returns false
        every { property.isAvailable() } returns true
        val assembler =
            DestinationOperationAssembler(
                listOf(PROPERTY_PATH),
                listOf(insertionMethod),
                NO_SCHEMA_REQUESTER,
            )

        val operations =
            assembler.assemble(DestinationObject(OBJECT_NAME, apiRepresentationWithOneProperty()))

        assertEquals(0, operations.size)
    }

    @Test
    internal fun `test given matching keys expected and found when assemble then return operation`() {
        every { insertionMethod.requiresMatchingKey() } returns true
        every { property.isMatchingKey() } returns true
        every { property.isAvailable() } returns true
        val assembler =
            DestinationOperationAssembler(
                listOf(PROPERTY_PATH),
                listOf(insertionMethod),
                NO_SCHEMA_REQUESTER,
            )

        val operations =
            assembler.assemble(DestinationObject(OBJECT_NAME, apiRepresentationWithOneProperty()))

        assertEquals(1, operations.size)
    }

    private fun apiRepresentationWithOneProperty(): ObjectNode =
        Jsons.objectNode().apply { this.putArray(PROPERTY_PATH).add(Jsons.objectNode()) }
}
