/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write.transform

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger

/**
 * Value coercer for GCS Data Lake destination. Applies Iceberg-specific transformations and
 * validations:
 * - Stringifies union values (required for UnionBehavior.STRINGIFY)
 * - Nulls out-of-range integers (outside Long range)
 * - Nulls out-of-range numbers (outside Double range)
 * - Records all changes in airbyte_meta
 *
 * Note: Object/array stringification is handled by Iceberg schema transformation (toIcebergSchema
 * with stringifyObjects), not here.
 */
@Singleton
class GcsDataLakeValueCoercer : ValueCoercer {
    companion object {
        // Cache these BigDecimal/BigInteger constants to avoid expensive allocations
        // and BigInteger.pow() operations on every validation call
        private val MIN_LONG = BigInteger.valueOf(Long.MIN_VALUE)
        private val MAX_LONG = BigInteger.valueOf(Long.MAX_VALUE)
        private val MIN_DOUBLE = BigDecimal(-Double.MAX_VALUE)
        private val MAX_DOUBLE = BigDecimal(Double.MAX_VALUE)
    }
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        // Stringify union values - this happens during Parse stage where we still
        // have type information to know which fields are unions
        // Note: Null values should NOT be stringified - they stay as NullValue
        if (value.type is UnionType && value.abValue !is NullValue) {
            value.abValue = StringValue(value.abValue.serializeToString())
        }
        return value
    }

    override fun validate(value: EnrichedAirbyteValue): ValidationResult {
        // Validate and null out-of-range values
        when (val abValue = value.abValue) {
            is IntegerValue -> {
                if (!isInLongRange(abValue.value)) {
                    return ValidationResult.ShouldNullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
                }
            }
            is NumberValue -> {
                if (!isInDoubleRange(abValue.value)) {
                    return ValidationResult.ShouldNullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
                }
            }
            else -> {
                // All other types are valid
            }
        }
        return ValidationResult.Valid
    }

    private fun isInLongRange(value: BigInteger): Boolean = value >= MIN_LONG && value <= MAX_LONG

    private fun isInDoubleRange(value: BigDecimal): Boolean =
        value >= MIN_DOUBLE && value <= MAX_DOUBLE
}
