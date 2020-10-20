/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.postgres;

import static java.util.stream.Collectors.toList;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.DatabaseHelper;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.AbstractMap;
import java.util.List;
import java.util.Map.Entry;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

class PostgresDestinationTest {

  private static final Instant NOW = Instant.now();
  private static final String USERS_STREAM_NAME = "users";
  private static final String TASKS_STREAM_NAME = "tasks";
  private static final AirbyteMessage MESSAGE_USERS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "john").put("id", "10").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_USERS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "susan").put("id", "30").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_TASKS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(TASKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "announce the game.").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  // also used for testing quote escaping
  private static final AirbyteMessage MESSAGE_TASKS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(TASKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "ship some 'code'.").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_STATE = new AirbyteMessage().withType(AirbyteMessage.Type.STATE)
      .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.builder().put("checkpoint", "now!").build())));

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(Lists.newArrayList(
      CatalogHelpers.createAirbyteStream(USERS_STREAM_NAME, Field.of("name", JsonSchemaPrimitive.STRING),
          Field.of("id", JsonSchemaPrimitive.STRING)),
      CatalogHelpers.createAirbyteStream(TASKS_STREAM_NAME, Field.of("goal", JsonSchemaPrimitive.STRING))));

  private JsonNode config;

  private PostgreSQLContainer<?> db;

  @BeforeEach
  void setup() {
    db = new PostgreSQLContainer<>("postgres:13-alpine");
    db.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("schema", "public")
        .put("port", db.getFirstMappedPort())
        .put("database", db.getDatabaseName())
        .build());
  }

  @AfterEach
  void tearDown() {
    db.stop();
    db.close();
  }

  // todo - same test as csv destination
  @Test
  void testSpec() throws IOException {
    final ConnectorSpecification actual = new PostgresDestination().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  // todo - same test as csv destination
  @Test
  void testCheckSuccess() {
    final AirbyteConnectionStatus actual = new PostgresDestination().check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @Test
  void testCheckFailure() {
    ((ObjectNode) config).put("password", "fake");
    final AirbyteConnectionStatus actual = new PostgresDestination().check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.FAILED)
        .withMessage("Cannot create PoolableConnectionFactory (FATAL: password authentication failed for user \"test\")");
    assertEquals(expected, actual);
  }

  @Test
  void testWriteSuccess() throws Exception {
    final DestinationConsumer<AirbyteMessage> consumer = new PostgresDestination().write(config, CATALOG);

    consumer.accept(MESSAGE_USERS1);
    consumer.accept(MESSAGE_TASKS1);
    consumer.accept(MESSAGE_USERS2);
    consumer.accept(MESSAGE_TASKS2);
    consumer.accept(MESSAGE_STATE);
    consumer.close();

    Set<JsonNode> usersActual = recordRetriever(USERS_STREAM_NAME);
    final Set<JsonNode> expectedUsersJson = Sets.newHashSet(MESSAGE_USERS1.getRecord().getData(), MESSAGE_USERS2.getRecord().getData());
    assertEquals(expectedUsersJson, usersActual);

    Set<JsonNode> tasksActual = recordRetriever(TASKS_STREAM_NAME);
    final Set<JsonNode> expectedTasksJson = Sets.newHashSet(MESSAGE_TASKS1.getRecord().getData(), MESSAGE_TASKS2.getRecord().getData());
    assertEquals(expectedTasksJson, tasksActual);

    assertTmpTablesNotPresent(CATALOG.getStreams().stream().map(AirbyteStream::getName).collect(Collectors.toList()));
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testWriteFailure() throws Exception {
    // hack to force an exception to be thrown from within the consumer.
    final AirbyteMessage spiedMessage = spy(MESSAGE_USERS1);
    doThrow(new RuntimeException()).when(spiedMessage).getRecord();

    final DestinationConsumer<AirbyteMessage> consumer = spy(new PostgresDestination().write(config, CATALOG));

    assertThrows(RuntimeException.class, () -> consumer.accept(spiedMessage));
    consumer.accept(MESSAGE_USERS2);
    consumer.close();

    final List<String> tableNames = CATALOG.getStreams().stream().map(AirbyteStream::getName).collect(toList());
    assertTmpTablesNotPresent(CATALOG.getStreams().stream().map(AirbyteStream::getName).collect(Collectors.toList()));
    // assert that no tables were created.
    assertTrue(fetchNamesOfTablesInDb().stream().noneMatch(tableName -> tableNames.stream().anyMatch(tableName::startsWith)));
  }

  private List<String> fetchNamesOfTablesInDb() throws SQLException {
    return DatabaseHelper.query(getDatabasePool(),
        ctx -> ctx.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"))
        .stream()
        .map(record -> (String) record.get("table_name")).collect(Collectors.toList());
  }

  private void assertTmpTablesNotPresent(List<String> tableNames) throws SQLException {
    Set<String> tmpTableNamePrefixes = tableNames.stream().map(name -> name + "_").collect(Collectors.toSet());
    assertTrue(fetchNamesOfTablesInDb().stream().noneMatch(tableName -> tmpTableNamePrefixes.stream().anyMatch(tableName::startsWith)));
  }

  private BasicDataSource getDatabasePool() {
    return DatabaseHelper.getConnectionPool(db.getUsername(), db.getPassword(), db.getJdbcUrl());
  }

  private Set<JsonNode> recordRetriever(String streamName) throws Exception {

    return DatabaseHelper.query(
        getDatabasePool(),
        ctx -> ctx
            .fetch(String.format("SELECT * FROM %s ORDER BY emitted_at ASC;", streamName))
            .stream()
            .peek(record -> {
              // ensure emitted_at is not in the future
              OffsetDateTime now = OffsetDateTime.now(ZoneOffset.UTC);
              OffsetDateTime emitted_at = record.get("emitted_at", OffsetDateTime.class);

              assertTrue(now.toEpochSecond() >= emitted_at.toEpochSecond());
            })
            .map(Record::intoMap)
            .map(r -> r.entrySet().stream().map(e -> {
              if (e.getValue().getClass().equals(org.jooq.JSONB.class)) {
                // jooq needs more configuration to handle jsonb natively. coerce it to a string for now and handle
                // deserializing later.
                return new AbstractMap.SimpleImmutableEntry<>(e.getKey(), e.getValue().toString());
              }
              return e;
            }).collect(Collectors.toMap(Entry::getKey, Entry::getValue)))
            .map(r -> (String) r.get(PostgresDestination.COLUMN_NAME))
            .map(Jsons::deserialize)
            .collect(Collectors.toSet()));
  }

}
