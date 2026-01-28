/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.write.transform

import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger

/**
 * Value coercer for S3 Data Lake destination.
 *
 * Applies Iceberg-specific transformations and validations:
 * - Stringifies complex types (objects, unions, schemaless arrays)
 * - Nulls out-of-range integers (outside Long range)
 * - Nulls out-of-range numbers (outside Double range)
 *
 * Logic extracted from IcebergUtil.toRecord() to work with the dataflow model.
 */
@Singleton
class S3DataLakeValueCoercer : ValueCoercer {
    companion object {
        private val MIN_LONG = BigInteger.valueOf(Long.MIN_VALUE)
        private val MAX_LONG = BigInteger.valueOf(Long.MAX_VALUE)
        private val MIN_DOUBLE = BigDecimal(-Double.MAX_VALUE)
        private val MAX_DOUBLE = BigDecimal(Double.MAX_VALUE)
    }

    /**
     * Transforms values after initial conversion.
     * Stringifies complex types that Iceberg represents as strings.
     */
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        // Stringify complex types - these are stored as JSON strings in Iceberg
        // Note: Null values should NOT be stringified
        if (value.abValue !is NullValue) {
            when (value.type) {
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema,
                is UnionType,
                is UnknownType,
                ArrayTypeWithoutSchema -> {
                    value.abValue = StringValue(value.abValue.serializeToString())
                }
                else -> {
                    // No transformation needed
                }
            }
        }
        return value
    }

    /**
     * Validates values against Iceberg/Parquet constraints.
     * Nullifies values that exceed destination limits.
     */
    override fun validate(value: EnrichedAirbyteValue): ValidationResult {
        return when (val abValue = value.abValue) {
            is IntegerValue -> {
                if (!isInLongRange(abValue.value)) {
                    ValidationResult.ShouldNullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
                } else {
                    ValidationResult.Valid
                }
            }
            is NumberValue -> {
                if (!isInDoubleRange(abValue.value)) {
                    ValidationResult.ShouldNullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
                } else {
                    ValidationResult.Valid
                }
            }
            else -> ValidationResult.Valid
        }
    }

    private fun isInLongRange(value: BigInteger): Boolean = value >= MIN_LONG && value <= MAX_LONG

    private fun isInDoubleRange(value: BigDecimal): Boolean =
        value >= MIN_DOUBLE && value <= MAX_DOUBLE
}
