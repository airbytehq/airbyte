package io.airbyte.integrations.destination.clickhouse_v2.write

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.integrations.destination.clickhouse_v2.write.ClickhouseValueValidator.Constants.DECIMAL64_MAX
import io.airbyte.integrations.destination.clickhouse_v2.write.ClickhouseValueValidator.Constants.DECIMAL64_MIN
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton
import java.math.BigDecimal

//@Suppress("deprecated")
@Singleton
class ClickhouseValueValidator {
    fun validateAndCoerce(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        when (val abValue = value.abValue) {
            // TODO: let's consider refactoring AirbyteValue so we don't have to do this
            is NumberValue -> if (abValue.value <= DECIMAL64_MIN || abValue.value >= DECIMAL64_MAX) {
                value.nullify(AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            }
//            is IntegerValue -> writer.setValue(columnName, abValue.value)
//            is DateValue -> writer.setValue(columnName, abValue.value)
//            is TimeWithTimezoneValue -> writer.setValue(columnName, abValue.value)
//            is TimeWithoutTimezoneValue -> writer.setValue(columnName, abValue.value)
//            is TimestampWithTimezoneValue -> writer.setValue(columnName, abValue.value)
//            is TimestampWithoutTimezoneValue -> writer.setValue(columnName, abValue.value)
            else -> {}
        }

        return value
    }

    object Constants {
        // copied from "deprecated" but still actively used
        // com.clickhouse.data.format.BinaryStreamUtils.DECIMAL64_MAX
        val DECIMAL64_MAX = BigDecimal("1000000000000000000");
        val DECIMAL64_MIN = BigDecimal("-1000000000000000000");
    }
}
