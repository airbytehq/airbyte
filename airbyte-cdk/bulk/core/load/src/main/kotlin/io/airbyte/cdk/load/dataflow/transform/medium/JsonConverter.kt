/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.medium

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.dataflow.transform.data.ValidationResultHandler
import jakarta.inject.Singleton

@Singleton
class JsonConverter(
    private val columnNameMapper: ColumnNameMapper,
    private val coercer: ValueCoercer,
    private val validationResultHandler: ValidationResultHandler,
) : MediumConverter {
    override fun convert(input: ConversionInput): Map<String, AirbyteValue> {
        val enriched =
            input.msg.asEnrichedDestinationRecordAirbyteValue(
                extractedAtAsTimestampWithTimezone = true
            )

        val munged = HashMap<String, AirbyteValue>()
        enriched.declaredFields.forEach { field ->
            val mappedKey =
                columnNameMapper.getMappedColumnName(input.msg.stream, field.key)
                    ?: field.key // fallback to the original key

            val mappedValue =
                field.value
                    .let { coercer.map(it) }
                    .let { value ->
                        validationResultHandler.handle(
                            partitionKey = input.partitionKey,
                            stream = input.msg.stream.mappedDescriptor,
                            result = coercer.validate(value),
                            value = value
                        )
                    }

            munged[mappedKey] = mappedValue.abValue
        }

        enriched.airbyteMetaFields.forEach { munged[it.key] = it.value.abValue }

        return munged
    }
}
