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
import io.airbyte.integrations.destination.mssql.v2.model.SqlColumn
import io.airbyte.integrations.destination.mssql.v2.model.SqlTable
import java.sql.Types

/** CDK pipeline [AirbyteType] to SQL [Types] converter. */
class AirbyteTypeToSqlType {

    /**
     * Converts an [AirbyteType] to the associated SQL [Types] value.
     *
     * @param airbyteSchema The stream's Airbyte schema, represented as an [AirbyteType]
     * @return The associated SQL [Types] value.
     * @throws IllegalArgumentException if the [AirbyteType] is not supported.
     */
    fun convert(airbyteSchema: AirbyteType): Int {
        return when (airbyteSchema) {
            is ObjectType -> Types.LONGVARCHAR
            is ArrayType -> Types.LONGVARCHAR
            is ArrayTypeWithoutSchema -> Types.LONGVARCHAR
            is BooleanType -> Types.BOOLEAN
            is DateType -> Types.DATE
            is IntegerType -> Types.BIGINT
            is NumberType -> Types.DECIMAL
            is ObjectTypeWithEmptySchema -> Types.LONGVARCHAR
            is ObjectTypeWithoutSchema -> Types.LONGVARCHAR
            is StringType -> Types.VARCHAR
            is TimeTypeWithTimezone -> Types.TIME_WITH_TIMEZONE
            is TimeTypeWithoutTimezone -> Types.TIME
            is TimestampTypeWithTimezone -> Types.TIMESTAMP_WITH_TIMEZONE
            is TimestampTypeWithoutTimezone -> Types.TIMESTAMP
            is UnionType -> Types.LONGVARCHAR
            is UnknownType -> Types.LONGVARCHAR
        }
    }
}

