/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.convert

import java.sql.Types

enum class MssqlType(val sqlType: Int, val sqlStringOverride: String? = null) {
    TEXT(Types.LONGVARCHAR),
    BIT(Types.BOOLEAN),
    DATE(Types.DATE),
    BIGINT(Types.BIGINT),
    DECIMAL(Types.DECIMAL, sqlStringOverride = "DECIMAL(18, 8)"),
    VARCHAR(Types.VARCHAR, sqlStringOverride = "VARCHAR(MAX)"),
    DATETIMEOFFSET(Types.TIMESTAMP_WITH_TIMEZONE),
    TIME(Types.TIME),
    DATETIME(Types.TIMESTAMP);

    val sqlString: String = sqlStringOverride ?: name

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
