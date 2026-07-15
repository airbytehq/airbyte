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
  static final String SNAPSHOT_MODE_VALUE = "never";
  static final String TOMBSTONE_ON_DELETE_KEY = "tombstones.on.delete";
  static final String TOMBSTONE_ON_DELETE_VALUE = Boolean.FALSE.toString();

  /**
   * Returns the common properties required to configure the Debezium MongoDB connector.
   *
   * @return The common Debezium CDC properties for the Debezium MongoDB connector.
   */
  public static Properties getDebeziumProperties() {
    return getDebeziumProperties(null);
  }

  /**
   * Returns the common MongoDB Debezium properties with bounded in-memory buffers when a CDC queue
   * size is configured.
   *
   * @param queueSize maximum records buffered by Debezium and Airbyte, or {@code null} for defaults.
   */
  public static Properties getDebeziumProperties(final Integer queueSize) {
    final Properties props = new Properties();

    props.setProperty(CONNECTOR_CLASS_KEY, CONNECTOR_CLASS_VALUE);
    props.setProperty(SNAPSHOT_MODE_KEY, SNAPSHOT_MODE_VALUE);
    props.setProperty(CAPTURE_MODE_KEY, CAPTURE_MODE_VALUE);
    props.setProperty(HEARTBEAT_INTERVAL_KEY, HEARTBEAT_FREQUENCY_MS);
    props.setProperty(TOMBSTONE_ON_DELETE_KEY, TOMBSTONE_ON_DELETE_VALUE);
    if (queueSize != null) {
      // Debezium requires max.batch.size to be no larger than max.queue.size. Keeping both
      // bounded by the Airbyte output queue prevents a burst of large MongoDB documents from
      // retaining multiple unbounded copies in the connector heap.
      props.setProperty("max.queue.size", Integer.toString(queueSize));
      props.setProperty("max.batch.size", Integer.toString(queueSize));
    }

    return props;
  }

}
