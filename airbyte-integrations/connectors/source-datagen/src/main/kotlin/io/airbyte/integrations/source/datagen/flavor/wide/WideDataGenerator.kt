/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.wide

import io.airbyte.cdk.data.BigDecimalCodec
import io.airbyte.cdk.data.BigDecimalIntegerCodec
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.OffsetTimeCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.integrations.source.datagen.BigDecimalFieldType
import io.airbyte.integrations.source.datagen.BigIntegerFieldType
import io.airbyte.integrations.source.datagen.BooleanFieldType
import io.airbyte.integrations.source.datagen.DateFieldType
import io.airbyte.integrations.source.datagen.IntegerFieldType
import io.airbyte.integrations.source.datagen.JsonFieldType
import io.airbyte.integrations.source.datagen.NumberFieldType
import io.airbyte.integrations.source.datagen.StringFieldType
import io.airbyte.integrations.source.datagen.TimeWithTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimeWithoutTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimestampWithTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimestampWithoutTimeZoneFieldType
import io.airbyte.integrations.source.datagen.flavor.DataGenerator
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime

class WideDataGenerator(private val fields: List<Field>) : DataGenerator {

    private val stringData = "string".repeat(200)
    private val bigInt = BigDecimal("3000000000")
    private val bigDecimal = BigDecimal("3000000000.123")
    private val date = LocalDate.now()
    private val timeWithTimeZone = OffsetTime.now()
    private val timeWithoutTimeZone = LocalTime.now()
    private val timestampWithTimeZone = OffsetDateTime.now()
    private val timestampWithoutTimeZone = LocalDateTime.now()
    private val json = """{"id": 1, "name": "alice", "active": true}"""

    private val intCodec = IntegerFieldType.jsonEncoder as IntCodec
    private val textCodec = StringFieldType.jsonEncoder as TextCodec
    private val booleanCodec = BooleanFieldType.jsonEncoder as BooleanCodec
    private val doubleCodec = NumberFieldType.jsonEncoder as DoubleCodec
    private val bigDecimalIntCodec = BigIntegerFieldType.jsonEncoder as BigDecimalIntegerCodec
    private val bigDecimalCodec = BigDecimalFieldType.jsonEncoder as BigDecimalCodec
    private val localDateCodec = DateFieldType.jsonEncoder as LocalDateCodec
    private val offsetTimeCodec = TimeWithTimeZoneFieldType.jsonEncoder as OffsetTimeCodec
    private val localTimeCodec = TimeWithoutTimeZoneFieldType.jsonEncoder as LocalTimeCodec
    private val offsetDateTimeCodec =
        TimestampWithTimeZoneFieldType.jsonEncoder as OffsetDateTimeCodec
    private val localDateTimeCodec =
        TimestampWithoutTimeZoneFieldType.jsonEncoder as LocalDateTimeCodec
    private val jsonStringCodec = JsonFieldType.jsonEncoder as JsonStringCodec

    override fun generateData(currentID: Long, modulo: Int, offset: Int): NativeRecordPayload {
        val incrementedID = (currentID * modulo + offset)
        val recordData: NativeRecordPayload = mutableMapOf()

        for (field in fields) {
            recordData[field.id] = encodeField(field.type, incrementedID)
        }

        return recordData
    }

    private fun encodeField(fieldType: FieldType, incrementedID: Long): FieldValueEncoder<*> =
        when (fieldType) {
            IntegerFieldType -> FieldValueEncoder(incrementedID.toInt(), intCodec)
            StringFieldType -> FieldValueEncoder(stringData, textCodec)
            BooleanFieldType -> FieldValueEncoder(incrementedID % 2 == 0L, booleanCodec)
            NumberFieldType -> FieldValueEncoder(incrementedID.toDouble(), doubleCodec)
            BigIntegerFieldType -> FieldValueEncoder(bigInt, bigDecimalIntCodec)
            BigDecimalFieldType -> FieldValueEncoder(bigDecimal, bigDecimalCodec)
            DateFieldType -> FieldValueEncoder(date, localDateCodec)
            TimeWithTimeZoneFieldType -> FieldValueEncoder(timeWithTimeZone, offsetTimeCodec)
            TimeWithoutTimeZoneFieldType -> FieldValueEncoder(timeWithoutTimeZone, localTimeCodec)
            TimestampWithTimeZoneFieldType ->
                FieldValueEncoder(timestampWithTimeZone, offsetDateTimeCodec)
            TimestampWithoutTimeZoneFieldType ->
                FieldValueEncoder(timestampWithoutTimeZone, localDateTimeCodec)
            JsonFieldType -> FieldValueEncoder(json, jsonStringCodec)
            else -> throw IllegalArgumentException("Unsupported field type: $fieldType")
        }
}
