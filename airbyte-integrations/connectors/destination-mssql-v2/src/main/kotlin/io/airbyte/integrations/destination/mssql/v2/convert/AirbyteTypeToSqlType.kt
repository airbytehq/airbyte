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
            is ObjectType -> Types.BLOB
            is ArrayType -> Types.BLOB
            is ArrayTypeWithoutSchema -> Types.BLOB
            is BooleanType -> Types.BOOLEAN
            is DateType -> Types.DATE
            is IntegerType -> Types.BIGINT
            is NumberType -> Types.DECIMAL
            is ObjectTypeWithEmptySchema -> Types.BLOB
            is ObjectTypeWithoutSchema -> Types.BLOB
            is StringType -> Types.VARCHAR
            is TimeTypeWithTimezone -> Types.TIME_WITH_TIMEZONE
            is TimeTypeWithoutTimezone -> Types.TIME
            is TimestampTypeWithTimezone -> Types.TIMESTAMP_WITH_TIMEZONE
            is TimestampTypeWithoutTimezone -> Types.TIMESTAMP
            is UnionType -> Types.BLOB
            is UnknownType -> Types.BLOB
        }
    }
}

/**
 * Extension function that converts an [ObjectType] into a [SqlTable] that can be used to define a
 * SQL table.
 *
 * @param primaryKeys The list of configured primary key properties that should be treated as
 * primary keys in the generated [SqlTable]
 * @return The [SqlTable] that represents the table to be mapped to the stream represented by the
 * [ObjectType].
 */
fun ObjectType.toSqlTable(primaryKeys: List<List<String>>): SqlTable {
    val identifierFieldNames = primaryKeys.flatten().toSet()
    val sqlTypeConverter = AirbyteTypeToSqlType()
    val columns =
        this.properties.entries.map { (name, field) ->
            val isPrimaryKey = identifierFieldNames.contains(name)
            val isNullable = !isPrimaryKey && field.nullable
            SqlColumn(
                name = name,
                type = sqlTypeConverter.convert(field.type),
                isPrimaryKey = isPrimaryKey,
                isNullable = isNullable
            )
        }
    return SqlTable(columns = columns)
}
