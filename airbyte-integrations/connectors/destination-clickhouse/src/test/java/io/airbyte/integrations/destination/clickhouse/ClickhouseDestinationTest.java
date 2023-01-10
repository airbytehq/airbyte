/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.time.Instant;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.ClickHouseContainer;

public class ClickhouseDestinationTest {

  private static final String DB_NAME = "default";
  private static final String STREAM_NAME = "id_and_name";
  private static final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  private static ClickHouseContainer db;
  private static ConfiguredAirbyteCatalog catalog;
  private static JsonNode config;

  private static final Map<String, String> CONFIG_WITH_SSL = ImmutableMap.of(
      JdbcUtils.HOST_KEY, "localhost",
      JdbcUtils.PORT_KEY, "1337",
      JdbcUtils.USERNAME_KEY, "user",
      JdbcUtils.DATABASE_KEY, "db");

  private static final Map<String, String> CONFIG_NO_SSL = MoreMaps.merge(
      CONFIG_WITH_SSL,
      ImmutableMap.of(
          "socket_timeout", "3000000",
          JdbcUtils.SSL_KEY, "false"));

  @BeforeAll
  static void init() {
    db = new ClickHouseContainer("clickhouse/clickhouse-server:22.5");
    db.start();
  }

  @BeforeEach
  void setup() {
    catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createConfiguredAirbyteStream(
            STREAM_NAME,
            DB_NAME,
            Field.of("id", JsonSchemaType.NUMBER),
            Field.of("name", JsonSchemaType.STRING))));

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, DB_NAME)
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.SCHEMA_KEY, DB_NAME)
        .put(JdbcUtils.SSL_KEY, false)
        .build());
  }

  @AfterAll
  static void cleanUp() {
    db.stop();
    db.close();
  }

  @Test
  void sanityTest() throws Exception {
    final Destination dest = new ClickhouseDestination();
    final AirbyteMessageConsumer consumer = dest.getConsumer(config, catalog,
        Destination::defaultOutputRecordCollector);
    final List<AirbyteMessage> expectedRecords = generateRecords(10);

    consumer.start();
    expectedRecords.forEach(m -> {
      try {
        consumer.accept(m);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
    consumer.accept(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(ImmutableMap.of(DB_NAME + "." + STREAM_NAME, 10)))));
    consumer.close();

    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(JdbcUtils.PASSWORD_KEY).asText(),
            ClickhouseDestination.DRIVER_CLASS,
            String.format(DatabaseDriver.CLICKHOUSE.getUrlFormatString(),
                ClickhouseDestination.HTTP_PROTOCOL,
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get(JdbcUtils.DATABASE_KEY).asText())));

    final List<JsonNode> actualRecords = database.bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery(
            String.format("SELECT * FROM %s.%s;", DB_NAME,
                namingResolver.getRawTableName(STREAM_NAME))),
        JdbcUtils.getDefaultSourceOperations()::rowToJson);

    assertEquals(
        expectedRecords.stream().map(AirbyteMessage::getRecord)
            .map(AirbyteRecordMessage::getData).collect(Collectors.toList()),
        actualRecords.stream()
            .map(o -> o.get("_airbyte_data").asText())
            .map(Jsons::deserialize)
            .sorted(Comparator.comparingInt(x -> x.get("id").asInt()))
            .collect(Collectors.toList()));
  }

  private List<AirbyteMessage> generateRecords(final int n) {
    return IntStream.range(0, n)
        .boxed()
        .map(i -> new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(STREAM_NAME)
                .withNamespace(DB_NAME)
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "test name " + i)))))
        .collect(Collectors.toList());
  }

}
