/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.components.ComponentRunner;
import io.airbyte.cdk.components.debezium.DebeziumConsumer;
import io.airbyte.cdk.components.debezium.DebeziumProducer;
import io.airbyte.cdk.components.debezium.DebeziumRecord;
import io.airbyte.cdk.components.debezium.DebeziumState;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.PostgresUtils;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.time.Duration;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class PostgresDebeziumComponentUtils {

  static public final String COMPONENT_NAME = "debezium";
  static public final long MAX_RECORDS = 10_000L;
  static public final long MAX_RECORD_BYTES = 1_000_000_000L;
  static public final DebeziumConsumer.Builder CONSUMER_BUILDER = new DebeziumConsumer.Builder(MAX_RECORDS, MAX_RECORD_BYTES);
  static public final Duration HEARTBEAT_INTERVAL = Duration.ofSeconds(10L);
  // Test execution latency is lower when heartbeats are more frequent.
  static public final Duration HEARTBEAT_INTERVAL_IN_TESTS = Duration.ofMillis(100L);

  static public ComponentRunner<DebeziumRecord, DebeziumState> runner(JdbcDatabase database, DebeziumState upperBound) {

    final JsonNode sourceConfig = database.getSourceConfig();

    final DebeziumProducer.Builder producerBuilder = new DebeziumProducer.Builder()
        .withBoundChecker(new PostgresLsnMapper(), upperBound)
        .with(PostgresCdcProperties.getDebeziumDefaultProperties(database))
        .withDatabaseHost(sourceConfig.get(JdbcUtils.HOST_KEY).asText())
        .withDatabasePort(sourceConfig.get(JdbcUtils.PORT_KEY).asInt())
        .withDatabaseUser(sourceConfig.get(JdbcUtils.USERNAME_KEY).asText())
        .withDatabaseName(sourceConfig.get(JdbcUtils.DATABASE_KEY).asText());

    if (sourceConfig.has(JdbcUtils.PASSWORD_KEY)) {
      producerBuilder.withDatabasePassword(sourceConfig.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    final Duration maxTime = PostgresUtils.getFirstRecordWaitTime(database.getSourceConfig());

    return new ComponentRunner<>(COMPONENT_NAME, producerBuilder, CONSUMER_BUILDER, maxTime, new PostgresLsnMapper().comparator());
  }

  static public AirbyteRecordMessage toAirbyteRecordMessage(DebeziumRecord debeziumRecord) {
    final ObjectNode data;
    final Instant transactionTimestamp = Instant.ofEpochMilli(debeziumRecord.source().get("ts_ms").asLong());
    if (debeziumRecord.after().isNull()) {
      data = (ObjectNode) Jsons.clone(debeziumRecord.before());
      data.put(DebeziumEventConverter.CDC_DELETED_AT, transactionTimestamp.toString());
    } else {
      data = (ObjectNode) Jsons.clone(debeziumRecord.after());
      data.put(DebeziumEventConverter.CDC_DELETED_AT, (String) null);
    }
    data.put(DebeziumEventConverter.CDC_UPDATED_AT, transactionTimestamp.toString());
    data.put(DebeziumEventConverter.CDC_LSN, debeziumRecord.source().get("lsn").asLong());

    return new AirbyteRecordMessage()
        .withStream(debeziumRecord.source().get("table").asText())
        .withNamespace(debeziumRecord.source().get("schema").asText())
        .withData(data);
  }

  static public DebeziumState makeSyntheticDebeziumState(JdbcDatabase database, String dbName) {
    JsonNode jsonState = new PostgresDebeziumStateUtil().constructInitialDebeziumState(database, dbName);
    Map<JsonNode, JsonNode> map = new HashMap<>();
    jsonState.fields().forEachRemaining(e -> map.put(Jsons.deserialize(e.getKey()), Jsons.deserialize(e.getValue().asText())));
    return new DebeziumState(new DebeziumState.Offset(map), Optional.empty());
  }

}
