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

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.DataType;
import io.airbyte.config.DestinationConnectionSpecification;
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
import java.nio.file.Files;
import java.nio.file.Path;
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
    final DestinationConnectionSpecification actual = new PostgresDestination().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final DestinationConnectionSpecification expected = Jsons.deserialize(resourceString, DestinationConnectionSpecification.class);

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

    // verify that the file is parsable as json (sanity check since the quoting is so goofy).
    List<JsonNode> usersActual = recordRetriever(USERS_STREAM_NAME);
    final List<JsonNode> expectedUsersJson = Lists.newArrayList(SINGER_MESSAGE_USERS1.getRecord(), SINGER_MESSAGE_USERS2.getRecord());
    assertEquals(expectedUsersJson, usersActual);

    List<JsonNode> tasksActual = recordRetriever(TASKS_STREAM_NAME);
    final List<JsonNode> expectedTasksJson = Lists.newArrayList(SINGER_MESSAGE_TASKS1.getRecord(), SINGER_MESSAGE_TASKS2.getRecord());
    assertEquals(expectedTasksJson, tasksActual);
  }

  @Test
  void testWriteFailure() throws Exception {
  }

  private List<JsonNode> recordRetriever(String streamName) throws Exception {
    BasicDataSource pool =
        DatabaseHelper.getConnectionPool(db.getUsername(), db.getPassword(), db.getJdbcUrl());

    return DatabaseHelper.query(
        pool,
        ctx -> ctx
            .fetch(String.format("SELECT * FROM public.%s ORDER BY ab_inserted_at ASC;", streamName))
//            .fetch(String.format("SELECT * FROM %s ORDER BY inserted_at ASC;", streamName))
            .stream()
            .map(Record::intoMap)
            .map(r -> r.entrySet().stream().map(e -> {
              // todo (cgardens) - bad in place mutation.
              if (e.getValue().getClass().equals(org.jooq.JSONB.class)) {
                e.setValue(e.getValue().toString());
              }
              return e;
            }).collect(Collectors.toMap(Entry::getKey, Entry::getValue)))
            .map(r -> (String)r.get("data"))
            .map(Jsons::deserialize)
            .collect(toList()));
  }
}
