/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.types

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
    val stringData = "string".repeat(200)
    val bigInt = BigDecimal("3000000000")
    val bigDecimal = BigDecimal("3000000000.123")
    val date = LocalDate.now()
    val timeWithTimeZone = OffsetTime.now()
    val timeWithoutTimeZone = LocalTime.now()
    val timestampWithTimeZone = OffsetDateTime.now()
    val timestampWithoutTimeZone = LocalDateTime.now()
    val json = """{"id": 1, "name": "alice", "active": true}"""

    override fun generateData(currentID: Long, modulo: Int, offset: Int): NativeRecordPayload {
        val incrementedID = (currentID * modulo + offset)
        val recordData: NativeRecordPayload = mutableMapOf()

        recordData[TypesFlavor.FieldNames.ID] =
            FieldValueEncoder(incrementedID.toInt(), IntegerFieldType.jsonEncoder as IntCodec)

        recordData[TypesFlavor.FieldNames.STRING] =
            FieldValueEncoder(stringData, StringFieldType.jsonEncoder as TextCodec)

        recordData[TypesFlavor.FieldNames.BOOLEAN] =
            FieldValueEncoder(Random.nextBoolean(), BooleanFieldType.jsonEncoder as BooleanCodec)

        recordData[TypesFlavor.FieldNames.NUMBER] =
            FieldValueEncoder(incrementedID.toDouble(), NumberFieldType.jsonEncoder as DoubleCodec)

        recordData[TypesFlavor.FieldNames.BIG_INTEGER] =
            FieldValueEncoder(bigInt, BigIntegerFieldType.jsonEncoder as BigDecimalIntegerCodec)

        recordData[TypesFlavor.FieldNames.BIG_DECIMAL] =
            FieldValueEncoder(bigDecimal, BigDecimalFieldType.jsonEncoder as BigDecimalCodec)

        recordData[TypesFlavor.FieldNames.DATE] =
            FieldValueEncoder(date, DateFieldType.jsonEncoder as LocalDateCodec)

        recordData[TypesFlavor.FieldNames.TIME_WITH_TIME_ZONE] =
            FieldValueEncoder(
                timeWithTimeZone,
                TimeWithTimeZoneFieldType.jsonEncoder as OffsetTimeCodec
            )

        recordData[TypesFlavor.FieldNames.TIME_WITHOUT_TIME_ZONE] =
            FieldValueEncoder(
                timeWithoutTimeZone,
                TimeWithoutTimeZoneFieldType.jsonEncoder as LocalTimeCodec
            )

        recordData[TypesFlavor.FieldNames.TIMESTAMP_WITH_TIME_ZONE] =
            FieldValueEncoder(
                timestampWithTimeZone,
                TimestampWithTimeZoneFieldType.jsonEncoder as OffsetDateTimeCodec
            )

        recordData[TypesFlavor.FieldNames.TIMESTAMP_WITHOUT_TIME_ZONE] =
            FieldValueEncoder(
                timestampWithoutTimeZone,
                TimestampWithoutTimeZoneFieldType.jsonEncoder as LocalDateTimeCodec
            )

        recordData[TypesFlavor.FieldNames.JSON] =
            FieldValueEncoder(json, JsonFieldType.jsonEncoder as JsonStringCodec)

        return recordData
    }
}
