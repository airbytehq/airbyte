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
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream.DestinationSyncMode;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.jooq.JSONFormat;
import org.jooq.JSONFormat.RecordFormat;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

class PostgresDestinationTest {

  private static final JSONFormat JSON_FORMAT = new JSONFormat().recordFormat(RecordFormat.OBJECT);
  private static final Instant NOW = Instant.now();
  private static final String USERS_STREAM_NAME = "users";
  private static final String TASKS_STREAM_NAME = "tasks-list";
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

  private static final ConfiguredAirbyteCatalog CATALOG = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
      CatalogHelpers.createConfiguredAirbyteStream(USERS_STREAM_NAME, Field.of("name", JsonSchemaPrimitive.STRING),
          Field.of("id", JsonSchemaPrimitive.STRING)),
      CatalogHelpers.createConfiguredAirbyteStream(TASKS_STREAM_NAME, Field.of("goal", JsonSchemaPrimitive.STRING))));

  private static final NamingConventionTransformer NAMING_TRANSFORMER = new PostgresSQLNameTransformer();

  private PostgreSQLContainer<?> container;
  private JsonNode config;
  private Database database;

  @BeforeEach
  void setup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("schema", "public")
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .build());

    database = Databases.createPostgresDatabase(container.getUsername(), container.getPassword(), container.getJdbcUrl());
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
    container.close();
  }

  @Test
  void testSpec() throws IOException {
    final ConnectorSpecification actual = new PostgresDestination().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

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
    assertEquals(Status.FAILED, actual.getStatus());
    assertTrue(actual.getMessage().startsWith("Could not connect with provided configuration."));
  }

  @Test
  void testWriteSuccess() throws Exception {
    final PostgresDestination destination = new PostgresDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, CATALOG);

    consumer.start();
    consumer.accept(MESSAGE_USERS1);
    consumer.accept(MESSAGE_TASKS1);
    consumer.accept(MESSAGE_USERS2);
    consumer.accept(MESSAGE_TASKS2);
    consumer.accept(MESSAGE_STATE);
    consumer.close();

    Set<JsonNode> usersActual = recordRetriever(NAMING_TRANSFORMER.getRawTableName(USERS_STREAM_NAME));
    final Set<JsonNode> expectedUsersJson = Sets.newHashSet(MESSAGE_USERS1.getRecord().getData(), MESSAGE_USERS2.getRecord().getData());
    assertEquals(expectedUsersJson, usersActual);

    Set<JsonNode> tasksActual = recordRetriever(NAMING_TRANSFORMER.getRawTableName(TASKS_STREAM_NAME));
    final Set<JsonNode> expectedTasksJson = Sets.newHashSet(MESSAGE_TASKS1.getRecord().getData(), MESSAGE_TASKS2.getRecord().getData());
    assertEquals(expectedTasksJson, tasksActual);

    assertTmpTablesNotPresent(CATALOG.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .collect(Collectors.toList()));
  }

  @Test
  void testWriteIncremental() throws Exception {
    final ConfiguredAirbyteCatalog catalog = Jsons.clone(CATALOG);
    catalog.getStreams().forEach(stream -> {
      stream.withSyncMode(SyncMode.INCREMENTAL);
      stream.withDestinationSyncMode(DestinationSyncMode.APPEND);
    });

    final PostgresDestination destination = new PostgresDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog);

    consumer.start();
    consumer.accept(MESSAGE_USERS1);
    consumer.accept(MESSAGE_TASKS1);
    consumer.accept(MESSAGE_USERS2);
    consumer.accept(MESSAGE_TASKS2);
    consumer.accept(MESSAGE_STATE);
    consumer.close();

    final AirbyteMessageConsumer consumer2 = destination.getConsumer(config, catalog);

    final AirbyteMessage messageUser3 = new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
            .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "michael").put("id", "87").build()))
            .withEmittedAt(NOW.toEpochMilli()));
    consumer2.start();
    consumer2.accept(messageUser3);
    consumer2.close();

    Set<JsonNode> usersActual = recordRetriever(NAMING_TRANSFORMER.getRawTableName(USERS_STREAM_NAME));
    final Set<JsonNode> expectedUsersJson = Sets.newHashSet(
        MESSAGE_USERS1.getRecord().getData(),
        MESSAGE_USERS2.getRecord().getData(),
        messageUser3.getRecord().getData());
    assertEquals(expectedUsersJson, usersActual);

    Set<JsonNode> tasksActual = recordRetriever(NAMING_TRANSFORMER.getRawTableName(TASKS_STREAM_NAME));
    final Set<JsonNode> expectedTasksJson = Sets.newHashSet(MESSAGE_TASKS1.getRecord().getData(), MESSAGE_TASKS2.getRecord().getData());
    assertEquals(expectedTasksJson, tasksActual);

    assertTmpTablesNotPresent(CATALOG.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .collect(Collectors.toList()));
  }

  @Test
  void testWriteNewSchema() throws Exception {
    JsonNode newConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("schema", "new_schema")
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .build());
    final PostgresDestination destination = new PostgresDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(newConfig, CATALOG);

    consumer.start();
    consumer.accept(MESSAGE_USERS1);
    consumer.accept(MESSAGE_TASKS1);
    consumer.accept(MESSAGE_USERS2);
    consumer.accept(MESSAGE_TASKS2);
    consumer.accept(MESSAGE_STATE);
    consumer.close();

    final String schemaName = NAMING_TRANSFORMER.getIdentifier("new_schema");
    String streamName = schemaName + "." + NAMING_TRANSFORMER.getRawTableName(USERS_STREAM_NAME);
    Set<JsonNode> usersActual = recordRetriever(streamName);
    final Set<JsonNode> expectedUsersJson = Sets.newHashSet(MESSAGE_USERS1.getRecord().getData(), MESSAGE_USERS2.getRecord().getData());
    assertEquals(expectedUsersJson, usersActual);

    streamName = schemaName + "." + NAMING_TRANSFORMER.getRawTableName(TASKS_STREAM_NAME);
    Set<JsonNode> tasksActual = recordRetriever(streamName);
    final Set<JsonNode> expectedTasksJson = Sets.newHashSet(MESSAGE_TASKS1.getRecord().getData(), MESSAGE_TASKS2.getRecord().getData());
    assertEquals(expectedTasksJson, tasksActual);

    assertTmpTablesNotPresent(CATALOG.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .collect(Collectors.toList()));

    assertThrows(RuntimeException.class, () -> recordRetriever(NAMING_TRANSFORMER.getRawTableName(USERS_STREAM_NAME)));
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testWriteFailure() throws Exception {
    // hack to force an exception to be thrown from within the consumer.
    final AirbyteMessage spiedMessage = spy(MESSAGE_USERS1);
    doThrow(new RuntimeException()).when(spiedMessage).getRecord();

    final PostgresDestination destination = new PostgresDestination();
    final AirbyteMessageConsumer consumer = spy(destination.getConsumer(config, CATALOG));

    consumer.start();
    assertThrows(RuntimeException.class, () -> consumer.accept(spiedMessage));
    consumer.accept(MESSAGE_USERS2);
    consumer.close();

    final List<String> tableNames = CATALOG.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(s -> NAMING_TRANSFORMER.getRawTableName(s.getName()))
        .collect(Collectors.toList());
    assertTmpTablesNotPresent(CATALOG.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .collect(Collectors.toList()));
    // assert that no tables were created.
    assertTrue(fetchNamesOfTablesInDb().stream().noneMatch(tableName -> tableNames.stream().anyMatch(tableName::startsWith)));
  }

  private List<String> fetchNamesOfTablesInDb() throws SQLException {
    return database.query(
        ctx -> ctx.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"))
        .stream()
        .map(record -> (String) record.get("table_name")).collect(Collectors.toList());
  }

  private void assertTmpTablesNotPresent(List<String> tableNames) throws SQLException {
    Set<String> tmpTableNamePrefixes = tableNames.stream().map(name -> name + "_\\d+").collect(Collectors.toSet());
    assertTrue(fetchNamesOfTablesInDb().stream().noneMatch(tableName -> tmpTableNamePrefixes.stream().anyMatch(tableName::matches)));
  }

  private Set<JsonNode> recordRetriever(String streamName) throws Exception {
    return database.query(ctx -> ctx
        .fetch(String.format("SELECT * FROM %s ORDER BY %s ASC;", streamName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
        .stream()
        .peek(record -> {
          // ensure emitted_at is not in the future
          OffsetDateTime now = OffsetDateTime.now(ZoneOffset.UTC);
          OffsetDateTime emitted_at = record.get(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, OffsetDateTime.class);

          assertTrue(now.toEpochSecond() >= emitted_at.toEpochSecond());
        })
        .map(r -> r.formatJSON(JSON_FORMAT))
        .map(Jsons::deserialize)
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toSet()));
  }

}
