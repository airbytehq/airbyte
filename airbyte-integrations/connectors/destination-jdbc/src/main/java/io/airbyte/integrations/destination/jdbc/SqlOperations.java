/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.jdbc;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.stream.Stream;

// todo (cgardens) - is it necessary to expose so much configurability in this interface. review if
// we can narrow the surface area.
public interface SqlOperations {

  /**
   * Create a schema with provided name if it does not already exist.
   *
   * @param schemaName name of schema.
   * @throws Exception exception
   */
  void createSchemaIfNotExists(JdbcDatabase database, String schemaName) throws Exception;

  /**
   * Create a table with provided name in provided schema if it does not already exist.
   *
   * @param schemaName name of schema
   * @param tableName name of table
   * @throws Exception exception
   */
  void createTableIfNotExists(JdbcDatabase database, String schemaName, String tableName) throws Exception;

  /**
   * Query to create a table with provided name in provided schema if it does not already exist.
   *
   * @param schemaName name of schema
   * @param tableName name of table
   * @return query
   */
  String createTableQuery(String schemaName, String tableName);

  /**
   * Drop the table if it exists.
   *
   * @param schemaName name of schema
   * @param tableName name of table
   * @throws Exception exception
   */
  void dropTableIfExists(JdbcDatabase database, String schemaName, String tableName) throws Exception;

  /**
   * Query to remove all records from a table. Assumes the table exists.
   *
   * @param schemaName name of schema
   * @param tableName name of table
   * @return query
   */
  String truncateTableQuery(String schemaName, String tableName);

  /**
   * Insert records into table. Assumes the table exists.
   *
   * @param records records to insert.
   * @param schemaName name of schema
   * @param tableName name of table
   * @throws Exception exception
   */
  void insertRecords(JdbcDatabase database, Stream<AirbyteRecordMessage> records, String schemaName, String tableName) throws Exception;

  /**
   * Query to copy all records from source table to destination table. Both tables must be in the
   * specified schema. Assumes both table exist.
   *
   * @param schemaName name of schema
   * @param sourceTableName name of source table
   * @param destinationTableName name of destination table
   * @return query
   */
  String copyTableQuery(String schemaName, String sourceTableName, String destinationTableName);

  /**
   * Given an arbitrary number of queries, execute a transaction.
   *
   * @param queries queries to execute
   * @throws Exception exception
   */
  void executeTransaction(JdbcDatabase database, String queries) throws Exception;

}
