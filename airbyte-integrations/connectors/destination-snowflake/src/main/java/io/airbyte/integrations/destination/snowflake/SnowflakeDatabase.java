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

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.JDBCType;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.function.Function;
import java.util.function.Supplier;
import net.snowflake.client.core.QueryStatus;
import net.snowflake.client.jdbc.SnowflakeResultSet;
import net.snowflake.client.jdbc.SnowflakeStatement;

/**
 * SnowflakeDatabase contains helpers to create connections to and run queries on Snowflake.
 */
public class SnowflakeDatabase {

  private static final Duration NETWORK_TIMEOUT = Duration.ofMinutes(1);
  private static final Duration QUERY_TIMEOUT = Duration.ofMinutes(5);
  private static final Duration QUERY_CHECK_INTERVAL = Duration.ofSeconds(1);

  /**
   * Snowflake queries are issued asynchronously. If we need to wait to make sure a query was
   * completed, we need to periodically check if the status for the query has been updated. This
   * method waits until the result set is ready to be processed.
   * <p>
   * This must be called while the connection for the result set is still open.
   *
   * @param resultSet Snowflake result set
   * @return Snowflake result set that is ready for consumption.
   * @throws InterruptedException - thrown on interruption
   * @throws SQLException - thrown on unexpected query status
   */
  public static ResultSet waitForQuery(ResultSet resultSet) throws InterruptedException, SQLException {
    QueryStatus status = QueryStatus.RUNNING;

    // wait until async query completes
    while (status == QueryStatus.RUNNING || status == QueryStatus.RESUMING_WAREHOUSE) {
      Thread.sleep(QUERY_CHECK_INTERVAL.toMillis());
      status = resultSet.unwrap(SnowflakeResultSet.class).getStatus();
    }

    switch (status) {
      case FAILED_WITH_ERROR -> throw new SQLException(status.getErrorMessage());
      case SUCCESS -> {
        return resultSet;
      }
      default -> throw new SQLException("Unexpected query status: " + status);
    }
  }

  /**
   * Executes an async query and waits for completion. This method does not return a result.
   *
   * @param connectionFactory - a supplier for a Snowflake connection
   * @param query - single statement Snowflake query
   * @throws SQLException - thrown on sql failure
   * @throws InterruptedException - thrown on interruption
   */
  public static void executeSync(Supplier<Connection> connectionFactory, String query) throws SQLException, InterruptedException {
    executeSync(connectionFactory, query, false, rs -> null);
  }

  public static void executeSync(Supplier<Connection> connectionFactory, String query, boolean multipleStatements)
      throws SQLException, InterruptedException {
    executeSync(connectionFactory, query, multipleStatements, rs -> null);
  }

  /**
   * @param connectionFactory - a supplier for a Snowflake connection
   * @param query - Snowflake query
   * @param multipleStatements - true if the query contains multiple statements, false otherwise
   * @param transform - a function that transforms a result set into an object that can be used after
   *        the conn closes
   * @param <T> - output type
   * @return - output based on the transformed result set
   * @throws SQLException - thrown on sql failure
   * @throws InterruptedException - thrown on interruption
   */
  public static <T> T executeSync(Supplier<Connection> connectionFactory, String query, boolean multipleStatements, Function<ResultSet, T> transform)
      throws SQLException, InterruptedException {
    try (Connection conn = connectionFactory.get()) {
      final Statement statement = conn.createStatement();
      final SnowflakeStatement snowflakeStatement = statement.unwrap(SnowflakeStatement.class);

      if (multipleStatements) {
        snowflakeStatement.setParameter("MULTI_STATEMENT_COUNT", 0);
      }

      ResultSet resultSet = snowflakeStatement.executeAsyncQuery(query);
      return transform.apply(waitForQuery(resultSet));
    }
  }

  /**
   * @param config - json config input to the destination
   * @return a supplier for connections to Snowflake with default settings in place
   */
  public static Supplier<Connection> getConnectionFactory(JsonNode config) {
    final String connectUrl = String.format("jdbc:snowflake://%s", config.get("host").asText());

    final Properties properties = new Properties();

    properties.put("user", config.get("username").asText());
    properties.put("password", config.get("password").asText());
    properties.put("warehouse", config.get("warehouse").asText());
    properties.put("database", config.get("database").asText());
    properties.put("role", config.get("role").asText());
    properties.put("schema", config.get("schema").asText());

    properties.put("networkTimeout", Math.toIntExact(NETWORK_TIMEOUT.toSeconds()));
    properties.put("queryTimeout", Math.toIntExact(QUERY_TIMEOUT.toSeconds()));

    return () -> {
      try {
        return DriverManager.getConnection(connectUrl, properties);
      } catch (SQLException e) {
        throw new RuntimeException(e);
      }
    };
  }

  // todo (cgardens) - this only handles results without nesting. the type conversion isn't very well
  // tested and it makes some strong assumptions about how to handle nulls that may only make sense in
  // testing scenarios. if you are using this for a non-testing use case, this method wil need a
  // little more scrutiny. putting it here, because it is still a better base than nothing and if it's
  // not here it will never be found.
  public static List<JsonNode> resultSetToJson(ResultSet resultSet) throws SQLException {
    final List<JsonNode> jsons = new ArrayList<>();
    final int columnCount = resultSet.getMetaData().getColumnCount();

    while (resultSet.next()) {
      final Map<String, Object> json = new HashMap<>();

      for (int i = 1; i < columnCount; i++) {
        final String columnName = resultSet.getMetaData().getColumnName(i);
        final int columnType = resultSet.getMetaData().getColumnType(i);
        final JDBCType jdbcType = JDBCType.valueOf(columnType);

        // attempt to access the column. this allows us to know if it is null before we do type-specific
        // parsing. if it is null, we can move on. while awkward, this seems to be the agreed upon way of
        // checking for null values with jdbc.
        resultSet.getObject(i);
        if (resultSet.wasNull())
          continue;

        // convert to java types that will convert into reasonable json.
        switch (jdbcType) {
          case INTEGER, BIGINT, SMALLINT, TINYINT, BIT -> {
            json.put(columnName, resultSet.getLong(i));
          }
          case FLOAT, DOUBLE, NUMERIC, DECIMAL -> {
            json.put(columnName, resultSet.getDouble(i));
          }
          case NULL -> {
            // no op.
          }
          case BOOLEAN -> {
            json.put(columnName, resultSet.getBoolean(i));
          }
          default -> {
            json.put(columnName, resultSet.getString(i));
          }
        }
      }
      jsons.add(Jsons.jsonNode(json));
    }

    return jsons;
  }

}
