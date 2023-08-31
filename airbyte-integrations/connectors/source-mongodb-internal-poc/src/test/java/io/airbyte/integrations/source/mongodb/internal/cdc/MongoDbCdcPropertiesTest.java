/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.CAPTURE_MODE_KEY;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.CAPTURE_MODE_VALUE;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.CONNECTOR_CLASS_KEY;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.CONNECTOR_CLASS_VALUE;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.HEARTBEAT_FREQUENCY_MS;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.HEARTBEAT_INTERVAL_KEY;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.SNAPSHOT_MODE_KEY;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.SNAPSHOT_MODE_VALUE;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Properties;
import org.junit.jupiter.api.Test;

class MongoDbCdcPropertiesTest {

  @Test
  void testDebeziumProperties() {
    final Properties debeziumProperties = MongoDbCdcProperties.getDebeziumProperties();
    assertEquals(4, debeziumProperties.size());
    assertEquals(CONNECTOR_CLASS_VALUE, debeziumProperties.get(CONNECTOR_CLASS_KEY));
    assertEquals(SNAPSHOT_MODE_VALUE, debeziumProperties.get(SNAPSHOT_MODE_KEY));
    assertEquals(CAPTURE_MODE_VALUE, debeziumProperties.get(CAPTURE_MODE_KEY));
    assertEquals(HEARTBEAT_FREQUENCY_MS, debeziumProperties.get(HEARTBEAT_INTERVAL_KEY));
  }

}
