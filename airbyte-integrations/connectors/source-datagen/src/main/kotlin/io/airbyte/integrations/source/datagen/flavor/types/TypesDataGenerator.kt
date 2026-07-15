/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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

        recordData[TypesFlavor.FieldNames.ID] = FieldValueEncoder(incrementedID.toInt(), intCodec)

        recordData[TypesFlavor.FieldNames.STRING] = FieldValueEncoder(stringData, textCodec)

        recordData[TypesFlavor.FieldNames.BOOLEAN] =
            FieldValueEncoder(Random.nextBoolean(), booleanCodec)

        recordData[TypesFlavor.FieldNames.NUMBER] =
            FieldValueEncoder(incrementedID.toDouble(), doubleCodec)

        recordData[TypesFlavor.FieldNames.BIG_INTEGER] =
            FieldValueEncoder(bigInt, bigDecimalIntCodec)

        recordData[TypesFlavor.FieldNames.BIG_DECIMAL] =
            FieldValueEncoder(bigDecimal, bigDecimalCodec)

        recordData[TypesFlavor.FieldNames.DATE] = FieldValueEncoder(date, localDateCodec)

        recordData[TypesFlavor.FieldNames.TIME_WITH_TIME_ZONE] =
            FieldValueEncoder(timeWithTimeZone, offsetTimeCodec)

        recordData[TypesFlavor.FieldNames.TIME_WITHOUT_TIME_ZONE] =
            FieldValueEncoder(timeWithoutTimeZone, localTimeCodec)

        recordData[TypesFlavor.FieldNames.TIMESTAMP_WITH_TIME_ZONE] =
            FieldValueEncoder(timestampWithTimeZone, offsetDateTimeCodec)

        recordData[TypesFlavor.FieldNames.TIMESTAMP_WITHOUT_TIME_ZONE] =
            FieldValueEncoder(timestampWithoutTimeZone, localDateTimeCodec)

        recordData[TypesFlavor.FieldNames.JSON] = FieldValueEncoder(json, jsonStringCodec)

        return recordData
    }
}
