/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.write.transform

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton

@Singleton
class DatabricksValueCoercer : ValueCoercer {

    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        if ((value.type is UnionType || value.type is UnknownType) && value.abValue !is NullValue) {
            value.abValue = StringValue(value.abValue.serializeToString())
        }
        return value
    }

    override fun validate(value: EnrichedAirbyteValue): ValidationResult =
        when (val abValue = value.abValue) {
            is IntegerValue -> validIf(abValue.value.bitLength() <= 63)
            is NumberValue -> {
                val integerDigits = abValue.value.precision() - abValue.value.scale()
                validIf(integerDigits <= DECIMAL_38_10_INTEGER_DIGITS)
            }
            else -> ValidationResult.Valid
        }

    companion object {
        private fun nullify() =
            ValidationResult.ShouldNullify(
                AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            )

        private fun validIf(inRange: Boolean): ValidationResult =
            if (inRange) ValidationResult.Valid else nullify()

        // Databricks DECIMAL(38, 10): 38 total digits, 10 fractional → 28 integer digits max
        private const val DECIMAL_38_10_INTEGER_DIGITS = 28
    }
}
