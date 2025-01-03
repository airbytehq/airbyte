/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import javax.sql.DataSource;
import org.apache.commons.lang3.RandomStringUtils;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class SingleStoreDestinationTest {

  private static AirbyteSingleStoreTestContainer db;
  private static final String DATABASE = "database_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();
  private static final String NAMESPACE = "namespace_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();
  private static final String STREAM_NAME = "id_and_name";

  private static final ConfiguredAirbyteCatalog CATALOG =
      new ConfiguredAirbyteCatalog()
          .withStreams(List.of(CatalogHelpers.createConfiguredAirbyteStream(STREAM_NAME, NAMESPACE, Field.of("id", JsonSchemaType.NUMBER),
              Field.of("name", JsonSchemaType.STRING), Field.of("_ab_cdc_deleted_at", JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE))));

  static {
    CATALOG.getStreams().get(0).setCursorField(List.of("id"));
    CATALOG.getStreams().get(0).setPrimaryKey(List.of(List.of("id")));
    CATALOG.getStreams().get(0).setSyncMode(SyncMode.INCREMENTAL);
    CATALOG.getStreams().get(0).setDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP);
  }

  private JsonNode config;

  @BeforeAll
  static void init() throws IOException, InterruptedException {
    AirbyteSingleStoreTestContainer container = new AirbyteSingleStoreTestContainer();
    container.start();
    final String username = "user_" + RandomStringUtils.randomAlphabetic(5).toLowerCase();
    final String password = RandomStringUtils.randomAlphabetic(10).toLowerCase();
    final String[] sql = new String[] {String.format("CREATE DATABASE %s", DATABASE),
      String.format("CREATE USER %s IDENTIFIED BY '%s'", username, password), String.format("GRANT ALL ON *.* TO %s", username)};
    container.execInContainer("/bin/bash", "-c",
        String.format("set -o errexit -o pipefail; echo \"%s\" | singlestore -v -v -v --user=root --password=root", String.join("; ", sql)));
    db = container.withUsername(username).withPassword(password).withDatabaseName(DATABASE);
  }

  @BeforeEach
  void setup() {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.SSL_KEY, false).build());
  }

  @Test
  void testCheck() {
    final SingleStoreDestination destination = new SingleStoreDestination();
    AirbyteConnectionStatus status = destination.check(config);
    assertNotNull(status);
    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, status.getStatus());
  }

  // used for debug
  @Test
  void simpleTest() throws Exception {
    final SingleStoreDestination destination = new SingleStoreDestination();
    final SerializedAirbyteMessageConsumer consumer =
        destination.getSerializedMessageConsumer(config, CATALOG, Destination::defaultOutputRecordCollector);
    final List<AirbyteMessage> expectedRecords = getNRecords(10);

    consumer.start();
    expectedRecords.forEach(m -> {
      try {
        String message = Jsons.serialize(m);
        consumer.accept(message, message.getBytes(StandardCharsets.UTF_8).length);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
    final String stateMessage = Jsons.serialize(new AirbyteMessage().withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(NAMESPACE + "." + STREAM_NAME, 10)))));
    consumer.accept(stateMessage, stateMessage.getBytes(StandardCharsets.UTF_8).length);
    consumer.close();
    final JdbcDatabase database = getJdbcDatabaseFromConfig(getDataSourceFromConfig(config));

    final List<JsonNode> actualRecords =
        database.bufferedResultSetQuery(
            connection -> connection.createStatement()
                .executeQuery(String.format("SELECT * " + "FROM %s.%s_raw__stream_id_and_name order by _airbyte_loaded_at;", DATABASE, NAMESPACE)),
            JdbcUtils.getDefaultSourceOperations()::rowToJson);

    Assertions.assertThat(actualRecords.stream().map(o -> o.get("_airbyte_data").asText()).map(Jsons::deserialize).collect(Collectors.toList()))
        .hasSameElementsAs(expectedRecords.stream().map(AirbyteMessage::getRecord).map(AirbyteRecordMessage::getData).collect(Collectors.toList()));
  }

  private List<AirbyteMessage> getNRecords(final int n) {
    return IntStream.range(0, n).boxed()
        .map(i -> new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME).withNamespace(NAMESPACE).withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(
                    i % 2 == 0 ? ImmutableMap.of("id", i, "name", true)
                        : ImmutableMap.of("id", i, "name", "test_" + i, "_ab_cdc_deleted_at", "2023-01-01T00:01:00")))))
        .collect(Collectors.toList());
  }

  private JdbcDatabase getJdbcDatabaseFromConfig(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource, JdbcUtils.getDefaultSourceOperations());
  }

  private DataSource getDataSourceFromConfig(final JsonNode config) {
    return DataSourceFactory.create(config.get(JdbcUtils.USERNAME_KEY).asText(), config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.SINGLESTORE.getDriverClassName(), String.format(DatabaseDriver.SINGLESTORE.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(), config.get(JdbcUtils.PORT_KEY).asInt(), config.get(JdbcUtils.DATABASE_KEY).asText()));
  }

}
