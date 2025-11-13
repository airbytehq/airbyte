package io.airbyte.integrations.destination.mysql_v2.sql

import io.airbyte.cdk.load.data.*
import jakarta.inject.Singleton

@Singleton
class MysqlColumnUtils {

    /**
     * Maps Airbyte types to MySQL column types.
     *
     * Type mappings:
     * - Boolean → BOOLEAN (TINYINT(1) internally)
     * - Integer → BIGINT
     * - Number → DECIMAL(38, 9)
     * - String → TEXT
     * - Date → DATE
     * - Time (with/without TZ) → TIME (MySQL doesn't support time with timezone)
     * - Timestamp with TZ → TIMESTAMP (stores in UTC, converts based on session TZ)
     * - Timestamp without TZ → DATETIME
     * - Array, Object, Union → JSON
     */
    fun toDialectType(type: AirbyteType): String =
        when (type) {
            BooleanType -> "BOOLEAN"
            IntegerType -> "BIGINT"
            NumberType -> "DECIMAL(38, 9)"
            StringType -> "TEXT"
            DateType -> "DATE"
            TimeTypeWithTimezone,
            TimeTypeWithoutTimezone -> "TIME"
            TimestampTypeWithTimezone -> "TIMESTAMP"
            TimestampTypeWithoutTimezone -> "DATETIME"
            is ArrayType,
            ArrayTypeWithoutSchema -> "JSON"
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema -> "JSON"
            is UnionType,
            is UnknownType -> "JSON"
            else -> "TEXT" // Fallback for unknown types
        }

    /**
     * Formats a column declaration with name, type, and nullability.
     */
    fun formatColumn(name: String, type: AirbyteType, nullable: Boolean): String {
        val typeDecl = toDialectType(type)
        val nullableDecl = if (nullable) "" else " NOT NULL"
        return "`$name` $typeDecl$nullableDecl"
    }

    /**
     * Quotes a column or table name with backticks.
     */
    fun String.quote() = "`$this`"

    /**
     * Fully qualified table name: `database`.`table`
     */
    fun fullyQualifiedName(database: String, tableName: String) =
        "`$database`.`$tableName`"
}
