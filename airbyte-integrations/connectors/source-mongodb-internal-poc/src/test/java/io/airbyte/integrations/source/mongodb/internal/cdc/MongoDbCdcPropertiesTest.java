/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static com.mongodb.internal.connection.tlschannel.util.Util.assertTrue;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.CAPTURE_MODE_KEY;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.CAPTURE_MODE_VALUE;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.CONNECTOR_CLASS_KEY;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.CONNECTOR_CLASS_VALUE;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.FIELD_EXCLUDE_LIST_KEY;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.HEARTBEAT_FREQUENCY_MS;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.HEARTBEAT_INTERVAL_KEY;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.SNAPSHOT_MODE_KEY;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.SNAPSHOT_MODE_VALUE;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.ExcludedField;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;
import java.util.Set;
import org.junit.jupiter.api.Test;

class MongoDbCdcPropertiesTest {

  private final String COLLECTION1 = "collection1";
  private final String COLLECTION2 = "collection2";
  private final String COLLECTION3 = "collection3";

  private final String FIELD1 = "field1";
  private final String FIELD2 = "field2";
  private final String FIELD3 = "field3";

  private final String DATABASE = "database";

  private final String FULLY_QUALIFIED_FIELD1 = DATABASE + "." + COLLECTION1 + "." + FIELD1;
  private final String FULLY_QUALIFIED_FIELD2 = DATABASE + "." + COLLECTION2 + "." + FIELD2;
  private final String FULLY_QUALIFIED_FIELD3 = DATABASE + "." + COLLECTION3 + "." + FIELD3;
  private final String FULLY_QUALIFIED_FIELD4 = DATABASE + "." + COLLECTION3 + "." + FIELD1;

  @Test
  void testDebeziumProperties() {
    final Set<ExcludedField> fieldsToExclude = Set.of(
        new ExcludedField(DATABASE, COLLECTION1, FIELD1),
        new ExcludedField(DATABASE, COLLECTION2, FIELD2),
        new ExcludedField(DATABASE, COLLECTION3, FIELD3),
        new ExcludedField(DATABASE, COLLECTION3, FIELD1));

    final Properties debeziumProperties = MongoDbCdcProperties.getDebeziumProperties(fieldsToExclude);
    assertEquals(5, debeziumProperties.size());
    assertEquals(CONNECTOR_CLASS_VALUE, debeziumProperties.get(CONNECTOR_CLASS_KEY));
    assertEquals(SNAPSHOT_MODE_VALUE, debeziumProperties.get(SNAPSHOT_MODE_KEY));
    assertEquals(CAPTURE_MODE_VALUE, debeziumProperties.get(CAPTURE_MODE_KEY));
    assertEquals(HEARTBEAT_FREQUENCY_MS, debeziumProperties.get(HEARTBEAT_INTERVAL_KEY));
    final String fieldExcludeList = (String) debeziumProperties.get(FIELD_EXCLUDE_LIST_KEY);
    final List<String> actualFullyQualifiedExcludedFields = Arrays.asList(fieldExcludeList.split(","));
    assertEquals(4, actualFullyQualifiedExcludedFields.size());
    assertTrue(actualFullyQualifiedExcludedFields.contains(FULLY_QUALIFIED_FIELD1));
    assertTrue(actualFullyQualifiedExcludedFields.contains(FULLY_QUALIFIED_FIELD2));
    assertTrue(actualFullyQualifiedExcludedFields.contains(FULLY_QUALIFIED_FIELD3));
    assertTrue(actualFullyQualifiedExcludedFields.contains(FULLY_QUALIFIED_FIELD4));
  }

}
