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
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ConnectorSpecification;
import io.airbyte.config.DataType;
import io.airbyte.config.Field;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.Stream;
import io.airbyte.db.DatabaseHelper;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.singer.SingerMessage;
import io.airbyte.singer.SingerMessage.Type;
import java.io.IOException;
import java.sql.SQLException;
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

  private static final ObjectMapper objectMapper = new ObjectMapper();

  private static final String USERS_STREAM_NAME = "users";
  private static final String TASKS_STREAM_NAME = "tasks";
  private static final SingerMessage SINGER_MESSAGE_USERS1 = new SingerMessage().withType(Type.RECORD).withStream(USERS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("name", "john").put("id", "10"));
  private static final SingerMessage SINGER_MESSAGE_USERS2 = new SingerMessage().withType(Type.RECORD).withStream(USERS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("name", "susan").put("id", "30"));
  private static final SingerMessage SINGER_MESSAGE_TASKS1 = new SingerMessage().withType(Type.RECORD).withStream(TASKS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("goal", "announce the game."));
  private static final SingerMessage SINGER_MESSAGE_TASKS2 = new SingerMessage().withType(Type.RECORD).withStream(TASKS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("goal", "ship some code."));
  private static final SingerMessage SINGER_MESSAGE_RECORD = new SingerMessage().withType(Type.STATE)
      .withValue(objectMapper.createObjectNode().put("checkpoint", "now!"));

  private static final Schema CATALOG = new Schema().withStreams(Lists.newArrayList(
      new Stream().withName(USERS_STREAM_NAME)
          .withFields(Lists.newArrayList(new Field().withName("name").withDataType(DataType.STRING).withSelected(true),
              new Field().withName("id").withDataType(DataType.STRING).withSelected(true))),
      new Stream().withName(TASKS_STREAM_NAME)
          .withFields(Lists.newArrayList(new Field().withName("goal").withDataType(DataType.STRING).withSelected(true)))));

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
    final StandardCheckConnectionOutput actual = new PostgresDestination().check(config);
    final StandardCheckConnectionOutput expected = new StandardCheckConnectionOutput().withStatus(Status.SUCCESS);
    assertEquals(expected, actual);
  }

  @Test
  void testCheckFailure() {
    ((ObjectNode) config).put("password", "fake");
    final StandardCheckConnectionOutput actual = new PostgresDestination().check(config);
    final StandardCheckConnectionOutput expected = new StandardCheckConnectionOutput().withStatus(Status.FAILURE)
        .withMessage("Cannot create PoolableConnectionFactory (FATAL: password authentication failed for user \"test\")");
    assertEquals(expected, actual);
  }

  @Test
  void testWriteSuccess() throws Exception {
    final DestinationConsumer<SingerMessage> consumer = new PostgresDestination().write(config, CATALOG);

    consumer.accept(SINGER_MESSAGE_USERS1);
    consumer.accept(SINGER_MESSAGE_TASKS1);
    consumer.accept(SINGER_MESSAGE_USERS2);
    consumer.accept(SINGER_MESSAGE_TASKS2);
    consumer.accept(SINGER_MESSAGE_RECORD);
    consumer.close();

    Set<JsonNode> usersActual = recordRetriever(USERS_STREAM_NAME);
    final Set<JsonNode> expectedUsersJson = Sets.newHashSet(SINGER_MESSAGE_USERS1.getRecord(), SINGER_MESSAGE_USERS2.getRecord());
    assertEquals(expectedUsersJson, usersActual);

    Set<JsonNode> tasksActual = recordRetriever(TASKS_STREAM_NAME);
    final Set<JsonNode> expectedTasksJson = Sets.newHashSet(SINGER_MESSAGE_TASKS1.getRecord(), SINGER_MESSAGE_TASKS2.getRecord());
    assertEquals(expectedTasksJson, tasksActual);

    assertTmpTablesNotPresent(CATALOG.getStreams().stream().map(Stream::getName).collect(Collectors.toList()));
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testWriteFailure() throws Exception {
    // hack to force an exception to be thrown from within the consumer.
    final SingerMessage spiedMessage = spy(SINGER_MESSAGE_USERS1);
    doThrow(new RuntimeException()).when(spiedMessage).getStream();

    final DestinationConsumer<SingerMessage> consumer = spy(new PostgresDestination().write(config, CATALOG));

    assertThrows(RuntimeException.class, () -> consumer.accept(spiedMessage));
    consumer.accept(SINGER_MESSAGE_USERS2);
    consumer.close();

    final List<String> tableNames = CATALOG.getStreams().stream().map(Stream::getName).collect(toList());
    assertTmpTablesNotPresent(CATALOG.getStreams().stream().map(Stream::getName).collect(Collectors.toList()));
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
            .fetch(String.format("SELECT * FROM %s ORDER BY ab_inserted_at ASC;", streamName))
            .stream()
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
