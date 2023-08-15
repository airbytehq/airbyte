/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.db.jdbc.JdbcUtils;
import io.debezium.jdbc.JdbcConnection.ResultSetMapper;
import io.debezium.jdbc.JdbcConnection.StatementFactory;
import java.sql.*;
import java.util.*;
import org.postgresql.util.PSQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is a helper for creating replication connections for Postgres
 */
public class PostgresReplicationConnection {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresReplicationConnection.class);
  private static final String ILLEGAL_CONNECTION_ERROR_MESSAGE = "The DB connection is not a valid replication connection";
  public static final String REPLICATION_PRIVILEGE_ERROR_MESSAGE =
      "User '%s' does not have enough privileges for CDC replication. Please read the docs and add required privileges.";

  public static Connection createConnection(final JsonNode jdbcConfig) throws SQLException, IllegalStateException {
    try {
      Properties properties = new Properties();
      if (jdbcConfig.has(JdbcUtils.USERNAME_KEY)) {
        properties.setProperty("user", jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText());
      }

      if (jdbcConfig.has(JdbcUtils.PASSWORD_KEY)) {
        properties.setProperty("password", jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText());
      }

      properties.setProperty("assumeMinServerVersion", "9.4");
      properties.setProperty("ApplicationName", "Airbyte Debezium Streaming");
      properties.setProperty("replication", "database");
      properties.setProperty("preferQueryMode", "simple"); // replication protocol only supports simple query mode

      LOGGER.info("Creating a replication connection.");
      final Connection connection = DriverManager.getConnection(jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(), properties);

      LOGGER.info("Validating replication connection.");
      validateReplicationConnection(connection);
      return connection;
    } catch (final PSQLException exception) {
      if (exception.getMessage().equals("FATAL: must be superuser or replication role to start walsender")) {
        throw new ConfigErrorException(String.format(REPLICATION_PRIVILEGE_ERROR_MESSAGE, jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText()));
      }
      throw exception;
    }
  }

  private static void validateReplicationConnection(final Connection pgConnection) throws SQLException, IllegalStateException {
    queryAndMap(pgConnection, "IDENTIFY_SYSTEM", Connection::createStatement, rs -> {
      if (!rs.next()) {
        throw new IllegalStateException(ILLEGAL_CONNECTION_ERROR_MESSAGE);
      }
      return null;
    });
  }

  private static <T> T queryAndMap(final Connection conn,
                                   final String query,
                                   final StatementFactory statementFactory,
                                   final ResultSetMapper<T> mapper)
      throws SQLException {
    Objects.requireNonNull(mapper, "Mapper must be provided");
    try (Statement statement = statementFactory.createStatement(conn)) {
      try (ResultSet resultSet = statement.executeQuery(query);) {
        return mapper.apply(resultSet);
      }
    }
  }

}
