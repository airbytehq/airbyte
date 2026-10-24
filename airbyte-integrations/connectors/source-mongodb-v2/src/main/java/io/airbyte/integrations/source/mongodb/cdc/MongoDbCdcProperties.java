/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import java.time.Duration;
import java.util.Properties;

/**
 * Defines MongoDB specific CDC configuration properties for Debezium.
 */
public class MongoDbCdcProperties {

  static final String CAPTURE_MODE_KEY = "capture.mode";
  static final String CAPTURE_MODE_VALUE = "change_streams_update_full_with_pre_image";
  static final String CONNECTOR_CLASS_KEY = "connector.class";
  static final String CONNECTOR_CLASS_VALUE = "io.debezium.connector.mongodb.MongoDbConnector";
  static final String HEARTBEAT_FREQUENCY_MS = Long.toString(Duration.ofSeconds(10).toMillis());
  static final String HEARTBEAT_INTERVAL_KEY = "heartbeat.interval.ms";
  static final String SNAPSHOT_MODE_KEY = "snapshot.mode";
  static final String SNAPSHOT_MODE_VALUE = "no_data";
  // Debezium's AsyncEmbeddedEngine (starting with v3.2.0.Alpha1) includes a new engine start timeout
  // of 40 s. This
  // can be too low for a busy oplog, so we override it with 3 min, which was Debezium's previous
  // default.
  static final String TASK_MANAGEMENT_TIMEOUT_KEY = "internal.task.management.timeout.ms";
  static final String TASK_MANAGEMENT_TIMEOUT_MS = Long.toString(Duration.ofMinutes(3).toMillis());
  static final String TOMBSTONE_ON_DELETE_KEY = "tombstones.on.delete";
  static final String TOMBSTONE_ON_DELETE_VALUE = Boolean.FALSE.toString();

  /**
   * Returns the common properties required to configure the Debezium MongoDB connector.
   *
   * @return The common Debezium CDC properties for the Debezium MongoDB connector.
   */
  public static Properties getDebeziumProperties() {
    final Properties props = new Properties();

    props.setProperty(CONNECTOR_CLASS_KEY, CONNECTOR_CLASS_VALUE);
    props.setProperty(SNAPSHOT_MODE_KEY, SNAPSHOT_MODE_VALUE);
    props.setProperty(CAPTURE_MODE_KEY, CAPTURE_MODE_VALUE);
    props.setProperty(HEARTBEAT_INTERVAL_KEY, HEARTBEAT_FREQUENCY_MS);
    props.setProperty(TOMBSTONE_ON_DELETE_KEY, TOMBSTONE_ON_DELETE_VALUE);
    props.setProperty(TASK_MANAGEMENT_TIMEOUT_KEY, TASK_MANAGEMENT_TIMEOUT_MS);

    return props;
  }

}
