/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write.transform

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger

/*
 * Redshift-specific data type limits.
 * See https://docs.aws.amazon.com/redshift/latest/dg/c_Supported_data_types.html
 */

internal val BIGINT_MAX = BigInteger("9223372036854775807")
internal val BIGINT_MIN = BigInteger("-9223372036854775808")
internal val BIGINT_RANGE = BIGINT_MIN..BIGINT_MAX
// For NUMERIC(38,9) the max representable value has 29 integer digits + 9 fractional digits.
internal val NUMERIC_MAX = BigDecimal("99999999999999999999999999999.999999999")
internal val NUMERIC_MIN = BigDecimal("-99999999999999999999999999999.999999999")
internal const val SUPER_LIMIT_BYTES = 16 * 1024 * 1024
internal const val VARCHAR_MAX_BYTES = 65_535

/**
 * Validates and transforms values to conform to Redshift's data type constraints. The CDK calls
 * coercer methods in order: [representAs] -> [map] -> [validate].
 *
 * Key Redshift-specific limits enforced:
 * - **BIGINT**: int64 range (-2^63 to 2^63-1)
 * - **SUPER**: 16 MB maximum per value (for JSON objects/arrays)
 */
@Singleton
class RedshiftValueCoercer : ValueCoercer {

    /**
     * Serializes Union typed values to JSON strings for storage in VARCHAR columns.
     *
     * Union types are mapped to `varchar(65535)` columns. Values must be serialized to a JSON
     * string representation so they can be stored. [NullValue]s pass through unchanged.
     */
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        if (value.type is UnionType && value.abValue !is NullValue) {
            value.abValue = StringValue(value.abValue.serializeToString())
        }
        return value
    }

    /**
     * Validates values against Redshift's data type constraints.
     *
     * Returns [ValidationResult.ShouldNullify] for values that exceed Redshift limits, or
     * [ValidationResult.Valid] for values that are safe to load.
     */
    override fun validate(value: EnrichedAirbyteValue): ValidationResult =
        when (val abValue = value.abValue) {
            is IntegerValue -> {
                if (abValue.value !in BIGINT_RANGE) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else {
                    ValidationResult.Valid
                }
            }
            is NumberValue -> {
                if (abValue.value < NUMERIC_MIN || abValue.value > NUMERIC_MAX) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else {
                    ValidationResult.Valid
                }
            }
            is ArrayValue,
            is ObjectValue -> {
                if (!isSuperValid(abValue.toCsvValue().toString())) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else {
                    ValidationResult.Valid
                }
            }
            is StringValue -> {
                val len = abValue.value.length
                if (len > VARCHAR_MAX_BYTES) {
                    // Fast fail: more chars than bytes allowed — can't fit even as pure ASCII.
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else if (
                    // Worst case each char maybe 4 bytes
                    // Compute exact byte size to confirm using toByteArray, which is expensive
                    len * 4 > VARCHAR_MAX_BYTES &&
                        abValue.value.toByteArray(Charsets.UTF_8).size > VARCHAR_MAX_BYTES
                ) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else {
                    ValidationResult.Valid
                }
            }
            else -> ValidationResult.Valid
        }
}

/** Checks whether a serialized SUPER value fits within Redshift's 16 MB limit. */
internal fun isSuperValid(s: String): Boolean = s.length <= SUPER_LIMIT_BYTES
