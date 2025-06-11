/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.core.io.SerializedString
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.dataWithAirbyteMeta
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.util.Jsons
import java.io.OutputStream

class FastJsonFormattingWriter(
    private val stream: DestinationStream,
    private val outputStream: OutputStream,
    private val rootLevelFlattening: Boolean,
) : ObjectStorageFormattingWriter {

    private val gen: JsonGenerator =
        Jsons.factory.createGenerator(outputStream).apply {
            setRootValueSeparator(SerializedString(System.lineSeparator()))
        }

    override fun accept(record: DestinationRecordRaw) {
        val obj: ObjectValue =
            record
                .asDestinationRecordAirbyteValue()
                .dataWithAirbyteMeta(
                    stream = stream,
                    flatten = rootLevelFlattening,
                    airbyteRawId = record.airbyteRawId,
                )

        writeValue(obj)
        gen.writeRaw('\n')
    }

    override fun flush() {
        gen.flush()
        outputStream.flush()
    }
    override fun close() {
        gen.close()
        outputStream.close()
    }

    private fun writeValue(v: AirbyteValue) {
        when (v) {
            is NullValue -> gen.writeNull()
            is StringValue -> gen.writeString(v.value)
            is BooleanValue -> gen.writeBoolean(v.value)
            is IntegerValue -> gen.writeNumber(v.value)
            is NumberValue -> gen.writeNumber(v.value)
            is DateValue -> gen.writeString(v.value.toString())
            is TimestampWithTimezoneValue -> gen.writeString(v.value.toString())
            is TimestampWithoutTimezoneValue -> gen.writeString(v.value.toString())
            is TimeWithTimezoneValue -> gen.writeString(v.value.toString())
            is TimeWithoutTimezoneValue -> gen.writeString(v.value.toString())
            is ArrayValue -> {
                gen.writeStartArray()
                v.values.forEach { element: AirbyteValue -> writeValue(element) }
                gen.writeEndArray()
            }
            is ObjectValue -> {
                gen.writeStartObject()
                v.values.forEach { (k, fieldVal): Map.Entry<String, AirbyteValue> ->
                    gen.writeFieldName(k)
                    writeValue(fieldVal)
                }
                gen.writeEndObject()
            }
        }
    }
}
