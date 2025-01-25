/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.avro

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import java.time.ZoneOffset

object AvroExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val withIntegerTimestamps = timestampsToInteger(expectedRecord.data)
        val withRemappedFieldNames = fieldNameMangler(withIntegerTimestamps)
        return expectedRecord.copy(data = withRemappedFieldNames as ObjectValue)
    }

    override fun mapStreamDescriptor(
        descriptor: DestinationStream.Descriptor
    ): DestinationStream.Descriptor {
        // Map the special character but not the '+', because only the former is replaced in file
        // paths.
        return descriptor.copy(name = descriptor.name.replace("é", "e"))
    }

    private fun fieldNameMangler(value: AirbyteValue): AirbyteValue =
        when (value) {
            is ObjectValue ->
                ObjectValue(
                    LinkedHashMap(
                        value.values
                            .map { (k, v) ->
                                k.replace("é", "e").replace("+", "_").replace(Regex("(^\\d+)")) {
                                    "_${it.groupValues[0]}"
                                } to fieldNameMangler(v)
                            }
                            .toMap()
                    )
                )
            else -> value
        }

    /**
     * Avro doesn't distinguish between temporal types having/not having timezone. So we map all
     * temporal types to their "with timezone" variant, defaulting to UTC.
     */
    private fun timestampsToInteger(value: AirbyteValue): AirbyteValue =
        when (value) {
            is TimestampWithoutTimezoneValue ->
                TimestampWithTimezoneValue(value.value.atOffset(ZoneOffset.UTC))
            is TimeWithoutTimezoneValue ->
                TimeWithTimezoneValue(value.value.atOffset(ZoneOffset.UTC))
            is ArrayValue -> ArrayValue(value.values.map { timestampsToInteger(it) })
            is ObjectValue ->
                ObjectValue(
                    value.values.mapValuesTo(linkedMapOf()) { (_, v) -> timestampsToInteger(v) }
                )
            else -> value
        }
}
