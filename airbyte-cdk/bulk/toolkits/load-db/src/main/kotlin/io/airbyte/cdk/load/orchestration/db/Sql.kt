/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db

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
data class Sql(val transactions: List<List<String>>) {
    /**
     * @param begin The SQL statement to start a transaction, typically "BEGIN"
     * @param commit The SQL statement to commit a transaction, typically "COMMIT"
     * @return A list of SQL strings, each of which represents a transaction.
     */
    fun asSqlStrings(begin: String, commit: String): List<String> {
        return transactions.map { transaction: List<String> ->
            // If there's only one statement, we don't need to wrap it in a transaction.
            if (transaction.size == 1) {
                return@map transaction[0]
            }
            val builder = StringBuilder()
            builder.append(begin)
            builder.append(";\n")
            transaction.forEach {
                builder.append(it)
                // No semicolon - statements already end with a semicolon
                builder.append("\n")
            }
            builder.append(commit)
            builder.append(";\n")
            builder.toString()
        }
    }

    init {
        transactions.forEach(
            Consumer { transaction: List<String> ->
                require(transaction.isNotEmpty()) { "Transaction must not be empty" }
                require(!transaction.any { it.isEmpty() }) {
                    "Transaction must not contain empty statements"
                }
            }
        )
    }

    companion object {
        /** Execute a list of SQL statements in a single transaction. */
        fun transactionally(statements: List<String>): Sql {
            return create(listOf(statements))
        }

        fun transactionally(vararg statements: String): Sql {
            return transactionally(listOf(*statements))
        }

        /** Execute each statement as its own transaction. */
        fun separately(statements: List<String>): Sql {
            return create(statements.map { listOf(it) })
        }

        fun separately(vararg statements: String): Sql {
            return separately(statements.asList())
        }

        /**
         * Convenience method for indicating intent. Equivalent to calling [transactionally] or
         * [.separately] with the same string.
         */
        fun of(statement: String): Sql {
            return transactionally(statement)
        }

        fun concat(vararg sqls: Sql): Sql {
            return create(sqls.flatMap { it.transactions })
        }

        fun concat(sqls: List<Sql>): Sql {
            return create(sqls.flatMap { it.transactions })
        }

        /**
         * Utility method to create a Sql object without empty statements/transactions, and
         * appending semicolons when needed.
         */
        fun create(transactions: List<List<String>>): Sql {
            return Sql(
                transactions
                    .map { transaction: List<String> ->
                        transaction
                            .map { it.trim() }
                            .filter { it.isNotEmpty() }
                            .map {
                                if (!it.endsWith(";")) {
                                    "$it;"
                                } else {
                                    it
                                }
                            }
                    }
                    .filter { it.isNotEmpty() }
            )
        }

        fun empty() = Sql(emptyList())
    }
}
