/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write.transform

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger

/**
 * Databricks-specific value coercer that replicates v1's `try_cast()` safety net: out-of-range
 * values are nullified with a
 * [AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION] reason recorded in
 * metadata.
 */
@Singleton
class DatabricksValueCoercer : ValueCoercer {

    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        if (value.type is UnionType && value.abValue !is NullValue) {
            value.abValue = StringValue(value.abValue.serializeToString())
        }
        return value
    }

    override fun validate(value: EnrichedAirbyteValue): ValidationResult =
        when (val abValue = value.abValue) {
            is IntegerValue -> validIf(abValue.value in INT64_MIN..INT64_MAX)
            is NumberValue ->
                validIf(abValue.value > DECIMAL_38_10_MIN && abValue.value < DECIMAL_38_10_MAX)
            else -> ValidationResult.Valid
        }

    companion object {
        private fun nullify() =
            ValidationResult.ShouldNullify(
                AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            )

        private fun validIf(inRange: Boolean): ValidationResult =
            if (inRange) ValidationResult.Valid else nullify()

        // Databricks LONG is INT64
        val INT64_MAX = BigInteger(Long.MAX_VALUE.toString())
        val INT64_MIN = BigInteger(Long.MIN_VALUE.toString())

        // Databricks DECIMAL(38, 10): 28 integer digits + 10 fractional digits.
        val DECIMAL_38_10_MAX = BigDecimal("10000000000000000000000000000")
        val DECIMAL_38_10_MIN = BigDecimal("-10000000000000000000000000000")
    }
}
