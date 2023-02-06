/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.postgres.PostgresType.BIGINT;
import static io.airbyte.integrations.source.postgres.PostgresType.DATE;
import static io.airbyte.integrations.source.postgres.PostgresType.DECIMAL;
import static io.airbyte.integrations.source.postgres.PostgresType.DOUBLE;
import static io.airbyte.integrations.source.postgres.PostgresType.FLOAT;
import static io.airbyte.integrations.source.postgres.PostgresType.INTEGER;
import static io.airbyte.integrations.source.postgres.PostgresType.LONGVARCHAR;
import static io.airbyte.integrations.source.postgres.PostgresType.NUMERIC;
import static io.airbyte.integrations.source.postgres.PostgresType.NVARCHAR;
import static io.airbyte.integrations.source.postgres.PostgresType.REAL;
import static io.airbyte.integrations.source.postgres.PostgresType.SMALLINT;
import static io.airbyte.integrations.source.postgres.PostgresType.TIME;
import static io.airbyte.integrations.source.postgres.PostgresType.TIMESTAMP;
import static io.airbyte.integrations.source.postgres.PostgresType.TIMESTAMP_WITH_TIMEZONE;
import static io.airbyte.integrations.source.postgres.PostgresType.TIME_WITH_TIMEZONE;
import static io.airbyte.integrations.source.postgres.PostgresType.TINYINT;
import static io.airbyte.integrations.source.postgres.PostgresType.VARCHAR;

import com.fasterxml.jackson.databind.JsonNode;
import java.time.Duration;
import java.util.Optional;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresUtils {

  public static final Set<PostgresType> ALLOWED_CURSOR_TYPES = Set.of(TIMESTAMP, TIMESTAMP_WITH_TIMEZONE, TIME, TIME_WITH_TIMEZONE,
      DATE, TINYINT, SMALLINT, INTEGER, BIGINT, FLOAT, DOUBLE, REAL, NUMERIC, DECIMAL, NVARCHAR, VARCHAR, LONGVARCHAR);

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresUtils.class);

  private static final String PGOUTPUT_PLUGIN = "pgoutput";

  public static final Duration MIN_FIRST_RECORD_WAIT_TIME = Duration.ofMinutes(2);
  public static final Duration MAX_FIRST_RECORD_WAIT_TIME = Duration.ofMinutes(20);
  public static final Duration DEFAULT_FIRST_RECORD_WAIT_TIME = Duration.ofMinutes(5);

  public static String getPluginValue(final JsonNode field) {
    return field.has("plugin") ? field.get("plugin").asText() : PGOUTPUT_PLUGIN;
  }

  public static boolean isCdc(final JsonNode config) {
    final boolean isCdc = config.hasNonNull("replication_method")
        && config.get("replication_method").hasNonNull("replication_slot")
        && config.get("replication_method").hasNonNull("publication");
    LOGGER.info("using CDC: {}", isCdc);
    return isCdc;
  }

  public static boolean shouldFlushAfterSync(final JsonNode config) {
    final boolean shouldFlushAfterSync = config.hasNonNull("replication_method")
        && config.get("replication_method").hasNonNull("lsn_commit_behaviour")
        && config.get("replication_method").get("lsn_commit_behaviour").asText().equals("After loading Data in the destination");
    LOGGER.info("Should flush after sync: {}", shouldFlushAfterSync);
    return shouldFlushAfterSync;
  }

  public static Optional<Integer> getFirstRecordWaitSeconds(final JsonNode config) {
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
