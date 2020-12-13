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

package io.airbyte.integrations.source.jdbc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doCallRealMethod;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.models.JdbcState;
import io.airbyte.integrations.source.jdbc.models.JdbcStreamState;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;

// todo (cgardens) - either remove AbstractJooqSource or have this test extend
// JdbcSourceStandardTest so that we can ensure the behavior is the same.
class AbstractJooqSourceTest {

  private static final String STREAM_NAME = "public.id_and_name";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(Lists.newArrayList(CatalogHelpers.createAirbyteStream(
      STREAM_NAME,
      Field.of("id", JsonSchemaPrimitive.NUMBER),
      Field.of("name", JsonSchemaPrimitive.STRING),
      Field.of("updated_at", JsonSchemaPrimitive.STRING))
      .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))));
  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers.toDefaultConfiguredCatalog(CATALOG);
  private static final List<AirbyteMessage> MESSAGES = Lists.newArrayList(
      new AirbyteMessage().withType(Type.RECORD)
          .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME)
              .withData(Jsons.jsonNode(ImmutableMap.of("id", 1, "name", "picard", "updated_at", "2004-10-19")))),
      new AirbyteMessage().withType(Type.RECORD)
          .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME)
              .withData(Jsons.jsonNode(ImmutableMap.of("id", 2, "name", "crusher", "updated_at", "2005-10-19")))),
      new AirbyteMessage().withType(Type.RECORD)
          .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME)
              .withData(Jsons.jsonNode(ImmutableMap.of("id", 3, "name", "vash", "updated_at", "2006-10-19")))));

  private JsonNode config;

  private PostgreSQLContainer<?> container;
  private Database database;
  private Source source;

  @BeforeEach
  void setup() throws Exception {
    source = new PostgresJooqTestSource();
    container = new PostgreSQLContainer<>("postgres:13-alpine");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("jdbc_url", String.format("jdbc:postgresql://%s:%s/%s",
            container.getHost(),
            container.getFirstMappedPort(),
            container.getDatabaseName()))
        .build());

    database = Databases.createPostgresDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        config.get("jdbc_url").asText());

    database.query(ctx -> {
      // todo (cgardens) - jooq has inconsistent behavior in how it picks the current timezone across mac
      // and the CI. it does not in the DSL allow us to set a timezone. this may be the last straw for
      // jooq, because it means we can't fully abstract over it it with this source.
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), updated_at DATE);");
      ctx.fetch(
          "INSERT INTO id_and_name (id, name, updated_at) VALUES (1,'picard', '2004-10-19'),  (2, 'crusher', '2005-10-19'), (3, 'vash', '2006-10-19');");
      return null;
    });
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
    container.close();
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source.spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  @Test
  void testCheckSuccess() throws Exception {
    final AirbyteConnectionStatus actual = source.check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @Test
  void testCheckFailure() throws Exception {
    ((ObjectNode) config).put("password", "fake");
    final AirbyteConnectionStatus actual = source.check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.FAILED)
        .withMessage("Can't connect with provided configuration.");
    assertEquals(expected, actual);
  }

  @Test
  void testDiscover() throws Exception {
    final AirbyteCatalog actual = source.discover(config);
    assertEquals(CATALOG, actual);
  }

  @Test
  void testReadSuccess() throws Exception {
    final List<AirbyteMessage> actualMessages = source.read(config, getConfiguredCatalog(), null).collect(Collectors.toList());

    actualMessages.forEach(r -> {
      if (r.getRecord() != null) {
        r.getRecord().setEmittedAt(null);
      }
    });

    assertEquals(MESSAGES, actualMessages);
  }

  @Test
  void testReadOneColumn() throws Exception {
    final ConfiguredAirbyteCatalog catalog = CatalogHelpers.createConfiguredAirbyteCatalog(STREAM_NAME, Field.of("id", JsonSchemaPrimitive.NUMBER));

    final List<AirbyteMessage> actualMessages = source.read(config, catalog, null).collect(Collectors.toList());

    actualMessages.forEach(r -> {
      if (r.getRecord() != null) {
        r.getRecord().setEmittedAt(null);
      }
    });

    final List<AirbyteMessage> expectedMessages = MESSAGES.stream()
        .map(Jsons::clone)
        .peek(m -> {
          ((ObjectNode) m.getRecord().getData()).remove("name");
          ((ObjectNode) m.getRecord().getData()).remove("updated_at");
        })
        .collect(Collectors.toList());
    assertEquals(expectedMessages, actualMessages);
  }

  @Test
  void testReadMultipleTables() throws Exception {
    final String streamName2 = STREAM_NAME + 2;
    database.query(ctx -> {
      ctx.fetch("CREATE TABLE id_and_name2(id INTEGER, name VARCHAR(200));");
      ctx.fetch("INSERT INTO id_and_name2 (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");

      return null;
    });

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        getConfiguredCatalog().getStreams().get(0),
        CatalogHelpers.createConfiguredAirbyteStream(
            streamName2,
            Field.of("id", JsonSchemaPrimitive.NUMBER),
            Field.of("name", JsonSchemaPrimitive.STRING))));
    final List<AirbyteMessage> actualMessages = source.read(config, catalog, null).collect(Collectors.toList());

    actualMessages.forEach(r -> {
      if (r.getRecord() != null) {
        r.getRecord().setEmittedAt(null);
      }
    });

    final List<AirbyteMessage> secondStreamExpectedMessages = MESSAGES
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamName2);
          ((ObjectNode) m.getRecord().getData()).remove("updated_at");
        })
        .collect(Collectors.toList());
    final List<AirbyteMessage> expectedMessages = new ArrayList<>(MESSAGES);
    expectedMessages.addAll(secondStreamExpectedMessages);

    assertEquals(expectedMessages, actualMessages);
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testReadFailure() {
    final ConfiguredAirbyteStream spiedAbStream = spy(getConfiguredCatalog().getStreams().get(0));
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(spiedAbStream));
    doCallRealMethod().doThrow(new RuntimeException()).when(spiedAbStream).getStream();

    assertThrows(RuntimeException.class, () -> source.read(config, catalog, null));
  }

  @Test
  void testIncrementalNoPreviousState() throws Exception {
    incrementalCursorCheck(
        "id",
        null,
        "3",
        Lists.newArrayList(MESSAGES));
  }

  @Test
  void testIncrementalIntCheckCursor() throws Exception {
    incrementalCursorCheck(
        "id",
        "2",
        "3",
        Lists.newArrayList(MESSAGES.get(2)));
  }

  @Test
  void testIncrementalStringCheckCursor() throws Exception {
    incrementalCursorCheck(
        "name",
        "patent",
        "vash",
        Lists.newArrayList(MESSAGES.get(0), MESSAGES.get(2)));
  }

  @Test
  void testIncrementalTimestampCheckCursor() throws Exception {
    incrementalCursorCheck(
        "updated_at",
        "2005-10-18",
        "2006-10-19",
        Lists.newArrayList(MESSAGES.get(1), MESSAGES.get(2)));
  }

  @Test
  void testIncrementalCursorChanges() throws Exception {
    incrementalCursorCheck(
        "id",
        "name",
        // cheesing this value a little bit. in the correct implementation this initial cursor value should
        // be ignored because the cursor field changed. setting it to a value that if used, will cause
        // records to (incorrectly) be filtered out.
        "data",
        "vash",
        Lists.newArrayList(MESSAGES));
  }

  @Test
  void testReadOneTableIncrementallyTwice() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(Lists.newArrayList("id"));
    });

    final JdbcState state = new JdbcState().withStreams(Lists.newArrayList(new JdbcStreamState().withStreamName(STREAM_NAME)));
    final List<AirbyteMessage> actualMessagesFirstSync = source.read(config, configuredCatalog, Jsons.jsonNode(state)).collect(Collectors.toList());

    final Optional<AirbyteMessage> stateAfterFirstSyncOptional = actualMessagesFirstSync.stream().filter(r -> r.getType() == Type.STATE).findFirst();
    assertTrue(stateAfterFirstSyncOptional.isPresent());

    database.query(ctx -> {
      ctx.fetch(
          "INSERT INTO id_and_name (id, name, updated_at) VALUES (4,'riker', '2006-10-19'),  (5, 'data', '2006-10-19');");
      return null;
    });

    final List<AirbyteMessage> actualMessagesSecondSync = source
        .read(config, configuredCatalog, stateAfterFirstSyncOptional.get().getState().getData())
        .collect(Collectors.toList());

    assertEquals(2, (int) actualMessagesSecondSync.stream().filter(r -> r.getType() == Type.RECORD).count());
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME)
            .withData(Jsons.jsonNode(ImmutableMap.of("id", 4, "name", "riker", "updated_at", "2006-10-19")))));
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME)
            .withData(Jsons.jsonNode(ImmutableMap.of("id", 5, "name", "data", "updated_at", "2006-10-19")))));
    expectedMessages.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new JdbcState()
                .withStreams(Lists.newArrayList(new JdbcStreamState()
                    .withStreamName(STREAM_NAME)
                    .withCursorField(ImmutableList.of("id"))
                    .withCursor("5")))))));

    actualMessagesSecondSync.forEach(r -> {
      if (r.getRecord() != null) {
        r.getRecord().setEmittedAt(null);
      }
    });

    assertEquals(expectedMessages, actualMessagesSecondSync);
  }

  @Test
  void testReadMultipleTablesIncrementally() throws Exception {
    final String streamName2 = STREAM_NAME + 2;
    database.query(ctx -> {
      ctx.fetch("CREATE TABLE id_and_name2(id INTEGER, name VARCHAR(200));");
      ctx.fetch("INSERT INTO id_and_name2 (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
      return null;
    });

    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    configuredCatalog.getStreams().add(CatalogHelpers.createConfiguredAirbyteStream(
        streamName2,
        Field.of("id", JsonSchemaPrimitive.NUMBER),
        Field.of("name", JsonSchemaPrimitive.STRING)));
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(Lists.newArrayList("id"));
    });

    final JdbcState state = new JdbcState().withStreams(Lists.newArrayList(new JdbcStreamState().withStreamName(STREAM_NAME)));
    final List<AirbyteMessage> actualMessagesFirstSync = source.read(config, configuredCatalog, Jsons.jsonNode(state)).collect(Collectors.toList());

    // get last state message.
    final Optional<AirbyteMessage> stateAfterFirstSyncOptional = actualMessagesFirstSync.stream()
        .filter(r -> r.getType() == Type.STATE)
        .reduce((first, second) -> second);
    assertTrue(stateAfterFirstSyncOptional.isPresent());

    // we know the second streams messages are the same as the first minus the updated at column. so we
    // cheat and generate the expected messages off of the first expected messages.
    final List<AirbyteMessage> secondStreamExpectedMessages = MESSAGES
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamName2);
          ((ObjectNode) m.getRecord().getData()).remove("updated_at");
        })
        .collect(Collectors.toList());
    final List<AirbyteMessage> expectedMessagesFirstSync = new ArrayList<>(MESSAGES);
    expectedMessagesFirstSync.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new JdbcState()
                .withStreams(Lists.newArrayList(
                    new JdbcStreamState()
                        .withStreamName(STREAM_NAME)
                        .withCursorField(ImmutableList.of("id"))
                        .withCursor("3"),
                    new JdbcStreamState()
                        .withStreamName(streamName2)
                        .withCursorField(ImmutableList.of("id"))))))));
    expectedMessagesFirstSync.addAll(secondStreamExpectedMessages);
    expectedMessagesFirstSync.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new JdbcState()
                .withStreams(Lists.newArrayList(
                    new JdbcStreamState()
                        .withStreamName(STREAM_NAME)
                        .withCursorField(ImmutableList.of("id"))
                        .withCursor("3"),
                    new JdbcStreamState()
                        .withStreamName(streamName2)
                        .withCursorField(ImmutableList.of("id"))
                        .withCursor("3")))))));
    actualMessagesFirstSync.forEach(r -> {
      if (r.getRecord() != null) {
        r.getRecord().setEmittedAt(null);
      }
    });

    assertEquals(expectedMessagesFirstSync, actualMessagesFirstSync);
  }

  // when initial and final cursor fields are the same.
  private void incrementalCursorCheck(
                                      String cursorField,
                                      String initialCursorValue,
                                      String endCursorValue,
                                      List<AirbyteMessage> expectedRecordMessages)
      throws Exception {
    incrementalCursorCheck(cursorField, cursorField, initialCursorValue, endCursorValue, expectedRecordMessages);
  }

  private void incrementalCursorCheck(
                                      String initialCursorField,
                                      String cursorField,
                                      String initialCursorValue,
                                      String endCursorValue,
                                      List<AirbyteMessage> expectedRecordMessages)
      throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(Lists.newArrayList(cursorField));
    });

    final JdbcState state = new JdbcState()
        .withStreams(Lists.newArrayList(new JdbcStreamState()
            .withStreamName(STREAM_NAME)
            .withCursorField(ImmutableList.of(initialCursorField))
            .withCursor(initialCursorValue)));

    final List<AirbyteMessage> actualMessages = source.read(config, configuredCatalog, Jsons.jsonNode(state)).collect(Collectors.toList());

    actualMessages.forEach(r -> {
      if (r.getRecord() != null) {
        r.getRecord().setEmittedAt(null);
      }
    });

    final List<AirbyteMessage> expectedMessages = new ArrayList<>(expectedRecordMessages);
    expectedMessages.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new JdbcState()
                .withStreams(Lists.newArrayList(new JdbcStreamState()
                    .withStreamName(STREAM_NAME)
                    .withCursorField(ImmutableList.of(cursorField))
                    .withCursor(endCursorValue)))))));

    assertEquals(expectedMessages, actualMessages);
  }

  // get catalog and perform a defensive copy.
  private static ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return Jsons.clone(CONFIGURED_CATALOG);
  }

  private static class PostgresJooqTestSource extends AbstractJooqSource implements Source {

    private static final Logger LOGGER = LoggerFactory.getLogger(PostgresJooqTestSource.class);

    public PostgresJooqTestSource() {
      super("org.postgresql.Driver", SQLDialect.POSTGRES);
    }

    // no-op for JooqSource since the config it receives is designed to be use for JDBC.
    @Override
    public JsonNode toJdbcConfig(JsonNode config) {
      return config;
    }

    public static void main(String[] args) throws Exception {
      final Source source = new PostgresJooqTestSource();
      LOGGER.info("starting source: {}", PostgresJooqTestSource.class);
      new IntegrationRunner(source).run(args);
      LOGGER.info("completed source: {}", PostgresJooqTestSource.class);
    }

  }

}
