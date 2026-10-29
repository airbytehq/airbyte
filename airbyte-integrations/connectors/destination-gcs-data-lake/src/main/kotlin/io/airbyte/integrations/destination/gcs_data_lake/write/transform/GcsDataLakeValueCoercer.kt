/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write.transform

import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.ChangedValue
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger

/**
 * Value coercer for GCS Data Lake destination. Applies Iceberg-specific transformations and
 * validations. It matches S3 Data Lake's Iceberg munging, except scalar unknown-type values pass
 * through unchanged.
 * - Stringifies objects, unions, and schemaless complex values, recursing into schematized arrays
 * - Nulls out-of-range integers (outside Long range)
 * - Nulls out-of-range numbers (outside Double range)
 */
@Singleton
class GcsDataLakeValueCoercer(private val icebergUtil: IcebergUtil) : ValueCoercer {
    companion object {
        // Cache these BigDecimal/BigInteger constants to avoid expensive allocations
        // and BigInteger.pow() operations on every validation call
        private val MIN_LONG = BigInteger.valueOf(Long.MIN_VALUE)
        private val MAX_LONG = BigInteger.valueOf(Long.MAX_VALUE)
        private val MIN_DOUBLE = BigDecimal(-Double.MAX_VALUE)
        private val MAX_DOUBLE = BigDecimal(Double.MAX_VALUE)
    }

    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue =
        with(icebergUtil) {
            value.transformValueRecursingIntoArrays { element, elementType ->
                when (elementType) {
                    ArrayTypeWithoutSchema,
                    is ObjectType,
                    ObjectTypeWithEmptySchema,
                    ObjectTypeWithoutSchema,
                    is UnionType ->
                        ChangedValue(
                            StringValue(element.serializeToString()),
                            changeDescription = null,
                        )
                    is UnknownType ->
                        if (element is ObjectValue || element is ArrayValue) {
                            ChangedValue(
                                StringValue(element.serializeToString()),
                                changeDescription = null,
                            )
                        } else {
                            null
                        }
                    else -> null
                }
            }
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
