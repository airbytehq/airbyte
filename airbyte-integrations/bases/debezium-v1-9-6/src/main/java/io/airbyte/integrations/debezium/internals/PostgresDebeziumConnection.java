/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.debezium.connector.postgresql.connection.Lsn;
import io.debezium.jdbc.JdbcConnection.ResultSetMapper;
import io.debezium.jdbc.JdbcConnection.StatementFactory;
import java.sql.*;
import java.util.*;
import org.postgresql.util.PSQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is a helper for creating Debezium connections for Postgres
 */
public class PostgresDebeziumConnection {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresDebeziumConnection.class);
  private static final String ILLEGAL_CONNECTION_ERROR_MESSAGE = "The DB connection is not a valid replication connection";

  public static Connection createConnection(final JsonNode jdbcConfig) throws SQLException, IllegalStateException {
    Properties properties = new Properties();
    properties.setProperty("user", jdbcConfig.has(JdbcUtils.USERNAME_KEY) ? jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText()
        : null);
    properties.setProperty("password", jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText()
        : null);
    properties.setProperty("assumeMinServerVersion", "9.4");
    properties.setProperty("ApplicationName", "Airbyte Debezium Streaming");
    properties.setProperty("replication", "database");
    properties.setProperty("preferQueryMode", "simple"); // replication protocol only supports simple query mode

    LOGGER.info("Creating a CDC connection.");
    final String jdbcUrl = jdbcConfig.has(JdbcUtils.JDBC_URL_KEY) ? jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText()
        : String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            jdbcConfig.get(JdbcUtils.HOST_KEY).asText(),
            jdbcConfig.get(JdbcUtils.PORT_KEY).asInt(),
            jdbcConfig.get(JdbcUtils.DATABASE_KEY).asText());
    Connection connection;
    try {
      connection = DriverManager.getConnection(jdbcUrl, properties);
    } catch (PSQLException exception) {
      if (exception.getMessage().equals("FATAL: must be superuser or replication role to start walsender")) {
        throw new IllegalStateException(ILLEGAL_CONNECTION_ERROR_MESSAGE);
      }
      throw exception;
    }

    LOGGER.info("Validating connection.");
    validateReplicationConnection(connection);

    return connection;
  }

  private static void validateReplicationConnection(final Connection pgConnection) throws SQLException, IllegalStateException {
    final Lsn xlogStart = queryAndMap(pgConnection, "IDENTIFY_SYSTEM", Connection::createStatement, rs -> {
      if (!rs.next()) {
        throw new IllegalStateException(ILLEGAL_CONNECTION_ERROR_MESSAGE);
      }
      final String xlogpos = rs.getString("xlogpos");
      return Lsn.valueOf(xlogpos);
    });
  }

  private static <T> T queryAndMap(final Connection conn, final String query, final StatementFactory statementFactory, final ResultSetMapper<T> mapper)
      throws SQLException {
    Objects.requireNonNull(mapper, "Mapper must be provided");
    try (Statement statement = statementFactory.createStatement(conn)) {
      try (ResultSet resultSet = statement.executeQuery(query);) {
        return mapper.apply(resultSet);
      }
    }
  }

}
