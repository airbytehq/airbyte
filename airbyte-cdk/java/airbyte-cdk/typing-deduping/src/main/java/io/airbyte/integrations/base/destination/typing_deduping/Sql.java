/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.Collections;
import java.util.List;
import java.util.stream.Stream;

/**
 * Represents a list of SQL transactions, where each transaction consists of one or more SQL
 * statements. Each transaction MUST NOT contain the BEGIN/COMMIT statements. Each inner list is a
 * single transaction, and each String is a single statement within that transaction.
 * <p>
 * Most callers likely only need a single transaction, but e.g. BigQuery disallows running DDL
 * inside transactions, and so needs to run sequential "CREATE SCHEMA", "CREATE TABLE" as separate
 * transactions.
 * <p>
 * Callers are encouraged to use the static factory methods instead of the public constructor.
 */
public record Sql(List<List<String>> transactions) {

  public Sql {
    transactions.forEach(transaction -> {
      if (transaction.isEmpty()) {
        throw new IllegalArgumentException("Transaction must not be empty");
      }
      if (transaction.stream().anyMatch(s -> s == null || s.isEmpty())) {
        throw new IllegalArgumentException("Transaction must not contain empty statements");
      }
    });
  }

  /**
   * @param begin The SQL statement to start a transaction, typically "BEGIN"
   * @param commit The SQL statement to commit a transaction, typically "COMMIT"
   * @return A list of SQL strings, each of which represents a transaction.
   */
  public List<String> asSqlStrings(final String begin, final String commit) {
    return transactions().stream()
        .map(transaction -> {
          // If there's only one statement, we don't need to wrap it in a transaction.
          if (transaction.size() == 1) {
            return transaction.get(0);
          }
          final StringBuilder builder = new StringBuilder();
          builder.append(begin);
          builder.append(";\n");
          transaction.forEach(statement -> {
            builder.append(statement);
            // No semicolon - statements already end with a semicolon
            builder.append("\n");
          });
          builder.append(commit);
          builder.append(";\n");
          return builder.toString();
        }).toList();
  }

  /**
   * Execute a list of SQL statements in a single transaction.
   */
  public static Sql transactionally(final List<String> statements) {
    return create(List.of(statements));
  }

  public static Sql transactionally(final String... statements) {
    return transactionally(Stream.of(statements).toList());
  }

  /**
   * Execute each statement as its own transaction.
   */
  public static Sql separately(final List<String> statements) {
    return create(statements.stream().map(Collections::singletonList).toList());
  }

  public static Sql separately(final String... statements) {
    return separately(Stream.of(statements).toList());
  }

  /**
   * Convenience method for indicating intent. Equivalent to calling
   * {@link #transactionally(String...)} or {@link #separately(String...)} with the same string.
   */
  public static Sql of(final String statement) {
    return transactionally(statement);
  }

  public static Sql concat(final Sql... sqls) {
    return create(Stream.of(sqls).flatMap(sql -> sql.transactions.stream()).toList());
  }

  public static Sql concat(final List<Sql> sqls) {
    return create(sqls.stream().flatMap(sql -> sql.transactions.stream()).toList());
  }

  /**
   * Utility method to create a Sql object without empty statements/transactions, and appending
   * semicolons when needed.
   */
  public static Sql create(final List<List<String>> transactions) {
    return new Sql(transactions.stream()
        .map(transaction -> transaction.stream()
            .filter(statement -> statement != null && !statement.isEmpty())
            .map(statement -> {
              if (!statement.trim().endsWith(";")) {
                return statement + ";";
              }
              return statement;
            })
            .toList())
        .filter(transaction -> !transaction.isEmpty())
        .toList());
  }

}
