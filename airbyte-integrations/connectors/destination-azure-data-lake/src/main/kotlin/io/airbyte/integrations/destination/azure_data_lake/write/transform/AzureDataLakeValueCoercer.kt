/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_data_lake.write.transform

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger

/**
 * Value coercer for Azure Data Lake destination. Applies Iceberg-specific transformations and
 * validations:
 * - Stringifies complex types (objects, unions, schemaless arrays), including array elements
 * - Nulls out-of-range integers (outside Long range)
 * - Nulls out-of-range numbers (outside Double range)
 * - Records all changes in airbyte_meta
 *
 * Same as S3DataLakeValueCoercer. The Iceberg schema maps these types to string, so a value left
 * as an object (e.g. an element of an array of objects) fails in AirbyteValueToIcebergRecord with
 * "ObjectValue should be mapped to StructType".
 */
@Singleton
class AzureDataLakeValueCoercer(
    private val icebergUtil: IcebergUtil,
) : ValueCoercer {
    companion object {
        // Cache these BigDecimal/BigInteger constants to avoid expensive allocations
        // and BigInteger.pow() operations on every validation call
        private val MIN_LONG = BigInteger.valueOf(Long.MIN_VALUE)
        private val MAX_LONG = BigInteger.valueOf(Long.MAX_VALUE)
        private val MIN_DOUBLE = BigDecimal(-Double.MAX_VALUE)
        private val MAX_DOUBLE = BigDecimal(Double.MAX_VALUE)
    }
    // Runs in the Parse stage, where type information is still available. Null values stay
    // NullValue.
    override fun map(value: EnrichedAirbyteValue) = icebergUtil.mungeForIceberg(value)

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
