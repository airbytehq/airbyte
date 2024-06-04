/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.ChangeEvent.SOURCE_RESUME_TOKEN;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.ChangeEvent.SOURCE_SECONDS;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.OffsetState.KEY_REPLICA_SET;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.OffsetState.VALUE_TRANSACTION_ID;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.Mockito.mock;

import com.mongodb.ConnectionString;
import io.debezium.connector.mongodb.MongoDbConnectorConfig;
import io.debezium.connector.mongodb.MongoDbOffsetContext;
import io.debezium.connector.mongodb.ReplicaSets;
import io.debezium.connector.mongodb.ResumeTokens;
import io.debezium.connector.mongodb.connection.ReplicaSet;
import java.util.HashMap;
import java.util.Map;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.junit.jupiter.api.Test;

class MongoDbCustomLoaderTest {

  private static final String RESUME_TOKEN = "8264BEB9F3000000012B0229296E04";

  @Test
  void testLoadOffsets() {
    final String replicaSet = "replica-set";
    final BsonDocument resumeToken = ResumeTokens.fromData(RESUME_TOKEN);
    final BsonTimestamp timestamp = ResumeTokens.getTimestamp(resumeToken);
    final Map<String, String> key = Map.of(KEY_REPLICA_SET, replicaSet);
    final Map<String, Object> value = new HashMap<>();
    value.put(SOURCE_SECONDS, timestamp.getTime());
    value.put(SOURCE_ORDER, timestamp.getInc());
    value.put(SOURCE_RESUME_TOKEN, RESUME_TOKEN);
    value.put(VALUE_TRANSACTION_ID, null);
    final Map<Map<String, String>, Map<String, Object>> offsets = Map.of(key, value);
    final MongoDbConnectorConfig mongoDbConnectorConfig = mock(MongoDbConnectorConfig.class);
    final ReplicaSets replicaSets = ReplicaSets.of(
        new ReplicaSet(new ConnectionString("mongodb://localhost:1234/?replicaSet=" + replicaSet)));
    final MongoDbCustomLoader loader = new MongoDbCustomLoader(mongoDbConnectorConfig, replicaSets);

    final MongoDbOffsetContext context = loader.loadOffsets(offsets);
    final Map<String, ?> offset = context.getReplicaSetOffsetContext(replicaSets.all().get(0)).getOffset();

    assertNotNull(offset);
    assertEquals(value, offset);
  }

}
