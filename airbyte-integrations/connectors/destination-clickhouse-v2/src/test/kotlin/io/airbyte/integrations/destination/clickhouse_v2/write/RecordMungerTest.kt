/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.EnrichedDestinationRecordAirbyteValue
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.verify
import kotlin.test.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class RecordMungerTest {
    @MockK lateinit var catalogInfo: TableCatalog

    private lateinit var munger: RecordMunger

    @BeforeEach
    fun setup() {
        munger = RecordMunger(catalogInfo)
    }

    @Test
    fun `transforms record into map of munged keys and values`() {
        // add "_munged" to every key so we can validate we get the mapped cols
        every { catalogInfo.getMappedColumnName(any(), any()) } answers
            {
                secondArg<String>() + "_munged"
            }

        // mock coercion output
        val userFields =
            linkedMapOf(
                "user_field_1" to Fixtures.mockCoercedValue(StringValue("test1")),
                "user_field_2" to Fixtures.mockCoercedValue(StringValue("test2")),
                "user_field_3" to Fixtures.mockCoercedValue(IntegerValue(777)),
                "user_field_4" to Fixtures.mockCoercedValue(BooleanValue(false)),
            )
        val internalFields =
            mapOf(
                "internal_field_1" to Fixtures.mockCoercedValue(StringValue("internal1")),
                "internal_field_2" to Fixtures.mockCoercedValue(IntegerValue(0)),
                "internal_field_3" to Fixtures.mockCoercedValue(BooleanValue(true)),
            )
        val coerced =
            mockk<EnrichedDestinationRecordAirbyteValue> {
                every { declaredFields } answers { userFields }
                every { airbyteMetaFields } answers { internalFields }
            }

        val input =
            mockk<DestinationRecordRaw>(relaxed = true) {
                every { asEnrichedDestinationRecordAirbyteValue(any()) } answers { coerced }
            }

        val output = munger.transformForDest(input)

        // just validate we call the coercing logic here
        // if we refactor to do the coercing directly here, we need more comprehensive tests
        verify {
            input.asEnrichedDestinationRecordAirbyteValue(extractedAtAsTimestampWithTimezone = true)
        }

        // munged keys map to unwrapped / coerced values
        val expected =
            mapOf(
                // user cols are munged
                "user_field_1_munged" to StringValue("test1"),
                "user_field_2_munged" to StringValue("test2"),
                "user_field_3_munged" to IntegerValue(777),
                "user_field_4_munged" to BooleanValue(false),
                // internal cols are not munged for now
                "internal_field_1" to StringValue("internal1"),
                "internal_field_2" to IntegerValue(0),
                "internal_field_3" to BooleanValue(true),
            )

        assertEquals(expected, output)
    }

    object Fixtures {
        // we can't use mockk for these because AirbyteValue being recursive
        // causes a stack overflow in the mockk interceptor
        fun mockCoercedValue(value: AirbyteValue) =
            EnrichedAirbyteValue(
                abValue = value,
                // the below fields are not under test
                type = StringType,
                name = "fixture",
                airbyteMetaField = null,
            )
    }
}
