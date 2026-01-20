/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.write.transform

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger

/*
 * Limits defined for datatypes in Redshift.
 * See https://docs.aws.amazon.com/redshift/latest/dg/c_Supported_data_types.html
 */

// BIGINT: -9223372036854775808 to 9223372036854775807 (64-bit signed)
val INT_MAX: BigInteger = Long.MAX_VALUE.toBigInteger()
val INT_MIN: BigInteger = Long.MIN_VALUE.toBigInteger()
internal val INT_RANGE = INT_MIN..INT_MAX

// DOUBLE PRECISION: IEEE 754 double (±1.7976931348623158E+308)
internal val FLOAT_MAX: BigDecimal = BigDecimal.valueOf(Double.MAX_VALUE)
internal val FLOAT_MIN: BigDecimal = BigDecimal.valueOf(-Double.MAX_VALUE)
internal val FLOAT_RANGE = FLOAT_MIN..FLOAT_MAX

/**
 * Redshift-specific value coercion and validation.
 *
 * Handles validation for:
 * - Integers: BIGINT has 64-bit range limits
 * - Numbers: DOUBLE PRECISION has IEEE 754 double range limits
 *
 * Values outside these ranges are nullified with DESTINATION_FIELD_SIZE_LIMITATION reason.
 */
@Singleton
class RedshiftValueCoercer : ValueCoercer {
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        // TODO replace nulls with sentinel value
        value.abValue =
            if (
                value.type.isArray ||
                    value.type.isObject ||
                    value.type is UnionType ||
                    value.type is UnknownType
            ) {
                StringValue(value.abValue.serializeToString())
            } else {
                value.abValue
            }
        return value
    }

    override fun validate(value: EnrichedAirbyteValue): ValidationResult {
        return when (val abValue = value.abValue) {
            is NumberValue -> {
                if (abValue.value in FLOAT_RANGE) {
                    ValidationResult.Valid
                } else {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                }
            }
            is IntegerValue -> {
                if (abValue.value in INT_RANGE) {
                    ValidationResult.Valid
                } else {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                }
            }
            else -> ValidationResult.Valid
        }
    }
}
