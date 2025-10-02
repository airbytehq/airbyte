package io.airbyte.integrations.source.datagen.flavor.all_types

import io.airbyte.cdk.data.AnyEncoder
import io.airbyte.cdk.data.ArrayEncoder
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.ObjectEncoder
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.OffsetTimeCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.integrations.source.datagen.ArrayFieldType
import io.airbyte.integrations.source.datagen.BooleanFieldType
import io.airbyte.integrations.source.datagen.DateFieldType
import io.airbyte.integrations.source.datagen.IntegerFieldType
import io.airbyte.integrations.source.datagen.ObjectFieldType
import io.airbyte.integrations.source.datagen.ObjectWithEmptySchemaFieldType
import io.airbyte.integrations.source.datagen.ObjectWithoutSchemaFieldType
import io.airbyte.integrations.source.datagen.StringFieldType
import io.airbyte.integrations.source.datagen.TimeWithTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimeWithoutTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimestampWithTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimestampWithoutTimeZoneFieldType
import io.airbyte.integrations.source.datagen.flavor.DataGenerator
import kotlin.collections.set
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneId
import kotlin.random.Random

class TypesDataGenerator() : DataGenerator {
    val date = LocalDate.now()
    val timeWithTimeZone = OffsetTime.now()
    val timeWithoutTimeZone = LocalTime.now()
    val timestampWithTimeZone = OffsetDateTime.now()
    val timestampWithoutTimeZone = LocalDateTime.now()
    val array = listOf(1, 2, 3)
    val arrayWithoutSchema = listOf(1, "hello", true)

    override fun generateData(currentID: Long, modulo: Int, offset: Int): NativeRecordPayload {
        val incrementedID = (currentID * modulo + offset)
        val recordData: NativeRecordPayload = mutableMapOf()

        recordData["id"] =
            FieldValueEncoder(incrementedID, IntegerFieldType.jsonEncoder as LongCodec)

        recordData["string"] =
            FieldValueEncoder("string$incrementedID", StringFieldType.jsonEncoder as TextCodec)

        recordData["boolean"] =
            FieldValueEncoder(Random.nextBoolean(), BooleanFieldType.jsonEncoder as BooleanCodec)

        recordData["date"] =
            FieldValueEncoder(date,DateFieldType.jsonEncoder as LocalDateCodec)

        recordData["time with time zone"] =
            FieldValueEncoder(timeWithTimeZone, TimeWithTimeZoneFieldType.jsonEncoder as OffsetTimeCodec)

        recordData["time without time zone"] =
            FieldValueEncoder(timeWithoutTimeZone, TimeWithoutTimeZoneFieldType.jsonEncoder as LocalTimeCodec)

        recordData["timestamp wth time zone"] =
            FieldValueEncoder(timestampWithTimeZone,TimestampWithTimeZoneFieldType.jsonEncoder as OffsetDateTimeCodec)

        recordData["timestamp without time zone"] =
            FieldValueEncoder(timestampWithoutTimeZone,TimestampWithoutTimeZoneFieldType.jsonEncoder as LocalDateTimeCodec)

        recordData["array"] = FieldValueEncoder(array, ArrayEncoder(IntCodec)) // TODO: check this cuz it feels wrong lol

        recordData["array without schema"] = FieldValueEncoder(arrayWithoutSchema, ArrayEncoder(AnyEncoder)) // and this

        recordData["object"] = FieldValueEncoder(linkedMapOf("id" to incrementedID, "name" to "Alice$incrementedID"),
            ObjectEncoder(linkedMapOf("id" to LongCodec, "name" to TextCodec))
        )

        recordData["object with empty schema"] = FieldValueEncoder(linkedMapOf(), ObjectEncoder(LinkedHashMap()))

        recordData["object without schema"] = FieldValueEncoder(linkedMapOf("id" to incrementedID, "name" to "Bob$incrementedID"),
            ObjectWithoutSchemaFieldType.jsonEncoder as ObjectEncoder)

        return recordData
    }
}
