/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import java.util.function.Consumer
import java.util.function.Function
import java.util.stream.Stream

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
        return transactions
            .stream()
            .map { transaction: List<String> ->
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
            .toList()
    }

    init {
        transactions.forEach(
            Consumer { transaction: List<String> ->
                require(!transaction.isEmpty()) { "Transaction must not be empty" }
                require(!transaction.stream().anyMatch { s: String -> s.isNullOrEmpty() }) {
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
            return create(
                statements
                    .stream()
                    .map(Function<String, List<String>> { o: String -> listOf(o) })
                    .toList()
            )
        }

        @JvmStatic
        fun separately(vararg statements: String): Sql {
            return separately(Stream.of(*statements).toList())
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
            return create(
                Stream.of(*sqls).flatMap { sql: Sql -> sql.transactions.stream() }.toList()
            )
        }

        @JvmStatic
        fun concat(sqls: List<Sql>): Sql {
            return create(sqls.stream().flatMap { sql: Sql -> sql.transactions.stream() }.toList())
        }

        /**
         * Utility method to create a Sql object without empty statements/transactions, and
         * appending semicolons when needed.
         */
        @JvmStatic
        fun create(transactions: List<List<String>>): Sql {
            return Sql(
                transactions
                    .stream()
                    .map { transaction: List<String> ->
                        transaction
                            .stream()
                            .filter { statement: String -> !statement.isNullOrEmpty() }
                            .map internalMap@{ statement: String ->
                                if (!statement.trim { it <= ' ' }.endsWith(";")) {
                                    return@internalMap "$statement;"
                                }
                                statement
                            }
                            .toList()
                    }
                    .filter { transaction: List<String> -> !transaction.isEmpty() }
                    .toList()
            )
        }
    }
}
