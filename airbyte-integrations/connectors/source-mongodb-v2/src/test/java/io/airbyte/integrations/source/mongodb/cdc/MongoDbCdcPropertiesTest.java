/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.CAPTURE_MODE_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.CAPTURE_MODE_VALUE;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.CONNECTOR_CLASS_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.CONNECTOR_CLASS_VALUE;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.HEARTBEAT_FREQUENCY_MS;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.HEARTBEAT_INTERVAL_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.MAX_BATCH_SIZE_CEILING;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.MAX_BATCH_SIZE_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.SNAPSHOT_MODE_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.SNAPSHOT_MODE_VALUE;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.TOMBSTONE_ON_DELETE_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.TOMBSTONE_ON_DELETE_VALUE;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Properties;
import org.junit.jupiter.api.Test;

class MongoDbCdcPropertiesTest {

  /**
   * Mirrors {@code MongoUtil.MAX_QUEUE_SIZE} / {@code MIN_QUEUE_SIZE}, which are package-private. The
   * clamping behaviour itself is covered by {@code MongoUtilTest}; these are here only to express the
   * queue sizes a user can actually end up with.
   */
  private static final int DEFAULT_QUEUE_SIZE = 10_000;
  private static final int SMALLEST_QUEUE_SIZE = 10;

  @Test
  void testDebeziumProperties() {
    final Properties debeziumProperties = MongoDbCdcProperties.getDebeziumProperties(DEFAULT_QUEUE_SIZE);
    assertEquals(6, debeziumProperties.size());
    assertEquals(CONNECTOR_CLASS_VALUE, debeziumProperties.get(CONNECTOR_CLASS_KEY));
    assertEquals(SNAPSHOT_MODE_VALUE, debeziumProperties.get(SNAPSHOT_MODE_KEY));
    assertEquals(CAPTURE_MODE_VALUE, debeziumProperties.get(CAPTURE_MODE_KEY));
    assertEquals(HEARTBEAT_FREQUENCY_MS, debeziumProperties.get(HEARTBEAT_INTERVAL_KEY));
    assertEquals(TOMBSTONE_ON_DELETE_VALUE, debeziumProperties.get(TOMBSTONE_ON_DELETE_KEY));
  }

  /**
   * The default queue size must keep producing the batch size the connector used before this knob was
   * coupled to queue_size, so that existing connections are unaffected.
   */
  @Test
  void testMaxBatchSizeIsUnchangedAtDefaultQueueSize() {
    assertEquals("2048",
        MongoDbCdcProperties.getDebeziumProperties(DEFAULT_QUEUE_SIZE).get(MAX_BATCH_SIZE_KEY));
  }

  /**
   * A deliberately low queue size must propagate to max.batch.size, since that is what bounds the
   * MongoDB change-stream prefetch buffer and Debezium's in-flight batch.
   */
  @Test
  void testMaxBatchSizeTracksLowQueueSize() {
    assertEquals("10", MongoDbCdcProperties.getDebeziumProperties(10).get(MAX_BATCH_SIZE_KEY));
    assertEquals("100", MongoDbCdcProperties.getDebeziumProperties(100).get(MAX_BATCH_SIZE_KEY));
    assertEquals(String.valueOf(SMALLEST_QUEUE_SIZE),
        MongoDbCdcProperties.getDebeziumProperties(SMALLEST_QUEUE_SIZE).get(MAX_BATCH_SIZE_KEY));
  }

  /**
   * Debezium validates {@code max.queue.size > max.batch.size} in
   * {@code CommonConnectorConfig.validateMaxQueueSize} and refuses to start the connector otherwise.
   * The CDK sets {@code max.queue.size=8192}, so the derived batch size must stay strictly below it
   * for every queue size a user can configure - including the maximum.
   */
  @Test
  void testDerivedBatchSizeNeverExceedsDebeziumMaxQueueSize() {
    final int debeziumMaxQueueSize = 8192;
    assertTrue(MAX_BATCH_SIZE_CEILING < debeziumMaxQueueSize,
        "max.batch.size ceiling must stay below Debezium's max.queue.size");
    for (final int queueSize : new int[] {SMALLEST_QUEUE_SIZE, 100, 2048, 2049, DEFAULT_QUEUE_SIZE}) {
      final int batchSize =
          Integer.parseInt((String) MongoDbCdcProperties.getDebeziumProperties(queueSize).get(MAX_BATCH_SIZE_KEY));
      assertTrue(batchSize < debeziumMaxQueueSize,
          "queue_size=" + queueSize + " derived max.batch.size=" + batchSize
              + ", which would fail Debezium config validation");
    }
  }

}
