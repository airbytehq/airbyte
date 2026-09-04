/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
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
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger

/*
 * Limits defined for data types in PostgreSQL.
 * See https://www.postgresql.org/docs/current/datatype.html for more information
 */

// https://www.postgresql.org/docs/current/datatype-numeric.html#DATATYPE-INT
// PostgreSQL BIGINT range: -9223372036854775808 to 9223372036854775807
internal val BIGINT_MAX = BigInteger("9223372036854775807")
internal val BIGINT_MIN = BigInteger("-9223372036854775808")
internal val BIGINT_RANGE = BIGINT_MIN..BIGINT_MAX

// https://www.postgresql.org/docs/current/datatype-numeric.html#DATATYPE-NUMERIC-DECIMAL
// PostgreSQL NUMERIC can have up to 131072 digits before the decimal point and up to 16383 after
// For practical purposes, we'll use a reasonable upper bound
internal val NUMERIC_MAX = BigDecimal("1E131072")
internal val NUMERIC_MIN = BigDecimal("-1E131072")

// https://www.postgresql.org/docs/current/datatype-character.html
// PostgreSQL TEXT and VARCHAR have no explicit byte limit, but the max field size is 1GB
internal const val TEXT_LIMIT_BYTES = 1 * 1024 * 1024 * 1024 // 1GB

// https://www.postgresql.org/docs/current/datatype-datetime.html
// PostgreSQL TIMESTAMP range: 4713 BC to 294276 AD
// In epoch seconds: roughly -210866760000 to 9223371331200
internal const val TIMESTAMP_MIN_EPOCH_SECONDS = -210866760000L
internal const val TIMESTAMP_MAX_EPOCH_SECONDS = 9223371331200L

private const val NUL = '\u0000'
private const val NUL_STRING = "\u0000"

@Singleton
class PostgresValueCoercer : ValueCoercer {
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        // Object, array, and union values are written to jsonb columns, which reject NUL
        // characters ("unsupported Unicode escape sequence"). Jackson emits NUL as a literal
        // six-character escape rather than dropping it, so sanitizing the serialized text
        // afterwards finds nothing — the value tree has to be cleaned before it is serialized.
        val sanitized =
            if (value.abValue.containsNullCharacter()) value.abValue.stripNullCharacters()
            else value.abValue

        value.abValue =
            if (value.type is UnionType || value.type is UnknownType) {
                // Don't serialize null values - keep them as NullValue
                if (sanitized is NullValue) {
                    sanitized
                } else {
                    StringValue(sanitized.serializeToString())
                }
            } else {
                sanitized
            }
        return value
    }

    override fun validate(value: EnrichedAirbyteValue): ValidationResult =
        when (val abValue = value.abValue) {
            is IntegerValue -> {
                // Validate against BIGINT range
                if (abValue.value !in BIGINT_RANGE) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            is NumberValue -> {
                // Validate against NUMERIC range
                if (abValue.value < NUMERIC_MIN || abValue.value > NUMERIC_MAX) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            is StringValue -> {
                // Validate string length (conservative check - actual byte size may vary with
                // encoding)
                // PostgreSQL uses UTF-8, so we check character count * 4 (max bytes per UTF-8 char)
                val currentValue = (value.abValue as StringValue).value
                if (currentValue.length * 4 > TEXT_LIMIT_BYTES) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            is TimestampWithTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond()
                if (
                    seconds < TIMESTAMP_MIN_EPOCH_SECONDS || seconds > TIMESTAMP_MAX_EPOCH_SECONDS
                ) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            is TimestampWithoutTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond(java.time.ZoneOffset.UTC)
                if (
                    seconds < TIMESTAMP_MIN_EPOCH_SECONDS || seconds > TIMESTAMP_MAX_EPOCH_SECONDS
                ) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            else -> {
                ValidationResult.Valid
            }
        }
}

/**
 * Cheap pre-check so the common (NUL-free) case walks the tree without allocating a sanitized copy
 * of it.
 */
private fun AirbyteValue.containsNullCharacter(): Boolean =
    when (this) {
        is StringValue -> value.contains(NUL)
        is ArrayValue -> values.any { it.containsNullCharacter() }
        is ObjectValue -> values.any { (k, v) -> k.contains(NUL) || v.containsNullCharacter() }
        else -> false
    }

// Postgres text cannot contain null bytes. We remove them.
// TODO: We don't currently set the metadata indicating that the data was modified (see
//  ValidationResultHandler). Doing so properly would require substantial CDK changes.
private fun AirbyteValue.stripNullCharacters(): AirbyteValue =
    when (this) {
        is StringValue -> StringValue(value.replace(NUL_STRING, ""))
        is ArrayValue -> ArrayValue(values.map { it.stripNullCharacters() })
        is ObjectValue -> {
            // jsonb rejects NUL in object keys too, not just in values. Stripping can collide two
            // keys into one ("a\u0000" and "a"); last one wins, which beats failing the record.
            val sanitized = LinkedHashMap<String, AirbyteValue>(values.size)
            values.forEach { (k, v) ->
                sanitized[k.replace(NUL_STRING, "")] = v.stripNullCharacters()
            }
            ObjectValue(sanitized)
        }
        else -> this
    }
