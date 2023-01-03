/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * todo (cgardens) - is it necessary to expose so much configurability in this interface. review if we can narrow the surface area.
 *
 * SQL queries required for successfully syncing to a destination connector. These operations include the ability to:
 * <ul>
 *   <li>Write - insert records from source connector</li>
 *   <li>Create - overloaded function but primarily to create tables if they don't exist (e.g. tmp tables to "stage" records before finalizing
 *   to final table</li>
 *   <li>Drop - removes a table from the schema</li>
 *   <li>Insert - move data from one table to another table - usually used for inserting data from tmp to final table (aka airbyte_raw)</li>
 * </ul>
 */
public interface SqlOperations {

  Logger LOGGER = LoggerFactory.getLogger(JdbcBufferedConsumerFactory.class);

  /**
   * Create a schema with provided name if it does not already exist.
   *
   * @param database Database that the connector is syncing
   * @param schemaName Name of schema.
   * @throws Exception exception
   */
  void createSchemaIfNotExists(JdbcDatabase database, String schemaName) throws Exception;

  /**
   * Denotes whether the schema exists in destination database
   *
   * @param database Database that the connector is syncing
   * @param schemaName Name of schema.
   * @return true if the schema exists in destination database, false if it doesn't
   */
  default boolean isSchemaExists(final JdbcDatabase database, final String schemaName) throws Exception {
    return false;
  }

  /**
   * Create a table with provided name in provided schema if it does not already exist.
   *
   * @param database Database that the connector is syncing
   * @param schemaName Name of schema
   * @param tableName Name of table
   * @throws Exception exception
   */
  void createTableIfNotExists(JdbcDatabase database, String schemaName, String tableName) throws Exception;

  /**
   * Query to create a table with provided name in provided schema if it does not already exist.
   *
   * @param database Database that the connector is syncing
   * @param schemaName Name of schema
   * @param tableName Name of table
   * @return query
   */
  String createTableQuery(JdbcDatabase database, String schemaName, String tableName);

  /**
   * Drop the table if it exists.
   *
   * @param schemaName Name of schema
   * @param tableName Name of table
   * @throws Exception exception
   */
  void dropTableIfExists(JdbcDatabase database, String schemaName, String tableName) throws Exception;

  /**
   * Query to remove all records from a table. Assumes the table exists.
   *
   * @param database Database that the connector is syncing
   * @param schemaName Name of schema
   * @param tableName Name of table
   * @return Query
   */
  String truncateTableQuery(JdbcDatabase database, String schemaName, String tableName);

  /**
   * Insert records into table. Assumes the table exists.
   *
   * @param database Database that the connector is syncing
   * @param records Records to insert.
   * @param schemaName Name of schema
   * @param tableName Name of table
   * @throws Exception exception
   */
  void insertRecords(JdbcDatabase database, List<AirbyteRecordMessage> records, String schemaName, String tableName) throws Exception;

  /**
   * Query to insert all records from source table to destination table. Both tables must be in the
   * specified schema. Assumes both table exist.
   *
   * <p>NOTE: this is an append-only operation meaning that data can be duplicated</p>
   *
   * @param database Database that the connector is syncing
   * @param schemaName Name of schema
   * @param sourceTableName Name of source table
   * @param destinationTableName Name of destination table
   * @return SQL Query string
   */
  String insertTableQuery(JdbcDatabase database, String schemaName, String sourceTableName, String destinationTableName);

  /**
   * Given an arbitrary number of queries, execute a transaction.
   *
   * @param database Database that the connector is syncing
   * @param queries Queries to execute
   * @throws Exception exception
   */
  void executeTransaction(JdbcDatabase database, List<String> queries) throws Exception;

  /**
   * Check if the data record is valid and ok to be written to destination
   */
  boolean isValidData(final JsonNode data);

  /**
   * Denotes whether the destination has the concept of schema or not
   *
   * @return true if the destination supports schema (ex: Postgres), false if it doesn't(MySQL)
   */
  boolean isSchemaRequired();

  /**
   * The method is responsible for executing some specific DB Engine logic in onClose method. We can
   * override this method to execute specific logic e.g. to handle any necessary migrations in the
   * destination, etc.
   * <p>
   * In next example you can see how migration from VARCHAR to SUPER column is handled for the
   * Redshift destination:
   *
   * @param database - Database that the connector is interacting with
   * @param writeConfigs - schemas and tables (streams) will be discovered
   * @see io.airbyte.integrations.destination.redshift.RedshiftSqlOperations#onDestinationCloseOperations
   */
  default void onDestinationCloseOperations(final JdbcDatabase database, final List<WriteConfig> writeConfigs) {
    // do nothing
    LOGGER.info("No onDestinationCloseOperations required for this destination.");
  }

}
