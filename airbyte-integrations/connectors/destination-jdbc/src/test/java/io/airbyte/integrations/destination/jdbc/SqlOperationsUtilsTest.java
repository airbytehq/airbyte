/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.sql.SQLException;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

class SqlOperationsUtilsTest {

  private static final Instant NOW = Instant.ofEpochSecond(900);
  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "rivers";

  private PostgreSQLContainer<?> container;
  private JdbcDatabase database;
  private Supplier<UUID> uuidSupplier;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine");
    container.start();

    final JsonNode config = createConfig();

    database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get("username").asText(),
            config.get("password").asText(),
            DatabaseDriver.POSTGRESQL.getDriverClassName(),
            config.get("jdbc_url").asText()
        )
    );

    uuidSupplier = mock(Supplier.class);
  }

  @Test
  void testInsertRawRecordsInSingleQuery() throws SQLException {
    final UUID RECORD1_UUID = UUID.randomUUID();
    final UUID RECORD2_UUID = UUID.randomUUID();
    when(uuidSupplier.get()).thenReturn(RECORD1_UUID).thenReturn(RECORD2_UUID);

    new TestJdbcSqlOperations().createTableIfNotExists(database, SCHEMA_NAME, STREAM_NAME);

    final String insertQueryComponent = String.format(
        "INSERT INTO %s.%s (%s, %s, %s) VALUES\n",
        SCHEMA_NAME,
        STREAM_NAME,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    final String recordQueryComponent = "(?, ?::jsonb, ?),\n";

    final List<AirbyteRecordMessage> records = Lists.newArrayList(
        new AirbyteRecordMessage()
            .withStream("rivers")
            .withEmittedAt(NOW.toEpochMilli())
            .withData(Jsons.jsonNode(ImmutableMap.of("name", "rio grande", "width", 10))),
        new AirbyteRecordMessage()
            .withStream("rivers")
            .withEmittedAt(NOW.toEpochMilli())
            .withData(Jsons.jsonNode(ImmutableMap.of("name", "mississippi", "width", 20))));

    SqlOperationsUtils.insertRawRecordsInSingleQuery(insertQueryComponent, recordQueryComponent, database, records, uuidSupplier, true);

    final List<JsonNode> actualRecords = database.bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT * FROM RIVERS"),
        JdbcUtils.getDefaultSourceOperations()::rowToJson);

    final List<JsonNode> expectedRecords = Lists.newArrayList(
        Jsons.jsonNode(ImmutableMap.builder()
            .put(JavaBaseConstants.COLUMN_NAME_AB_ID, RECORD1_UUID)
            .put(JavaBaseConstants.COLUMN_NAME_DATA, records.get(0).getData())
            .put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, DataTypeUtils
                .toISO8601StringWithMicroseconds(Instant.ofEpochMilli(records.get(0).getEmittedAt())))
            .build()),
        Jsons.jsonNode(ImmutableMap.builder()
            .put(JavaBaseConstants.COLUMN_NAME_AB_ID, RECORD2_UUID)
            .put(JavaBaseConstants.COLUMN_NAME_DATA, records.get(1).getData())
            .put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, DataTypeUtils
                .toISO8601StringWithMicroseconds(Instant.ofEpochMilli(records.get(1).getEmittedAt())))
            .build()));

    actualRecords.forEach(
        r -> ((ObjectNode) r).put(JavaBaseConstants.COLUMN_NAME_DATA, Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText())));

    assertEquals(expectedRecords, actualRecords);
  }

  private JsonNode createConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("schema", SCHEMA_NAME)
        .put("jdbc_url", String.format("jdbc:postgresql://%s:%s/%s",
            container.getHost(),
            container.getFirstMappedPort(),
            container.getDatabaseName()))
        .build());
  }

}
