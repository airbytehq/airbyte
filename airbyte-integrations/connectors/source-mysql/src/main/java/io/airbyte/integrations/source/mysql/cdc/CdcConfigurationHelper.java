/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.functional.CheckedConsumer;
import java.sql.SQLException;
import java.time.ZoneId;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Helper class for MySqlSource used to check cdc configuration in case of:
 * <p>
 * 1. adding new source and checking operations #getCheckOperations method.
 * </p>
 * <p>
 * 2. checking whether binlog required from saved cdc offset is available on mysql server
 * #checkBinlog method
 * </p>
 * 3. configuring initial CDC wait time. TODO : There is a lot of shared logic for this
 * functionality between MySQL and Postgres. Refactor it to reduce code de-duplication.
 */
public class CdcConfigurationHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(CdcConfigurationHelper.class);
  private static final String LOG_BIN = "log_bin";
  private static final String BINLOG_FORMAT = "binlog_format";
  private static final String BINLOG_ROW_IMAGE = "binlog_row_image";

  /**
   * Method will get required configurations for cdc sync
   *
   * @return list of List<CheckedConsumer<JdbcDatabase, Exception>>
   */
  public static List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations() {
    return List.of(getMasterStatusOperation(),
        getCheckOperation(LOG_BIN, "ON"),
        getCheckOperation(BINLOG_FORMAT, "ROW"),
        getCheckOperation(BINLOG_ROW_IMAGE, "FULL"));

  }

  // Checks whether the user has REPLICATION CLIENT privilege needed to query status information about
  // the binary log files, which are needed for CDC.
  private static CheckedConsumer<JdbcDatabase, Exception> getMasterStatusOperation() {
    return database -> {
      try {
        database.unsafeResultSetQuery(
            connection -> connection.createStatement().executeQuery("SHOW MASTER STATUS"),
            resultSet -> resultSet);
      } catch (final SQLException e) {
        throw new ConfigErrorException("Please grant REPLICATION CLIENT privilege, so that binary log files are available"
            + " for CDC mode.");
      }
    };
  }

  private static CheckedConsumer<JdbcDatabase, Exception> getCheckOperation(final String name, final String value) {
    return database -> {
      final List<String> result = database.queryStrings(
          connection -> connection.createStatement().executeQuery(String.format("show variables where Variable_name = '%s'", name)),
          resultSet -> resultSet.getString("Value"));

      if (result.size() != 1) {
        throw new RuntimeException("Could not query the variable " + name);
      }

      final String resultValue = result.get(0);
      if (!resultValue.equalsIgnoreCase(value)) {
        throw new RuntimeException(String.format("The variable \"%s\" should be set to \"%s\", but it is \"%s\"", name, value, resultValue));
      }
    };
  }

  private static Optional<String> getCdcServerTimezone(final JsonNode config) {
    final JsonNode replicationMethod = config.get("replication_method");
    if (replicationMethod != null && replicationMethod.has("server_time_zone")) {
      final String serverTimeZone = config.get("replication_method").get("server_time_zone").asText();
      return Optional.of(serverTimeZone);
    }
    return Optional.empty();
  }

  public static void checkServerTimeZoneConfig(final JsonNode config) {
    final Optional<String> serverTimeZone = getCdcServerTimezone(config);
    if (serverTimeZone.isPresent()) {
      final String timeZone = serverTimeZone.get();
      if (!timeZone.isEmpty() && !ZoneId.getAvailableZoneIds().contains((timeZone))) {
        throw new IllegalArgumentException(String.format("Given timezone %s is not valid. The given timezone must conform to the IANNA standard. "
            + "See https://www.iana.org/time-zones for more details", serverTimeZone.get()));
      }
    }
  }

}
