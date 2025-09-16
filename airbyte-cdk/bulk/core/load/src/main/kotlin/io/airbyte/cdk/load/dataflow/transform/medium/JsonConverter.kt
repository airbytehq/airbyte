/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.medium

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.message.DestinationRecordRaw
import jakarta.inject.Singleton

@Singleton
class JsonConverter(
    private val columnNameMapper: ColumnNameMapper,
    private val coercer: ValueCoercer,
) {
    fun convert(msg: DestinationRecordRaw): HashMap<String, AirbyteValue> {
        val enriched =
            msg.asEnrichedDestinationRecordAirbyteValue(extractedAtAsTimestampWithTimezone = true)

        val munged = HashMap<String, AirbyteValue>()
        enriched.declaredFields.forEach { field ->
            val mappedKey =
                columnNameMapper.getMappedColumnName(msg.stream, field.key)
                    ?: field.key // fallback to original key

            val mappedValue = field.value.let { coercer.map(it) }.let { coercer.validate(it) }

            munged[mappedKey] = mappedValue.abValue
        }

        enriched.airbyteMetaFields.forEach { munged[it.key] = it.value.abValue }

        return munged
    }
}
