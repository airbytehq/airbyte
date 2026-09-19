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
  static final String MAX_BATCH_SIZE_KEY = "max.batch.size";

  /**
   * Debezium's own {@code CommonConnectorConfig.DEFAULT_MAX_BATCH_SIZE}, and the value the Java CDK
   * sets today. The derived batch size is clamped to this so that connections using the default queue
   * size behave exactly as they did before, and so that {@code max.batch.size} can never exceed
   * Debezium's {@code max.queue.size} (8192) -- Debezium validates
   * {@code max.queue.size > max.batch.size} at startup and refuses to start otherwise.
   */
  static final int MAX_BATCH_SIZE_CEILING = 2048;

  /**
   * Returns the common properties required to configure the Debezium MongoDB connector.
   * <p>
   * The configured queue size also drives Debezium's {@code max.batch.size}, which bounds two
   * structures that are otherwise limited by event count only and not by bytes:
   * <ul>
   * <li>the MongoDB connector's change-stream prefetch buffer -- {@code BufferingChangeStreamCursor}
   * builds its {@code EventFetcher} with {@code config.getMaxBatchSize()} as the capacity, and each
   * entry holds the raw BSON full document <em>and</em> pre-image, which is several times heavier
   * than the corresponding JSON text;</li>
   * <li>Debezium's in-flight batch, the {@code List<SourceRecord>} the embedded engine holds for the
   * duration of a {@code handleBatch} call.</li>
   * </ul>
   * Debezium's {@code max.queue.size.in.bytes} applies to neither, so the event count is the only
   * available bound. Keeping this tied to the queue size means one user-facing number bounds the
   * whole pipeline, rather than three unrelated ones.
   *
   * @param queueSize The configured size of the Airbyte CDC event queue, already clamped by
   *        {@link io.airbyte.integrations.source.mongodb.MongoUtil#getDebeziumEventQueueSize}.
   * @return The common Debezium CDC properties for the Debezium MongoDB connector.
   */
  public static Properties getDebeziumProperties(final int queueSize) {
    final Properties props = new Properties();

    props.setProperty(CONNECTOR_CLASS_KEY, CONNECTOR_CLASS_VALUE);
    props.setProperty(SNAPSHOT_MODE_KEY, SNAPSHOT_MODE_VALUE);
    props.setProperty(CAPTURE_MODE_KEY, CAPTURE_MODE_VALUE);
    props.setProperty(HEARTBEAT_INTERVAL_KEY, HEARTBEAT_FREQUENCY_MS);
    props.setProperty(TOMBSTONE_ON_DELETE_KEY, TOMBSTONE_ON_DELETE_VALUE);
    props.setProperty(MAX_BATCH_SIZE_KEY, String.valueOf(Math.min(queueSize, MAX_BATCH_SIZE_CEILING)));

    return props;
  }

}
