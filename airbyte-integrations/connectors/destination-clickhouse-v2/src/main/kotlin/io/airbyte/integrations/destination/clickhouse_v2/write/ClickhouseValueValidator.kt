package io.airbyte.integrations.destination.clickhouse_v2.write

import com.clickhouse.data.format.BinaryStreamUtils.DECIMAL64_MAX
import com.clickhouse.data.format.BinaryStreamUtils.DECIMAL64_MIN
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton

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
}
