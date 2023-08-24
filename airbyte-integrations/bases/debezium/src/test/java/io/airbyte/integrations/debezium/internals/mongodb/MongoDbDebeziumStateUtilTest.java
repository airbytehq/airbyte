/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mongodb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import io.airbyte.integrations.debezium.internals.mysql.MySqlDebeziumStateUtil;
import io.debezium.connector.mongodb.ResumeTokens;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Optional;

class MongoDbDebeziumStateUtilTest {

  private MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil;

  @BeforeEach
  void setup() {
    mongoDbDebeziumStateUtil = new MongoDbDebeziumStateUtil();
  }

  @Test
  void testConstructInitialDebeziumState() {
    final String database = "test";
    final String replicaSet = "test_rs";
    final String resumeToken = "8264BEB9F3000000012B0229296E04";
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(resumeToken);
    final ChangeStreamIterable changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(BsonDocument.class)).thenReturn(changeStreamIterable);

    final JsonNode initialState = mongoDbDebeziumStateUtil.constructInitialDebeziumState(mongoClient,
        database, replicaSet);

    assertNotNull(initialState);
    assertEquals(1, initialState.size());
    final BsonTimestamp timestamp = ResumeTokens.getTimestamp(resumeTokenDocument);
    final JsonNode offsetState = initialState.fields().next().getValue();
    assertEquals(resumeToken, offsetState.get(MongoDbDebeziumConstants.OffsetState.VALUE_RESUME_TOKEN).asText());
    assertEquals(timestamp.getTime(), offsetState.get(MongoDbDebeziumConstants.OffsetState.VALUE_SECONDS).asInt());
    assertEquals(timestamp.getInc(), offsetState.get(MongoDbDebeziumConstants.OffsetState.VALUE_INCREMENT).asInt());
    assertEquals("null", offsetState.get(MongoDbDebeziumConstants.OffsetState.VALUE_TRANSACTION_ID).asText());

    final Optional<MySqlDebeziumStateUtil.MysqlDebeziumStateAttributes> parsedOffset =
            mongoDbDebeziumStateUtil.savedOffset(
                    MYSQL_PROPERTIES,
                    CONFIGURED_CATALOG,
                    debeziumState.get("mysql_cdc_offset"),
                    config);
    Assertions.assertTrue(parsedOffset.isPresent());
    Assertions.assertNotNull(parsedOffset.get().binlogFilename());
    Assertions.assertTrue(parsedOffset.get().binlogPosition() > 0);
    Assertions.assertTrue(parsedOffset.get().gtidSet().isEmpty());
  }

}
