/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.sql

/**
 * Escapes a StarRocks identifier (database/table/column name) by doubling any internal backtick and
 * wrapping the result in backticks. ALL DDL identifier interpolation must go through this — a raw
 * backtick in a source-controlled name would otherwise break out of the quoted identifier (issue
 * #36). Use PreparedStatement parameters for values; this is for identifiers only.
 */
internal fun quoteIdent(name: String): String = "`" + name.replace("`", "``") + "`"

/** Single-quoted SQL string literal with embedded quotes doubled. */
internal fun sqlStringLiteral(value: String): String = "'" + value.replace("'", "''") + "'"

/** A resolved StarRocks column (name + SQL type + nullability). */
data class StarrocksColumn(val name: String, val sqlType: String, val nullable: Boolean)

/** StarRocks table key model: PRIMARY KEY (dedup/upsert) vs DUPLICATE KEY (append). */
enum class KeyModel {
    PRIMARY,
    DUPLICATE,
}

/**
 * Pure StarRocks DDL string generation (no CDK types — unit-testable in isolation). The
 * StreamTableSchema -> (columns, keys, model) extraction lives in the Airbyte client (issue #11).
 *
 * StarRocks PRIMARY KEY tables require the key columns to be declared FIRST, in key order, and NOT
 * NULL — this generator enforces both.
 */
class StarrocksSqlGenerator {

    fun createDatabase(database: String): String =
        "CREATE DATABASE IF NOT EXISTS ${quoteIdent(database)}"

    fun dropTable(database: String, table: String): String =
        "DROP TABLE IF EXISTS ${quoteIdent(database)}.${quoteIdent(table)}"

    /**
     * Atomically swaps the data and schema of [target] with [withTable]. StarRocks requires the
     * `SWAP WITH` operand to be an UNQUALIFIED table name (resolved in [target]'s database); a
     * `db.table` operand is a syntax error. Both tables must therefore live in [database].
     */
    fun swapTable(database: String, target: String, withTable: String): String =
        "ALTER TABLE ${quoteIdent(database)}.${quoteIdent(target)} SWAP WITH ${quoteIdent(withTable)}"

    /**
     * In-place column evolution as ONE statement. StarRocks runs every `ALTER TABLE ... COLUMN` as
     * an asynchronous schema-change job and rejects a second ALTER on the same table while one is
     * still in flight ("A schema change operation is in progress"), so all adds and drops for a
     * sync must be issued as comma-separated clauses of a single ALTER. Added columns are always
     * NULL-able: StarRocks cannot ADD a NOT NULL column without a DEFAULT to a populated table.
     */
    /**
     * Most recent schema-change job on [table]. StarRocks rejects `SHOW ALTER` in the prepared
     * statement protocol, so the table name is inlined as an escaped string literal.
     */
    fun showLatestSchemaChange(database: String, table: String): String =
        "SHOW ALTER TABLE COLUMN FROM ${quoteIdent(database)} " +
            "WHERE TableName = ${sqlStringLiteral(table)} ORDER BY CreateTime DESC LIMIT 1"

    fun alterTableColumns(
        database: String,
        table: String,
        addColumns: List<StarrocksColumn>,
        dropColumns: List<String>,
    ): String {
        require(addColumns.isNotEmpty() || dropColumns.isNotEmpty()) {
            "alterTableColumns: nothing to alter"
        }
        val clauses =
            addColumns.map { "ADD COLUMN ${quoteIdent(it.name)} ${it.sqlType} NULL" } +
                dropColumns.map { "DROP COLUMN ${quoteIdent(it)}" }
        return "ALTER TABLE ${quoteIdent(database)}.${quoteIdent(table)} ${clauses.joinToString(", ")}"
    }

    fun createTable(
        database: String,
        table: String,
        columns: List<StarrocksColumn>,
        keyColumns: List<String>,
        model: KeyModel,
        ifNotExists: Boolean = true,
        replicationNum: Int? = null,
    ): String {
        require(keyColumns.isNotEmpty()) { "keyColumns must not be empty" }
        val byName = columns.associateBy { it.name }
        keyColumns.forEach {
            require(byName.containsKey(it)) { "key column '$it' is not present in columns" }
        }

        // Key columns first, in key order, forced NOT NULL; then the remaining columns in order.
        val keyDefs = keyColumns.map { byName.getValue(it).copy(nullable = false) }
        val rest = columns.filter { it.name !in keyColumns }
        val columnLines =
            (keyDefs + rest).joinToString(",\n") { col ->
                "  ${quoteIdent(col.name)} ${col.sqlType}${if (col.nullable) "" else " NOT NULL"}"
            }

        val keyClause = if (model == KeyModel.PRIMARY) "PRIMARY KEY" else "DUPLICATE KEY"
        val keyList = keyColumns.joinToString(", ") { quoteIdent(it) }
        val exists = if (ifNotExists) "IF NOT EXISTS " else ""

        return buildString {
            append("CREATE TABLE ")
                .append(exists)
                .append("${quoteIdent(database)}.${quoteIdent(table)} (\n")
            append(columnLines).append('\n')
            append(")\n")
            append("$keyClause ($keyList)\n")
            append("DISTRIBUTED BY HASH ($keyList)")
            // Optional replication_num for single-BE / shared-nothing clusters (issue #58). Unset
            // =>
            // no PROPERTIES => FE default (correct for shared-data and multi-BE).
            if (replicationNum != null) {
                append("\nPROPERTIES (\"replication_num\" = \"$replicationNum\")")
            }
        }
    }
}
