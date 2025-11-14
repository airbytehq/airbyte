/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.transform

import com.google.common.base.Utf8
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
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
 * Limits defined for datatypes in Snowflake.
 * See https://docs.snowflake.com/en/sql-reference-data-types for more information
 */

// https://docs.snowflake.com/en/sql-reference/data-types-numeric#number
internal val INT_MAX = BigInteger("99999999999999999999999999999999999999") // 38 9s
internal val INT_MIN = BigInteger("-99999999999999999999999999999999999999") // 38 9s
internal val INT_RANGE = INT_MIN..INT_MAX
// Snowflake NUMBER (integer) has 38 digits of precision
internal const val INTEGER_PRECISION = 38

// https://docs.snowflake.com/en/sql-reference/data-types-numeric#label-data-type-float
internal val FLOAT_MAX = BigDecimal("9007199254740991")
internal val FLOAT_MIN = BigDecimal("-9007199254740991")
internal val FLOAT_RANGE = FLOAT_MIN..FLOAT_MAX
// Snowflake FLOAT has 15 significant digits of precision
internal const val FLOAT_PRECISION = 15

// https://docs.snowflake.com/en/sql-reference/data-types-semistructured#characteristics-of-a-variant-value
internal const val VARIANT_LIMIT_BYTES = 128 * 1024 * 1024
// https://docs.snowflake.com/en/sql-reference/data-types-text#varchar
internal const val VARCHAR_LIMIT_BYTES = 16 * 1024 * 1024

// UTF-8 has max 4 bytes per char, so anything under this length is safe
internal const val MAX_UTF_8_VARIANT_LENGTH_UNDER_LIMIT = VARIANT_LIMIT_BYTES / 4 // (134217728 / 4)
internal const val MAX_UTF_8_VARCHAR_LENGTH_UNDER_LIMIT = VARCHAR_LIMIT_BYTES / 4 // (16777216 / 4)

fun isVariantValid(s: String): Boolean {
    // avoid expensive size calculation if we're safely under the limit
    if (s.length <= MAX_UTF_8_VARIANT_LENGTH_UNDER_LIMIT) return true

    // sums size without allocating extra byte arrays / copying
    return Utf8.encodedLength(s) <= VARIANT_LIMIT_BYTES
}

fun isVarcharValid(s: String): Boolean {
    // avoid expensive size calculation if we're safely under the limit
    if (s.length <= MAX_UTF_8_VARCHAR_LENGTH_UNDER_LIMIT) return true

    // sums size without allocating extra byte arrays / copying
    return Utf8.encodedLength(s) <= VARCHAR_LIMIT_BYTES
}

/**
 * Truncates a BigDecimal to fit within a specified range and maximum precision.
 * Returns null if the value cannot be made to fit within the range.
 *
 * We can't just truncate to the max precision because that doesn't guarantee the value will be in range.
 * For example: 99999999999999999 (17 digits) truncated to 15 digits = 999999999999999,
 * which is still > FLOAT_MAX (9007199254740991). So we keep reducing precision until it fits.
 *
 * Example: truncateToRange(99999999999999999, -9007199254740991, 9007199254740991, 15)
 *          -> 9999999999999 (13 digits), which is now within range
 */
fun truncateToRange(value: BigDecimal, min: BigDecimal, max: BigDecimal, maxPrecision: Int): BigDecimal? {
    // Caller should have already checked if value is in range
    // Start with maxPrecision and reduce until it fits
    var precision = maxPrecision

    while (precision > 0) {
        val truncated = if (value.precision() > precision) {
            // To keep only the first N digits, we divide by 10^(precision - N),
            // truncate, then that's our result (without multiplying back)
            val digitsToRemove = value.precision() - precision
            val divisor = BigDecimal.TEN.pow(digitsToRemove)
            value.divide(divisor, 0, java.math.RoundingMode.DOWN)
        } else {
            // Value's precision is already <= target, it won't fit by truncating digits
            return null
        }

        if (truncated in min..max) return truncated
        precision--
    }

    return null // Cannot fit in range even with truncation
}

@Singleton
class SnowflakeValueCoercer : ValueCoercer {
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        value.abValue =
            if (value.type is UnionType) {
                StringValue(value.abValue.serializeToString())
            } else {
                value.abValue
            }
        return value
    }

    override fun validate(value: EnrichedAirbyteValue): ValidationResult {
        return when (val abValue = value.abValue) {
            is NumberValue -> {
                // Check if already in range
                if (abValue.value in FLOAT_RANGE) {
                    return ValidationResult.Valid
                }

                // Out of range, try to truncate
                val truncated = truncateToRange(abValue.value, FLOAT_MIN, FLOAT_MAX, FLOAT_PRECISION)
                when {
                    truncated == null -> {
                        // Cannot fit in range even with truncation -> nullify
                        ValidationResult.ShouldNullify(
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    }
                    else -> {
                        // Value was truncated to fit
                        ValidationResult.ShouldTruncate(
                            NumberValue(truncated),
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    }
                }
            }
            is IntegerValue -> {
                // Check if already in range
                if (abValue.value in INT_RANGE) {
                    return ValidationResult.Valid
                }

                // Out of range, try to truncate
                val truncated = truncateToRange(
                    BigDecimal(abValue.value),
                    BigDecimal(INT_MIN),
                    BigDecimal(INT_MAX),
                    INTEGER_PRECISION
                )
                when {
                    truncated == null -> {
                        // Cannot fit in range even with truncation -> nullify
                        ValidationResult.ShouldNullify(
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    }
                    else -> {
                        // Value was truncated to fit
                        ValidationResult.ShouldTruncate(
                            IntegerValue(truncated.toBigInteger()),
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    }
                }
            }
            is StringValue -> {
                if (!isVarcharValid(abValue.value)) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else {
                    ValidationResult.Valid
                }
            }
            is ArrayValue,
            is ObjectValue -> {
                if (!isVariantValid(abValue.toCsvValue().toString())) {
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
}
