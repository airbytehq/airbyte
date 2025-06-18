package io.airbyte.integrations.destination.clickhouse_v2.write

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.integrations.destination.clickhouse_v2.write.ClickhouseValueValidator.Constants.DECIMAL64_MAX
import io.airbyte.integrations.destination.clickhouse_v2.write.ClickhouseValueValidator.Constants.DECIMAL64_MIN
import io.airbyte.integrations.destination.clickhouse_v2.write.ClickhouseValueValidator.Constants.INT64_MAX
import io.airbyte.integrations.destination.clickhouse_v2.write.ClickhouseValueValidator.Constants.INT64_MIN
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger

@Singleton
class ClickhouseValueValidator {
    /*
     * Mutative for performance reasons.
     */
    fun validateAndCoerce(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        when (val abValue = value.abValue) {
            is NumberValue -> if (abValue.value <= DECIMAL64_MIN || abValue.value >= DECIMAL64_MAX) {
                value.nullify(AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            }
            is IntegerValue -> if (abValue.value < INT64_MIN || abValue.value > INT64_MAX ) {
                value.nullify(AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            }
            else -> {}
        }

        return value
    }

    object Constants {
        // CH will overflow ints without erroring
        val INT64_MAX = BigInteger(Long.MAX_VALUE.toString())
        val INT64_MIN = BigInteger(Long.MIN_VALUE.toString())
        // copied from "deprecated" but still actively used
        // com.clickhouse.data.format.BinaryStreamUtils.DECIMAL64_MAX
        val DECIMAL64_MAX = BigDecimal("1000000000000000000")
        val DECIMAL64_MIN = BigDecimal("-1000000000000000000")
    }
}
