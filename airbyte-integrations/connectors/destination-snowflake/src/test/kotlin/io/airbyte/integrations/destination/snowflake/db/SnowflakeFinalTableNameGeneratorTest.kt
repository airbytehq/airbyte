/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.db

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeFinalTableNameGeneratorTest {

    @Test
    fun testGetTableNameWithInternalNamespace() {
        val configuration =
            mockk<SnowflakeConfiguration> {
                every { internalTableSchema } returns "test-internal-namespace"
                every { legacyRawTablesOnly } returns true
            }
        val generator = SnowflakeFinalTableNameGenerator(config = configuration)
        val streamName = "test-stream-name"
        val streamNamespace = "test-stream-namespace"
        val streamDescriptor =
            mockk<DestinationStream.Descriptor> {
                every { namespace } returns streamNamespace
                every { name } returns streamName
            }
        val tableName = generator.getTableName(streamDescriptor)
        assertEquals("test-stream-namespace_raw__stream_test-stream-name", tableName.name)
        assertEquals("test-internal-namespace", tableName.namespace)
    }

    @Test
    fun testGetTableNameWithNamespace() {
        val configuration =
            mockk<SnowflakeConfiguration> { every { legacyRawTablesOnly } returns false }
        val generator = SnowflakeFinalTableNameGenerator(config = configuration)
        val streamName = "test-stream-name"
        val streamNamespace = "test-stream-namespace"
        val streamDescriptor =
            mockk<DestinationStream.Descriptor> {
                every { namespace } returns streamNamespace
                every { name } returns streamName
            }
        val tableName = generator.getTableName(streamDescriptor)
        assertEquals("TEST-STREAM-NAME", tableName.name)
        assertEquals("TEST-STREAM-NAMESPACE", tableName.namespace)
    }

    @Test
    fun testGetTableNameWithDefaultNamespace() {
        val defaultNamespace = "test-default-namespace"
        val configuration =
            mockk<SnowflakeConfiguration> {
                every { schema } returns defaultNamespace
                every { legacyRawTablesOnly } returns false
            }
        val generator = SnowflakeFinalTableNameGenerator(config = configuration)
        val streamName = "test-stream-name"
        val streamDescriptor =
            mockk<DestinationStream.Descriptor> {
                every { namespace } returns null
                every { name } returns streamName
            }
        val tableName = generator.getTableName(streamDescriptor)
        assertEquals("TEST-STREAM-NAME", tableName.name)
        assertEquals("TEST-DEFAULT-NAMESPACE", tableName.namespace)
    }
}
