/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.medium

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.dataflow.transform.data.ValidationResultHandler
import jakarta.inject.Singleton

@Singleton
class JsonConverter(
    private val coercer: ValueCoercer,
    private val validationResultHandler: ValidationResultHandler,
) : MediumConverter {
    override fun convert(input: ConversionInput): Map<String, AirbyteValue> {
        val enriched =
            input.msg.asEnrichedDestinationRecordAirbyteValue(
                extractedAtAsTimestampWithTimezone = true
            )

        val result = HashMap<String, AirbyteValue>()

        // Column names are already mapped in the enriched value
        enriched.declaredFields.forEach { field ->
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

            result[field.key] = mappedValue.abValue
        }

        enriched.airbyteMetaFields.forEach { result[it.key] = it.value.abValue }

        return result
    }
}
