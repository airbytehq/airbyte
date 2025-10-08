package io.airbyte.integrations.source.datagen.flavor.all_types

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
import kotlin.collections.set
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import kotlin.random.Random

class TypesDataGenerator() : DataGenerator {
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

        recordData["id"] =
            FieldValueEncoder(incrementedID.toInt(), IntegerFieldType.jsonEncoder as IntCodec)

        recordData["string"] =
            FieldValueEncoder("string$incrementedID", StringFieldType.jsonEncoder as TextCodec)

        recordData["boolean"] =
            FieldValueEncoder(Random.nextBoolean(), BooleanFieldType.jsonEncoder as BooleanCodec)

        recordData["number"] =
            FieldValueEncoder(incrementedID.toDouble(), NumberFieldType.jsonEncoder as DoubleCodec)

        recordData["big integer"] =
            FieldValueEncoder(bigInt, BigIntegerFieldType.jsonEncoder as BigDecimalIntegerCodec)

        recordData["big decimal"] =
            FieldValueEncoder(bigDecimal, BigDecimalFieldType.jsonEncoder as BigDecimalCodec)

        recordData["date"] =
            FieldValueEncoder(date,DateFieldType.jsonEncoder as LocalDateCodec)

        recordData["time with time zone"] =
            FieldValueEncoder(timeWithTimeZone, TimeWithTimeZoneFieldType.jsonEncoder as OffsetTimeCodec)

        recordData["time without time zone"] =
            FieldValueEncoder(timeWithoutTimeZone, TimeWithoutTimeZoneFieldType.jsonEncoder as LocalTimeCodec)

        recordData["timestamp with time zone"] =
            FieldValueEncoder(timestampWithTimeZone,TimestampWithTimeZoneFieldType.jsonEncoder as OffsetDateTimeCodec)

        recordData["timestamp without time zone"] =
            FieldValueEncoder(timestampWithoutTimeZone,TimestampWithoutTimeZoneFieldType.jsonEncoder as LocalDateTimeCodec)

        recordData["json"] = FieldValueEncoder(json, JsonFieldType.jsonEncoder as JsonStringCodec)

        recordData["array"] = FieldValueEncoder(array, ArrayEncoder(IntCodec))

        return recordData
    }
}
