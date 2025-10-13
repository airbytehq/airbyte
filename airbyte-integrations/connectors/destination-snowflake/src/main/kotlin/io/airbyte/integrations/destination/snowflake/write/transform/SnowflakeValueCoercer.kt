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

// https://docs.snowflake.com/en/sql-reference/data-types-numeric#label-data-type-float
internal val FLOAT_MAX = BigDecimal("9007199254740991")
internal val FLOAT_MIN = BigDecimal("-9007199254740991")
internal val FLOAT_RANGE = FLOAT_MIN..FLOAT_MAX

// https://docs.snowflake.com/en/sql-reference/data-types-semistructured#characteristics-of-a-variant-value
internal const val VARIANT_LIMIT_BYTES = 128 * 1024 * 1024
// https://docs.snowflake.com/en/sql-reference/data-types-text#varchar
internal const val VARCHAR_LIMIT_BYTES = 16 * 1024 * 1024

// UTF-8 has max 4 bytes per char, so anything under this length is safe
internal const val MAX_UTF_8_VARIANT_LENGTH_UNDER_LIMIT = VARIANT_LIMIT_BYTES / 4 // (134217728 / 4)
internal const val MAX_UTF_8_VARCHAR_LENGTH_UNDER_LIMIT = VARCHAR_LIMIT_BYTES / 4 // (16777216 / 4)

fun isValid(value: AirbyteValue): Boolean {
    return when (value) {
        is ArrayValue,
        is ObjectValue -> isVariantValid(value.toCsvValue().toString())
        is IntegerValue -> value.value in INT_RANGE
        is NumberValue -> value.value in FLOAT_RANGE
        is StringValue -> isVarcharValid(value.value)
        else -> true
    }
}

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

    override fun validate(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        if (!isValid(value.abValue)) {
            value.nullify(AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION)
        }

        return value
    }
}
