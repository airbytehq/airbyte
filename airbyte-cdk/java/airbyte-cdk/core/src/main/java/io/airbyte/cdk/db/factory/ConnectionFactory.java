/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.db.factory;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Map;
import java.util.Properties;

/**
 * This class as been added in order to be able to save the connection in a test. It was found that
 * the {@link javax.sql.DataSource} close method wasn't propagating the connection properly. It
 * shouldn't be needed in our application code.
 */
public class ConnectionFactory {

  /**
   * Construct a new {@link Connection} instance using the provided configuration.
   *
   * @param username The username of the database user.
   * @param password The password of the database user.
   * @param connectionProperties The extra properties to add to the connection.
   * @param jdbcConnectionString The JDBC connection string.
   * @return The configured {@link Connection}
   */
  public static Connection create(final String username,
                                  final String password,
                                  final Map<String, String> connectionProperties,
                                  final String jdbcConnectionString) {
    try {
      Properties properties = new Properties();
      properties.put("user", username);
      properties.put("password", password);
      connectionProperties.forEach((k, v) -> properties.put(k, v));

      return DriverManager.getConnection(jdbcConnectionString,
          properties);
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

}
