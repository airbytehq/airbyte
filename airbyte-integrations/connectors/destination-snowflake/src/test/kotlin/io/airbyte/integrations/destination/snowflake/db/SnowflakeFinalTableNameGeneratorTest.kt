/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.db

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingUtil
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeFinalTableNameGeneratorTest {

    @Test
    fun testGetTableNameWithInternalNamespace() {
        val internalNamespace = "test-internal-namespace"
        val configuration =
            mockk<SnowflakeConfiguration> {
                every { internalTableSchema } returns internalNamespace
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
        assertEquals(
            TypingDedupingUtil.concatenateRawTableName(streamNamespace, streamName)
                .toSnowflakeCompatibleName(),
            tableName.name
        )
        assertEquals(internalNamespace.toSnowflakeCompatibleName(), tableName.namespace)
    }

    @Test
    fun testGetTableNameWithNamespace() {
        val configuration =
            mockk<SnowflakeConfiguration> { every { internalTableSchema } returns null }
        val generator = SnowflakeFinalTableNameGenerator(config = configuration)
        val streamName = "test-stream-name"
        val streamNamespace = "test-stream-namespace"
        val streamDescriptor =
            mockk<DestinationStream.Descriptor> {
                every { namespace } returns streamNamespace
                every { name } returns streamName
            }
        val tableName = generator.getTableName(streamDescriptor)
        assertEquals(streamName.toSnowflakeCompatibleName(), tableName.name)
        assertEquals(streamNamespace.toSnowflakeCompatibleName(), tableName.namespace)
    }

    @Test
    fun testGetTableNameWithDefaultNamespace() {
        val defaultNamespace = "test-default-namespace"
        val configuration =
            mockk<SnowflakeConfiguration> {
                every { internalTableSchema } returns null
                every { schema } returns defaultNamespace
            }
        val generator = SnowflakeFinalTableNameGenerator(config = configuration)
        val streamName = "test-stream-name"
        val streamDescriptor =
            mockk<DestinationStream.Descriptor> {
                every { namespace } returns null
                every { name } returns streamName
            }
        val tableName = generator.getTableName(streamDescriptor)
        assertEquals(streamName.toSnowflakeCompatibleName(), tableName.name)
        assertEquals(defaultNamespace.toSnowflakeCompatibleName(), tableName.namespace)
    }
}
