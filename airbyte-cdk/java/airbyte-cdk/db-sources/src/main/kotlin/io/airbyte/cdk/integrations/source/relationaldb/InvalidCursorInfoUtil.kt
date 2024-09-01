/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb

object InvalidCursorInfoUtil {
    fun getInvalidCursorConfigMessage(tablesWithInvalidCursor: List<InvalidCursorInfo>): String {
        return ("The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering with no null values as a cursor. " +
            tablesWithInvalidCursor.joinToString(",") { obj: InvalidCursorInfo -> obj.toString() })
    }

    class InvalidCursorInfo(
        tableName: String?,
        cursorColumnName: String,
        cursorSqlType: String,
        cause: String
    ) {
        override fun toString(): String {
            return "{" +
                "tableName='" +
                tableName +
                '\'' +
                ", cursorColumnName='" +
                cursorColumnName +
                '\'' +
                ", cursorSqlType=" +
                cursorSqlType +
                ", cause=" +
                cause +
                '}'
        }

        val tableName: String?
        val cursorColumnName: String
        val cursorSqlType: String
        val cause: String

        init {
            this.tableName = tableName
            this.cursorColumnName = cursorColumnName
            this.cursorSqlType = cursorSqlType
            this.cause = cause
        }
    }
}
