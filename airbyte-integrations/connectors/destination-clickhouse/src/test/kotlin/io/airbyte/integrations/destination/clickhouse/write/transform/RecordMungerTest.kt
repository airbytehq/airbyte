/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
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

    @MockK lateinit var validator: ClickhouseCoercer

    private lateinit var munger: RecordMunger

    @BeforeEach
    fun setup() {
        munger = RecordMunger(catalogInfo, validator)
    }

    @Test
    fun `transforms record into map of munged keys and values`() {
        // add "_munged" to every key so we can validate we get the mapped cols
        every { catalogInfo.getMappedColumnName(any(), any()) } answers
            {
                secondArg<String>() + "_munged"
            }

        every { validator.validate(any()) } answers { firstArg() }

        val stringfiedValue =
            Fixtures.mockCoercedValue(StringValue("{ \"json\": \"stringified\" }"))
        every { validator.toJsonStringValue(any()) } answers { stringfiedValue }

        // mock coercion output
        val nonUnionUserFields =
            linkedMapOf(
                "user_field_1" to Fixtures.mockCoercedValue(StringValue("test1")),
                "user_field_2" to Fixtures.mockCoercedValue(StringValue("test2")),
                "user_field_3" to Fixtures.mockCoercedValue(IntegerValue(777)),
                "user_field_4" to Fixtures.mockCoercedValue(BooleanValue(false)),
            )
        val unionUserField = "user_field_5" to Fixtures.mockCoercedValue(ObjectValue(linkedMapOf()))
        val userFields =
            (nonUnionUserFields + unionUserField) as LinkedHashMap<String, EnrichedAirbyteValue>
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
                every { schemaFields } returns
                    linkedMapOf(
                        "user_field_1" to FieldType(StringType, false),
                        "user_field_2" to FieldType(StringType, false),
                        "user_field_3" to FieldType(IntegerType, false),
                        "user_field_4" to FieldType(BooleanType, false),
                        // this field is a union type so it should be turned into a json string
                        "user_field_5" to FieldType(UnionType(setOf(), false), false),
                    )
            }

        val output = munger.transformForDest(input)

        // just validate we call the coercing logic here
        // if we refactor to do the coercing directly here, we need more comprehensive tests
        verify {
            input.asEnrichedDestinationRecordAirbyteValue(extractedAtAsTimestampWithTimezone = true)
        }
        // we validate each non-union field directly
        nonUnionUserFields.forEach { verify { validator.validate(it.value) } }
        // the stringified field is also validated
        verify { validator.validate(stringfiedValue) }

        // munged keys map to unwrapped / coerced values
        val expected =
            mapOf(
                // user cols are munged
                "user_field_1_munged" to StringValue("test1"),
                "user_field_2_munged" to StringValue("test2"),
                "user_field_3_munged" to IntegerValue(777),
                "user_field_4_munged" to BooleanValue(false),
                // union is stringified
                "user_field_5_munged" to stringfiedValue.abValue,
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
