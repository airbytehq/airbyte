/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write.transform

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger

/**
 * Value coercer for GCS Data Lake destination.
 * Applies Iceberg-specific transformations and validations:
 * - Converts timestamps to milliseconds for _airbyte_extracted_at
 * - Stringifies objects/arrays (except _airbyte_meta which stays as struct)
 * - Nulls out-of-range integers (outside Long range)
 * - Nulls out-of-range numbers (outside Double range)
 * - Records all changes in airbyte_meta
 */
@Singleton
class GcsDataLakeValueCoercer : ValueCoercer {
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        // ValueCoercer operates on individual field values during Parse stage
        // However, timestamp→integer and object→string are already handled by the
        // Iceberg schema transformation (toIcebergSchema with stringifyObjects)
        // So we just pass through here
        return value
    }

    override fun validate(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        // Validate and null out-of-range values
        when (val abValue = value.abValue) {
            is IntegerValue -> {
                if (!isInLongRange(abValue.value)) {
                    value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
                }
            }
            is NumberValue -> {
                if (!isInDoubleRange(abValue.value)) {
                    value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
                }
            }
            else -> {
                // All other types are valid
            }
        }
        return value
    }

    private fun isInLongRange(value: BigInteger): Boolean =
        value >= BigInteger.valueOf(Long.MIN_VALUE) && value <= BigInteger.valueOf(Long.MAX_VALUE)

    private fun isInDoubleRange(value: BigDecimal): Boolean =
        value >= BigDecimal(-Double.MAX_VALUE) && value <= BigDecimal(Double.MAX_VALUE)
}
