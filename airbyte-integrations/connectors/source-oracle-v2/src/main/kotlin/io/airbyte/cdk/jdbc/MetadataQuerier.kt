package io.airbyte.cdk.jdbc

import java.sql.JDBCType

/** A very thin abstraction around JDBC metadata queries, to help with testing. */
interface MetadataQuerier : AutoCloseable {

    /**
     * Queries the information_schema for all table names in the schemas specified by the connector
     * configuration.
     */
    fun tableNames(): List<TableName>

    /** Executes the provided sql query, discards the results, and extracts all column metadata. */
    fun columnMetadata(table: TableName, sql: String): List<ColumnMetadata>

    /** Queries the information_schema for all primary keys for the given table. */
    fun primaryKeys(table: TableName): List<List<String>>
}

/** Models a row for [java.sql.DatabaseMetaData.getTables]. */
data class TableName(
    val catalog: String? = null,
    val schema: String? = null,
    val name: String,
    val type: String,
)

/** Data class with one field for each [java.sql.ResultSetMetaData] column method. */
data class ColumnMetadata(
    val name: String,
    val type: JDBCType? = null,
    val typeName: String? = null,
    val klazz: Class<*>? = null,
    val isAutoIncrement: Boolean? = null,
    val isCaseSensitive: Boolean? = null,
    val isSearchable: Boolean? = null,
    val isCurrency: Boolean? = null,
    val isNullable: Boolean? = null,
    val isSigned: Boolean? = null,
    val displaySize: Int? = null,
    val precision: Int? = null,
    val scale: Int? = null,
)
