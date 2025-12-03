/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.TableName
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class TableNameResolverTest {
    @MockK private lateinit var mapper: TableSchemaMapper

    @Test
    fun `handles no collisions`() {
        val resolver = TableNameResolver(mapper)
        val desc1 = DestinationStream.Descriptor("namespace1", "stream1")
        val desc2 = DestinationStream.Descriptor("namespace2", "stream2")
        val descriptors = setOf(desc1, desc2)

        val table1 = TableName("namespace1", "stream1")
        val table2 = TableName("namespace2", "stream2")

        every { mapper.toFinalTableName(desc1) } returns table1
        every { mapper.toFinalTableName(desc2) } returns table2

        val result = resolver.getTableNameMapping(descriptors)

        assertEquals(2, result.size)
        assertEquals(table1, result[desc1])
        assertEquals(table2, result[desc2])
    }

    // We're testing some internals here but this represents an external API with the destination
    // so it's worth preserving.
    @Test
    fun `handles table name collision with hash suffix`() {
        val resolver = TableNameResolver(mapper)
        val desc1 = DestinationStream.Descriptor("namespace", "stream1")
        val desc2 = DestinationStream.Descriptor("namespace", "stream2")
        val descriptors = setOf(desc1, desc2)

        val collisionTableName = TableName("namespace", "same_table")
        val hashedTableName = TableName("namespace", "stream2_hash")

        every { mapper.toFinalTableName(any()) } returnsMany
            listOf(
                // call with desc1
                collisionTableName,
                // call with desc2
                collisionTableName,
                // call with desc2 and hash appended
                hashedTableName,
            )

        val result = resolver.getTableNameMapping(descriptors)

        assertEquals(2, result.size)
        assertEquals(collisionTableName, result[desc1])
        assertEquals(hashedTableName, result[desc2])
    }

    // We're testing some internals here but this represents an external API with the destination
    // so it's worth preserving.
    @Test
    fun `handles multiple collisions`() {
        val resolver = TableNameResolver(mapper)
        val desc1 = DestinationStream.Descriptor("namespace", "stream1")
        val desc2 = DestinationStream.Descriptor("namespace", "stream2")
        val desc3 = DestinationStream.Descriptor("namespace", "stream3")
        val descriptors = setOf(desc1, desc2, desc3)

        val collisionTableName = TableName("namespace", "same_table")
        val hashedTable2 = TableName("namespace", "stream2_hash")
        val hashedTable3 = TableName("namespace", "stream3_hash")

        every { mapper.toFinalTableName(any()) } returnsMany
            listOf(
                // call with desc1
                collisionTableName,
                // call with desc2
                collisionTableName,
                // call with desc2 and hash appended
                hashedTable2,
                // call with desc3
                collisionTableName,
                // call with desc3 and hash appended
                hashedTable3,
            )

        val result = resolver.getTableNameMapping(descriptors)

        assertEquals(3, result.size)
        assertEquals(collisionTableName, result[desc1])
        assertEquals(hashedTable2, result[desc2])
        assertEquals(hashedTable3, result[desc3])
    }

    @Test
    fun `handles empty set`() {
        val resolver = TableNameResolver(mapper)
        val result = resolver.getTableNameMapping(emptySet())

        assertEquals(0, result.size)
    }

    @Test
    fun `handles single stream`() {
        val resolver = TableNameResolver(mapper)
        val desc = DestinationStream.Descriptor("namespace", "stream")
        val table = TableName("namespace", "stream")

        every { mapper.toFinalTableName(desc) } returns table

        val result = resolver.getTableNameMapping(setOf(desc))

        assertEquals(1, result.size)
        assertEquals(table, result[desc])
    }
}
