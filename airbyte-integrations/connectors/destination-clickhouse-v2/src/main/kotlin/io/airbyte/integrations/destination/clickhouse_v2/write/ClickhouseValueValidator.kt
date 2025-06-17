package io.airbyte.integrations.destination.clickhouse_v2.write

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.data_formats.RowBinaryFormatWriter
import com.clickhouse.data.ClickHouseChecker
import com.clickhouse.data.ClickHouseFormat
import com.clickhouse.data.format.BinaryStreamUtils.DECIMAL64_MAX
import com.clickhouse.data.format.BinaryStreamUtils.DECIMAL64_MIN
import com.google.common.annotations.VisibleForTesting
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.util.serializeToString
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import kotlinx.coroutines.future.await

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton

@Singleton
class ClickhouseValueValidator {
    fun validateAndCoerce(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        val abValue = value.abValue
        when (abValue) {
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
