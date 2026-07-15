/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
    BIT(Types.BOOLEAN),
    BIGINT(Types.BIGINT),
    DECIMAL(Types.DECIMAL, sqlStringOverride = "DECIMAL(38, 8)"),
    VARCHAR(Types.VARCHAR, sqlStringOverride = "VARCHAR(MAX)"),
    VARCHAR_INDEX(Types.VARCHAR, sqlStringOverride = "VARCHAR(200)"),
    TEXT(Types.LONGVARCHAR),
    DATE(Types.DATE),
    TIME(Types.TIME),
    DATETIME(Types.TIMESTAMP),
    DATETIMEOFFSET(Types.TIMESTAMP_WITH_TIMEZONE),
    ;

    val sqlString: String = sqlStringOverride ?: name
}

object AirbyteTypeToMssqlType {
    fun convert(airbyteSchema: AirbyteType, isIndexed: Boolean = false): MssqlType {
        return when (airbyteSchema) {
            is BooleanType -> MssqlType.BIT
            is IntegerType -> MssqlType.BIGINT
            is NumberType -> MssqlType.DECIMAL
            is StringType -> if (isIndexed) MssqlType.VARCHAR_INDEX else MssqlType.VARCHAR
            is DateType -> MssqlType.DATE
            is TimeTypeWithoutTimezone -> MssqlType.TIME
            is TimestampTypeWithoutTimezone -> MssqlType.DATETIME
            is TimeTypeWithTimezone,
            is TimestampTypeWithTimezone -> MssqlType.DATETIMEOFFSET
            is ArrayType,
            is ArrayTypeWithoutSchema,
            is ObjectType,
            is ObjectTypeWithEmptySchema,
            is ObjectTypeWithoutSchema,
            is UnionType,
            is UnknownType -> MssqlType.TEXT
        }
    }
}
