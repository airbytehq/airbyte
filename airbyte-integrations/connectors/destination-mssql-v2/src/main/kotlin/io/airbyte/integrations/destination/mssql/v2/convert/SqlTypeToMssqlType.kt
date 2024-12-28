package io.airbyte.integrations.destination.mssql.v2.convert

import java.sql.Types

enum class MssqlType(val sqlType: Int) {
    TEXT(Types.LONGVARCHAR),
    BIT(Types.BOOLEAN),
    DATE(Types.DATE),
    BIGINT(Types.BIGINT),
    DECIMAL(Types.DECIMAL),
    VARCHAR(Types.VARCHAR),
    DATETIMEOFFSET(Types.TIMESTAMP_WITH_TIMEZONE),
    TIME(Types.TIME),
    DATETIME(Types.TIMESTAMP);

    val sqlString: String = if (sqlType == Types.VARCHAR) "VARCHAR(MAX)" else name

    companion object {
        val fromSqlType: Map<Int, MssqlType> =
            entries
                .associateByTo(mutableMapOf()) { it.sqlType }
                .apply { this[Types.TIME_WITH_TIMEZONE] = DATETIMEOFFSET }
                .toMap()
    }
}

class SqlTypeToMssqlType {
    fun convert(type: Int): MssqlType =
        MssqlType.fromSqlType.get(type) ?: throw IllegalArgumentException("type $type not found")
}
