/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.model

import java.sql.Types

/**
 * Representation of a colum in a SQL table.
 *
 * @param name The name of the column
 * @param type The data type of the column (see [Types] for values).
 * @param isPrimaryKey Whether the column represents a primary key.
 * @param isNullable Whether the column's value supports null values.
 */
data class SqlColumn(
    val name: String,
    val type: Int,
    val isPrimaryKey: Boolean = false,
    val isNullable: Boolean = false
)

/**
 * Representation of a SQL table.
 *
 * @param columns The list of columns in the table.
 */
data class SqlTable(val columns: List<SqlColumn>)

/**
 * Representation of a value in a SQL row/column cell.
 *
 * @param name The name of the column.
 * @param value The value of the row/column cell.
 * @param type The SQL type of the row/column cell (see [Types] for values).
 */
data class SqlTableRowValue(val name: String, val value: Any?, val type: Int)

/**
 * Representation of a row of values in a SQL table.
 *
 * @param values A list of values stored in the row.
 */
data class SqlTableRow(val values: List<SqlTableRowValue>)
