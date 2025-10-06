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
 * See https://docs.snowflake.com/en/sql-reference/data-types-numeric and
 * https://docs.snowflake.com/en/sql-reference/data-types-semistructured for more
 * information
 */
internal const val INTEGER_PRECISION_LIMIT = 38
internal val INT_MAX = BigInteger("99999999999999999999999999999999999999") // 38 9s 
internal val INT_MIN = BigInteger("-99999999999999999999999999999999999999") // 38 9s
internal val INT_RANGE = INT_MIN..INT_MAX
internal const val FLOAT_MAX = 9.007199E15f
internal const val FLOAT_MIN = -9.007199E15f
internal val DECIMAL_MAX = BigDecimal(FLOAT_MAX.toString())
internal val DECIMAL_MIN = BigDecimal(FLOAT_MIN.toString())
internal val DECIMAL_RANGE = DECIMAL_MIN..DECIMAL_MAX
internal const val VARCHAR_AND_VARIANT_LIMIT_BYTES = 134217728 // 128 MB
// UTF-8 has max 4 bytes per char, so we pre-calculate a safe length limit
internal const val MAX_UTF_8_STRING_LENGTH_UNDER_LIMIT = VARCHAR_AND_VARIANT_LIMIT_BYTES / 4

fun isValid(value: AirbyteValue): Boolean {
    return when (value) {
        is ArrayValue,
        is ObjectValue -> isStringValid(value.toCsvValue().toString())
        is IntegerValue -> value.value in INT_RANGE
        is NumberValue -> value.value in DECIMAL_RANGE
        is StringValue -> isStringValid(value.value)
        else -> true
    }
}

fun isStringValid(s: String): Boolean {
    // avoid expensive size calculation if we're safely under the limit
    if (s.length <= MAX_UTF_8_STRING_LENGTH_UNDER_LIMIT) return true

    // sums size without allocating extra byte arrays / copying
    return Utf8.encodedLength(s) <= VARCHAR_AND_VARIANT_LIMIT_BYTES
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
