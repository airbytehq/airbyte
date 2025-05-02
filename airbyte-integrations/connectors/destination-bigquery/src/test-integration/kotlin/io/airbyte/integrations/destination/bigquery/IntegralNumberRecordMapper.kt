/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord

/**
 * In nested JSON fields, bigquery converts integral numbers to integers. For example, if you try to
 * store `{"foo": 5.0}` in a JSON column, bigquery will actually store `{"foo": 5}`.
 *
 * (however, we don't want to modify root-level fields, because those are actual NUMERIC/INTEGER
 * columns).
 */
object IntegralNumberRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData = mapNestedIntegralNumberToInteger(expectedRecord.data, level = 0)
        return expectedRecord.copy(data = mappedData as ObjectValue)
    }

    private fun mapNestedIntegralNumberToInteger(value: AirbyteValue, level: Int): AirbyteValue =
        when (value) {
            is NumberValue -> {
                // level 0 is the root object
                // level 1 is any root-level fields
                // level 2 and above is anything inside a subobject/array
                if (level > 1) {
                    // can't use `.equals`, because that also checks for scale (i.e. 2.0 != 2)
                    if (value.value.toBigInteger().toBigDecimal().compareTo(value.value) == 0) {
                        IntegerValue(value.value.toBigInteger())
                    } else {
                        value
                    }
                } else {
                    value
                }
            }
            is ArrayValue ->
                ArrayValue(
                    value.values.map { mapNestedIntegralNumberToInteger(it, level = level + 1) }
                )
            is ObjectValue ->
                ObjectValue(
                    value.values.mapValuesTo(linkedMapOf()) { (_, v) ->
                        mapNestedIntegralNumberToInteger(v, level = level + 1)
                    }
                )
            else -> value
        }
}
