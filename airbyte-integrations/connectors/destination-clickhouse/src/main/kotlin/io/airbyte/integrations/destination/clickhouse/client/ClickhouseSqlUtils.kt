package io.airbyte.integrations.destination.clickhouse.client

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone


const val DATETIME_WITH_PRECISION = "DateTime64(3)"
const val DECIMAL_WITH_PRECISION_AND_SCALE = "Decimal(38, 9)"

val VALID_VERSION_COLUMN_TYPES =
    setOf(
        IntegerType::class,
        DateType::class,
        TimestampTypeWithTimezone::class,
        TimestampTypeWithoutTimezone::class,
    )

fun isValidVersionColumnType(airbyteType: AirbyteType): Boolean {
    // Must be of an integer type or of type Date/DateTime/DateTime64
    return VALID_VERSION_COLUMN_TYPES.any { it.isInstance(airbyteType) }
}


