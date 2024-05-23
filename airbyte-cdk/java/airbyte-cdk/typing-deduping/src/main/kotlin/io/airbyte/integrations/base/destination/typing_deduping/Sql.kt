/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import java.util.function.Consumer

/**
 * Represents a list of SQL transactions, where each transaction consists of one or more SQL
 * statements. Each transaction MUST NOT contain the BEGIN/COMMIT statements. Each inner list is a
 * single transaction, and each String is a single statement within that transaction.
 *
 * Most callers likely only need a single transaction, but e.g. BigQuery disallows running DDL
 * inside transactions, and so needs to run sequential "CREATE SCHEMA", "CREATE TABLE" as separate
 * transactions.
 *
 * Callers are encouraged to use the static factory methods instead of the public constructor.
 */
@JvmRecord
data class Sql(val transactions: List<List<String>>) {
    /**
     * @param begin The SQL statement to start a transaction, typically "BEGIN"
     * @param commit The SQL statement to commit a transaction, typically "COMMIT"
     * @return A list of SQL strings, each of which represents a transaction.
     */
    fun asSqlStrings(begin: String?, commit: String?): List<String> {
        return transactions.map { transaction: List<String> ->
            // If there's only one statement, we don't need to wrap it in a transaction.
            if (transaction.size == 1) {
                return@map transaction[0]
            }
            val builder = StringBuilder()
            builder.append(begin)
            builder.append(";\n")
            transaction.forEach(
                Consumer { statement: String ->
                    builder.append(statement)
                    // No semicolon - statements already end with a semicolon
                    builder.append("\n")
                }
            )
            builder.append(commit)
            builder.append(";\n")
            builder.toString()
        }
    }

    init {
        transactions.forEach(
            Consumer { transaction: List<String> ->
                require(!transaction.isEmpty()) { "Transaction must not be empty" }
                require(!transaction.any { it.isNullOrEmpty() }) {
                    "Transaction must not contain empty statements"
                }
            }
        )
    }

    companion object {
        /** Execute a list of SQL statements in a single transaction. */
        @JvmStatic
        fun transactionally(statements: List<String>): Sql {
            return create(java.util.List.of(statements))
        }

        @JvmStatic
        fun transactionally(vararg statements: String): Sql {
            return transactionally(listOf(*statements))
        }

        /** Execute each statement as its own transaction. */
        @JvmStatic
        fun separately(statements: List<String>): Sql {
            return create(statements.map { listOf(it) })
        }

        @JvmStatic
        fun separately(vararg statements: String): Sql {
            return separately(statements.asList())
        }

        /**
         * Convenience method for indicating intent. Equivalent to calling [.transactionally] or
         * [.separately] with the same string.
         */
        @JvmStatic
        fun of(statement: String): Sql {
            return transactionally(statement)
        }

        @JvmStatic
        fun concat(vararg sqls: Sql): Sql {
            return create(sqls.flatMap { sql: Sql -> sql.transactions })
        }

        @JvmStatic
        fun concat(sqls: List<Sql>): Sql {
            return create(sqls.flatMap { sql: Sql -> sql.transactions })
        }

        /**
         * Utility method to create a Sql object without empty statements/transactions, and
         * appending semicolons when needed.
         */
        @JvmStatic
        fun create(transactions: List<List<String>>): Sql {
            return Sql(
                transactions
                    .map { transaction: List<String> ->
                        transaction
                            .filter { statement: String -> !statement.isNullOrEmpty() }
                            .map internalMap@{ statement: String ->
                                if (!statement.trim { it <= ' ' }.endsWith(";")) {
                                    return@internalMap "$statement;"
                                }
                                statement
                            }
                    }
                    .filter { transaction: List<String> -> !transaction.isEmpty() }
            )
        }
    }
}
