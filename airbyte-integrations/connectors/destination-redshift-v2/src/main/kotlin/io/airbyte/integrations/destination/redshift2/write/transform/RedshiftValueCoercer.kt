/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.write.transform

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
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

// https://docs.aws.amazon.com/redshift/latest/dg/r_Numeric_types201.html
// Redshift BIGINT range: -9223372036854775808 to 9223372036854775807 (same as int64)
internal val BIGINT_MAX = BigInteger("9223372036854775807")
internal val BIGINT_MIN = BigInteger("-9223372036854775808")
internal val BIGINT_RANGE = BIGINT_MIN..BIGINT_MAX

// https://docs.aws.amazon.com/redshift/latest/dg/r_Numeric_types201.html
// Redshift NUMERIC(38,9) has up to 38 total digits. For the coercer we use a generous bound
// matching Postgres (the COPY command handles precision/scale truncation gracefully).
internal val NUMERIC_MAX = BigDecimal("1E131072")
internal val NUMERIC_MIN = BigDecimal("-1E131072")

// https://docs.aws.amazon.com/redshift/latest/dg/r_Character_types.html
// Redshift VARCHAR(65535) maximum is 65,535 bytes
internal const val VARCHAR_LIMIT_BYTES = 65_535

// https://docs.aws.amazon.com/redshift/latest/dg/r_SUPER_type.html
// Redshift SUPER type maximum is 16 MB per value
internal const val SUPER_LIMIT_BYTES = 16 * 1024 * 1024

// UTF-8 uses at most 4 bytes per character — anything under this char count is guaranteed safe
internal const val VARCHAR_SAFE_CHAR_LENGTH = VARCHAR_LIMIT_BYTES / 4
internal const val SUPER_SAFE_CHAR_LENGTH = SUPER_LIMIT_BYTES / 4

// https://docs.aws.amazon.com/redshift/latest/dg/r_Datetime_types.html
// Redshift TIMESTAMP/TIMESTAMPTZ range: 4713 BC to 294276 AD (same as PostgreSQL)
internal const val TIMESTAMP_MIN_EPOCH_SECONDS = -210866760000L
internal const val TIMESTAMP_MAX_EPOCH_SECONDS = 9223371331200L

/**
 * Validates and transforms values to conform to Redshift's data type constraints.
 *
 * The CDK calls coercer methods in order: [representAs] -> [map] -> [validate].
 *
 * Key Redshift-specific limits enforced:
 * - **BIGINT**: int64 range (-2^63 to 2^63-1)
 * - **VARCHAR(65535)**: 65,535 bytes maximum
 * - **SUPER**: 16 MB maximum per value (for JSON objects/arrays)
 * - **TIMESTAMP**: 4713 BC to 294276 AD
 * - **Null bytes**: `\u0000` characters are stripped (Redshift rejects them in text)
 */
@Singleton
class RedshiftValueCoercer : ValueCoercer {

    /**
     * Serializes Union/Unknown typed values to JSON strings for storage in typed VARCHAR columns.
     *
     * In schema mode (the only mode v2 supports), union and unknown types are mapped to
     * `varchar(65535)` or `super` columns. Values must be serialized to a string representation
     * so they can be stored. [NullValue]s pass through unchanged.
     */
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        value.abValue =
            if (value.type is UnionType || value.type is UnknownType) {
                if (value.abValue is NullValue) {
                    value.abValue
                } else {
                    StringValue(value.abValue.serializeToString())
                }
            } else {
                value.abValue
            }
        return value
    }

    /**
     * Validates values against Redshift's data type constraints.
     *
     * Returns [ValidationResult.ShouldNullify] for values that exceed Redshift limits, or
     * [ValidationResult.Valid] for values that are safe to load. String values containing null
     * bytes (`\u0000`) are sanitized in-place before the size check.
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
            is StringValue -> {
                // Strip null bytes — Redshift rejects \u0000 in text fields
                if (abValue.value.contains('\u0000')) {
                    value.abValue = StringValue(abValue.value.replace("\u0000", ""))
                }

                val currentValue = (value.abValue as StringValue).value
                if (!isVarcharValid(currentValue)) {
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
            is TimestampWithTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond()
                if (
                    seconds < TIMESTAMP_MIN_EPOCH_SECONDS || seconds > TIMESTAMP_MAX_EPOCH_SECONDS
                ) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else {
                    ValidationResult.Valid
                }
            }
            is TimestampWithoutTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond(java.time.ZoneOffset.UTC)
                if (
                    seconds < TIMESTAMP_MIN_EPOCH_SECONDS || seconds > TIMESTAMP_MAX_EPOCH_SECONDS
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

/**
 * Checks whether a string value fits within Redshift's VARCHAR(65535) byte limit.
 *
 * Uses a fast-path: if `string.length <= 65535 / 4`, it's guaranteed to be under the byte limit
 * (UTF-8 uses at most 4 bytes per character). Only computes the actual UTF-8 byte length when the
 * string is long enough to potentially exceed the limit.
 */
internal fun isVarcharValid(s: String): Boolean {
    if (s.length <= VARCHAR_SAFE_CHAR_LENGTH) return true
    return utf8ByteLength(s) <= VARCHAR_LIMIT_BYTES
}

/**
 * Checks whether a serialized SUPER value fits within Redshift's 16 MB limit.
 *
 * Same fast-path optimization as [isVarcharValid].
 */
internal fun isSuperValid(s: String): Boolean {
    if (s.length <= SUPER_SAFE_CHAR_LENGTH) return true
    return utf8ByteLength(s) <= SUPER_LIMIT_BYTES
}

/** Computes the UTF-8 encoded byte length of a string without allocating a byte array. */
private fun utf8ByteLength(s: String): Int {
    var count = 0
    for (char in s) {
        val code = char.code
        count +=
            when {
                code <= 0x7F -> 1
                code <= 0x7FF -> 2
                // High surrogate (part of a surrogate pair → 4 bytes total, counted once)
                code in 0xD800..0xDBFF -> 4
                // Low surrogate: already counted with the high surrogate
                code in 0xDC00..0xDFFF -> 0
                else -> 3
            }
    }
    return count
}
