/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.transform

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton

/*
 * Limits defined for datatypes in Snowflake.
 * See https://docs.snowflake.com/en/sql-reference/data-types-numeric and
 * https://docs.snowflake.com/en/sql-reference/data-types-semistructured for more
 * information
 */
internal const val INTEGER_PRECISION_LIMIT = 38
internal const val MAXIMUM_FLOAT_VALUE = 9.007199E15f
internal const val MINIMUM_FLOAT_VALUE = -9.007199E15f
internal const val VARCHAR_LIMIT_BYTES = 134217728 // 128 MB
internal const val VARIANT_LIMIT_BYTES = 134217728 // 128 MB

@Singleton
class SnowflakeValueCoercer : ValueCoercer {
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        return value
    }

    override fun validate(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        when (val abValue = value.abValue) {
            is ArrayValue,
            is ObjectValue -> {
                if (abValue.toCsvValue().toString().toByteArray().size > VARIANT_LIMIT_BYTES) {
                    value.nullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                }
            }
            is IntegerValue -> {
                if (abValue.value.toBigDecimal().precision() > INTEGER_PRECISION_LIMIT) {
                    value.nullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                }
            }
            is NumberValue -> {
                if (abValue.value.toFloat() !in MINIMUM_FLOAT_VALUE..MAXIMUM_FLOAT_VALUE) {
                    value.nullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                }
            }
            is StringValue -> {
                if (abValue.toString().toByteArray().size > VARCHAR_LIMIT_BYTES) {
                    value.nullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                }
            }
            else -> {}
        }

        return value
    }
}
