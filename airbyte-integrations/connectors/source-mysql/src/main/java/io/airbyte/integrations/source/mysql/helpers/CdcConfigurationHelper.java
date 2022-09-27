/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.time.Duration;
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
 * 3. configuring initial CDC wait time. TODO : There is a lot of shared logic for this functionality
 * between MySQL and Postgres. Refactor it to reduce code de-duplication.
 */
public class CdcConfigurationHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(CdcConfigurationHelper.class);
  private static final String LOG_BIN = "log_bin";
  private static final String BINLOG_FORMAT = "binlog_format";
  private static final String BINLOG_ROW_IMAGE = "binlog_row_image";

  public static final Duration MIN_FIRST_RECORD_WAIT_TIME = Duration.ofMinutes(2);
  public static final Duration MAX_FIRST_RECORD_WAIT_TIME = Duration.ofMinutes(20);
  public static final Duration DEFAULT_FIRST_RECORD_WAIT_TIME = Duration.ofMinutes(5);

  /**
   * Method will get required configurations for cdc sync
   *
   * @return list of List<CheckedConsumer<JdbcDatabase, Exception>>
   */
  public static List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations() {
    return List.of(getCheckOperation(LOG_BIN, "ON"),
        getCheckOperation(BINLOG_FORMAT, "ROW"),
        getCheckOperation(BINLOG_ROW_IMAGE, "FULL"));

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

  private static Optional<Integer> getFirstRecordWaitSeconds(final JsonNode config) {
    final JsonNode replicationMethod = config.get("replication_method");
    if (replicationMethod != null && replicationMethod.has("initial_waiting_seconds")) {
      final int seconds = config.get("replication_method").get("initial_waiting_seconds").asInt();
      return Optional.of(seconds);
    }
    return Optional.empty();
  }

  public static void checkFirstRecordWaitTime(final JsonNode config) {
    // we need to skip the check because in tests, we set initial_waiting_seconds
    // to 5 seconds for performance reasons, which is shorter than the minimum
    // value allowed in production
    if (config.has("is_test") && config.get("is_test").asBoolean()) {
      return;
    }

    final Optional<Integer> firstRecordWaitSeconds = getFirstRecordWaitSeconds(config);
    if (firstRecordWaitSeconds.isPresent()) {
      final int seconds = firstRecordWaitSeconds.get();
      if (seconds < MIN_FIRST_RECORD_WAIT_TIME.getSeconds() || seconds > MAX_FIRST_RECORD_WAIT_TIME.getSeconds()) {
        throw new IllegalArgumentException(
            String.format("initial_waiting_seconds must be between %d and %d seconds",
                MIN_FIRST_RECORD_WAIT_TIME.getSeconds(), MAX_FIRST_RECORD_WAIT_TIME.getSeconds()));
      }
    }
  }

  public static Duration getFirstRecordWaitTime(final JsonNode config) {
    final boolean isTest = config.has("is_test") && config.get("is_test").asBoolean();
    Duration firstRecordWaitTime = DEFAULT_FIRST_RECORD_WAIT_TIME;

    final Optional<Integer> firstRecordWaitSeconds = getFirstRecordWaitSeconds(config);
    if (firstRecordWaitSeconds.isPresent()) {
      firstRecordWaitTime = Duration.ofSeconds(firstRecordWaitSeconds.get());
      if (!isTest && firstRecordWaitTime.compareTo(MIN_FIRST_RECORD_WAIT_TIME) < 0) {
        LOGGER.warn("First record waiting time is overridden to {} minutes, which is the min time allowed for safety.",
            MIN_FIRST_RECORD_WAIT_TIME.toMinutes());
        firstRecordWaitTime = MIN_FIRST_RECORD_WAIT_TIME;
      } else if (!isTest && firstRecordWaitTime.compareTo(MAX_FIRST_RECORD_WAIT_TIME) > 0) {
        LOGGER.warn("First record waiting time is overridden to {} minutes, which is the max time allowed for safety.",
            MAX_FIRST_RECORD_WAIT_TIME.toMinutes());
        firstRecordWaitTime = MAX_FIRST_RECORD_WAIT_TIME;
      }
    }

    LOGGER.info("First record waiting time: {} seconds", firstRecordWaitTime.getSeconds());
    return firstRecordWaitTime;
  }

}
