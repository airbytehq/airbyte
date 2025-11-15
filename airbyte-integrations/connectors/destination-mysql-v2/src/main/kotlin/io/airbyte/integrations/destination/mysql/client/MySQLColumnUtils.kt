package io.airbyte.integrations.destination.mysql.client

import io.airbyte.cdk.load.data.*
import jakarta.inject.Singleton

@Singleton
class MySQLColumnUtils {

    fun toDialectType(type: AirbyteType): String = when (type) {
        BooleanType -> "BOOLEAN"
        IntegerType -> "BIGINT"
        NumberType -> "DECIMAL(38, 9)"
        StringType -> "TEXT"  // MySQL TEXT for arbitrary length strings
        DateType -> "DATE"
        TimeTypeWithTimezone,
        TimeTypeWithoutTimezone -> "TIME"  // MySQL doesn't have TIME WITH TIME ZONE
        TimestampTypeWithTimezone,
        TimestampTypeWithoutTimezone -> "DATETIME(6)"  // MySQL DATETIME with microsecond precision
        is ArrayType, ArrayTypeWithoutSchema -> "JSON"  // MySQL native JSON type
        is ObjectType, ObjectTypeWithEmptySchema, ObjectTypeWithoutSchema -> "JSON"
        is UnionType, is UnknownType -> "JSON"  // JSON for complex types
        else -> "TEXT"
    }

    fun formatColumn(name: String, type: AirbyteType, nullable: Boolean): String {
        val typeDecl = toDialectType(type)
        val nullableDecl = if (nullable) "" else " NOT NULL"
        return "`$name` $typeDecl$nullableDecl"
    }
}
