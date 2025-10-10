/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.types

import io.airbyte.cdk.data.ArrayEncoder
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
import kotlin.collections.set
import kotlin.random.Random

class TypesDataGenerator() : DataGenerator {
    val fieldsForTable = TypesFlavor.fields[TypesFlavor.typesTableName]!!
    val bigInt = BigDecimal("3000000000")
    val bigDecimal = BigDecimal("3000000000.123")
    val date = LocalDate.now()
    val timeWithTimeZone = OffsetTime.now()
    val timeWithoutTimeZone = LocalTime.now()
    val timestampWithTimeZone = OffsetDateTime.now()
    val timestampWithoutTimeZone = LocalDateTime.now()
    val json = """{"id": 1, "name": "alice", "active": true}"""
    val array = listOf(1, 2, 3)

    override fun generateData(currentID: Long, modulo: Int, offset: Int): NativeRecordPayload {
        val incrementedID = (currentID * modulo + offset)
        val recordData: NativeRecordPayload = mutableMapOf()

        recordData[fieldsForTable[0].id] =
            FieldValueEncoder(incrementedID.toInt(), IntegerFieldType.jsonEncoder as IntCodec)

        recordData[fieldsForTable[1].id] =
            FieldValueEncoder("string$incrementedID", StringFieldType.jsonEncoder as TextCodec)

        recordData[fieldsForTable[2].id] =
            FieldValueEncoder(Random.nextBoolean(), BooleanFieldType.jsonEncoder as BooleanCodec)

        recordData[fieldsForTable[3].id] =
            FieldValueEncoder(incrementedID.toDouble(), NumberFieldType.jsonEncoder as DoubleCodec)

        recordData[fieldsForTable[4].id] =
            FieldValueEncoder(bigInt, BigIntegerFieldType.jsonEncoder as BigDecimalIntegerCodec)

        recordData[fieldsForTable[5].id] =
            FieldValueEncoder(bigDecimal, BigDecimalFieldType.jsonEncoder as BigDecimalCodec)

        recordData[fieldsForTable[6].id] = FieldValueEncoder(date, DateFieldType.jsonEncoder as LocalDateCodec)

        recordData[fieldsForTable[7].id] =
            FieldValueEncoder(
                timeWithTimeZone,
                TimeWithTimeZoneFieldType.jsonEncoder as OffsetTimeCodec
            )

        recordData[fieldsForTable[8].id] =
            FieldValueEncoder(
                timeWithoutTimeZone,
                TimeWithoutTimeZoneFieldType.jsonEncoder as LocalTimeCodec
            )

        recordData[fieldsForTable[9].id] =
            FieldValueEncoder(
                timestampWithTimeZone,
                TimestampWithTimeZoneFieldType.jsonEncoder as OffsetDateTimeCodec
            )

        recordData[fieldsForTable[10].id] =
            FieldValueEncoder(
                timestampWithoutTimeZone,
                TimestampWithoutTimeZoneFieldType.jsonEncoder as LocalDateTimeCodec
            )

        recordData[fieldsForTable[11].id] = FieldValueEncoder(json, JsonFieldType.jsonEncoder as JsonStringCodec)

        recordData[fieldsForTable[12].id] = FieldValueEncoder(array, ArrayEncoder(IntCodec))

        return recordData
    }
}
