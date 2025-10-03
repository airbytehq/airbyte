/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.protocol.ProtobufTypeBasedEncoder
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime

/** Convenience class for testing. */
class AirbyteValueToProtobuf {
    private val encoder = ProtobufTypeBasedEncoder()
    fun toProtobuf(value: AirbyteValue, type: AirbyteType): AirbyteValueProtobuf {
        // Handle null values
        if (value is NullValue) {
            return encoder.encode(null, LeafAirbyteSchemaType.STRING)
        }

        // For complex types (arrays, objects, unions), encode as JSON
        return when (type) {
            is ArrayType, ArrayTypeWithoutSchema -> {
                if (value is ArrayValue) {
                    encoder.encode(value.toJson().serializeToJsonBytes(), LeafAirbyteSchemaType.JSONB)
                } else {
                    encoder.encode(null, LeafAirbyteSchemaType.STRING)
                }
            }
            is ObjectType, ObjectTypeWithEmptySchema, ObjectTypeWithoutSchema -> {
                if (value is ObjectValue) {
                    encoder.encode(value.toJson().serializeToJsonBytes(), LeafAirbyteSchemaType.JSONB)
                } else {
                    encoder.encode(null, LeafAirbyteSchemaType.STRING)
                }
            }
            is UnionType, is UnknownType -> {
                encoder.encode(value.toJson().serializeToJsonBytes(), LeafAirbyteSchemaType.JSONB)
            }
            // For scalar and temporal types, extract the underlying value and use the encoder
            is BooleanType -> {
                if (value is BooleanValue) {
                    encoder.encode(value.value, LeafAirbyteSchemaType.BOOLEAN)
                } else {
                    encoder.encode(null, LeafAirbyteSchemaType.STRING)
                }
            }
            is StringType -> {
                if (value is StringValue) {
                    encoder.encode(value.value, LeafAirbyteSchemaType.STRING)
                } else {
                    encoder.encode(null, LeafAirbyteSchemaType.STRING)
                }
            }
            is IntegerType -> {
                if (value is IntegerValue) {
                    encoder.encode(value.value, LeafAirbyteSchemaType.INTEGER)
                } else {
                    encoder.encode(null, LeafAirbyteSchemaType.STRING)
                }
            }
            is NumberType -> {
                if (value is NumberValue) {
                    encoder.encode(value.value, LeafAirbyteSchemaType.NUMBER)
                } else {
                    encoder.encode(value.toJson().serializeToJsonBytes(), LeafAirbyteSchemaType.JSONB)
                }
            }
            is DateType -> {
                val dateValue = when (value) {
                    is DateValue -> value.value
                    is StringValue -> try { LocalDate.parse(value.value) } catch (_: Exception) { null }
                    else -> null
                }
                encoder.encode(dateValue, LeafAirbyteSchemaType.DATE)
            }
            is TimeTypeWithTimezone -> {
                val timeValue = when (value) {
                    is TimeWithTimezoneValue -> value.value
                    is StringValue -> try { OffsetTime.parse(value.value) } catch (_: Exception) { null }
                    else -> null
                }
                encoder.encode(timeValue, LeafAirbyteSchemaType.TIME_WITH_TIMEZONE)
            }
            is TimeTypeWithoutTimezone -> {
                val timeValue = when (value) {
                    is TimeWithoutTimezoneValue -> value.value
                    is StringValue -> try { LocalTime.parse(value.value) } catch (_: Exception) { null }
                    else -> null
                }
                encoder.encode(timeValue, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
            }
            is TimestampTypeWithTimezone -> {
                val timestampValue = when (value) {
                    is TimestampWithTimezoneValue -> value.value
                    is StringValue -> try { OffsetDateTime.parse(value.value) } catch (_: Exception) { null }
                    else -> null
                }
                encoder.encode(timestampValue, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
            }
            is TimestampTypeWithoutTimezone -> {
                val timestampValue = when (value) {
                    is TimestampWithoutTimezoneValue -> value.value
                    is StringValue -> try { LocalDateTime.parse(value.value) } catch (_: Exception) { null }
                    else -> null
                }
                encoder.encode(timestampValue, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)
            }
        }
    }
}
