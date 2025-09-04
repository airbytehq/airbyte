/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.transform

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue.Companion.from
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.EnrichedDestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeRecordMungerTest {

    @Test
    fun testTransformation() {
        val rawId = 1
        val id = 2
        val idColumnName = "id"
        val enrichedAirbyteMetaFields = LinkedHashMap<String, EnrichedAirbyteValue>()
        val enrichedDeclaredFields = LinkedHashMap<String, EnrichedAirbyteValue>()

        enrichedAirbyteMetaFields[Meta.AirbyteMetaFields.RAW_ID.name] =
            EnrichedAirbyteValue(
                abValue = from(rawId),
                name = Meta.AirbyteMetaFields.RAW_ID.name,
                type = IntegerType,
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        enrichedDeclaredFields[idColumnName] =
            EnrichedAirbyteValue(
                abValue = from(id),
                name = idColumnName,
                type = IntegerType,
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val tableCatalog =
            mockk<TableCatalog> { every { getMappedColumnName(any(), any()) } returnsArgument (1) }
        val enrichedDestinationRecordAirbyteValue =
            mockk<EnrichedDestinationRecordAirbyteValue> {
                every { airbyteMetaFields } returns enrichedAirbyteMetaFields
                every { declaredFields } returns enrichedDeclaredFields
            }
        val destinationRecordRaw =
            mockk<DestinationRecordRaw> {
                every { asEnrichedDestinationRecordAirbyteValue(any()) } returns
                    enrichedDestinationRecordAirbyteValue
                every { stream } returns mockk<DestinationStream>()
            }
        val munger = SnowflakeRecordMunger(catalogInfo = tableCatalog)
        val transformed = munger.transformForDest(destinationRecordRaw)
        assertEquals(
            rawId,
            (transformed[Meta.AirbyteMetaFields.RAW_ID.name] as IntegerValue).value.toInt()
        )
        assertEquals(id, (transformed[idColumnName] as IntegerValue).value.toInt())
    }
}
