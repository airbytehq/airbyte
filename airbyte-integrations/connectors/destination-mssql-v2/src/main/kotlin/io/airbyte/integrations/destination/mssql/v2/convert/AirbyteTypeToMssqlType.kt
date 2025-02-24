/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.convert

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import java.sql.Types

enum class MssqlType(val sqlType: Int, val sqlStringOverride: String? = null) {
    TEXT(Types.LONGVARCHAR),
    BIT(Types.BOOLEAN),
    DATE(Types.DATE),
    BIGINT(Types.BIGINT),
    DECIMAL(Types.DECIMAL, sqlStringOverride = "DECIMAL(18, 8)"),
    VARCHAR(Types.VARCHAR, sqlStringOverride = "VARCHAR(MAX)"),
    VARCHAR_INDEX(Types.VARCHAR, sqlStringOverride = "VARCHAR(200)"),
    DATETIMEOFFSET(Types.TIMESTAMP_WITH_TIMEZONE),
    TIME(Types.TIME),
    DATETIME(Types.TIMESTAMP);

    val sqlString: String = sqlStringOverride ?: name
}

class AirbyteTypeToMssqlType {
    fun convert(airbyteSchema: AirbyteType, isIndexed: Boolean = false): MssqlType {
        return when (airbyteSchema) {
            is ObjectType -> MssqlType.TEXT
            is ArrayType -> MssqlType.TEXT
            is ArrayTypeWithoutSchema -> MssqlType.TEXT
            is BooleanType -> MssqlType.BIT
            is DateType -> MssqlType.DATE
            is IntegerType -> MssqlType.BIGINT
            is NumberType -> MssqlType.DECIMAL
            is ObjectTypeWithEmptySchema -> MssqlType.TEXT
            is ObjectTypeWithoutSchema -> MssqlType.TEXT
            is StringType -> if (isIndexed) MssqlType.VARCHAR_INDEX else MssqlType.VARCHAR
            is TimeTypeWithTimezone -> MssqlType.DATETIMEOFFSET
            is TimeTypeWithoutTimezone -> MssqlType.TIME
            is TimestampTypeWithTimezone -> MssqlType.DATETIMEOFFSET
            is TimestampTypeWithoutTimezone -> MssqlType.DATETIME
            is UnionType -> MssqlType.TEXT
            is UnknownType -> MssqlType.TEXT
        }
    }
}
