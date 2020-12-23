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

package io.airbyte.integrations.source.jdbc.test;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.models.JdbcState;
import io.airbyte.integrations.source.jdbc.models.JdbcStreamState;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.sql.PreparedStatement;
import java.sql.Timestamp;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.Test;

public abstract class DbSourceDateTimeStandardTest {

  private static final String TABLE_NAME = "id_and_name";

  private JsonNode config;
  private JdbcDatabase database;
  // private AbstractJdbcSource2 source;
  private AbstractJdbcSource source;
  private static String streamName;

  public abstract Optional<String> getSchemaName();

  public abstract JsonNode getConfig();

  public abstract String getDriverClass();

  public abstract AbstractJdbcSource getSource();

  // keyword to be used to create the datetime table.
  public abstract String getDatetimeKeyword();

  // ascending list of 3 datetime strings as required to be written to the db, and its equivalent in
  // iso8601
  public abstract List<ImmutablePair<String, String>> getDateTimes();

  // @BeforeEach
  public void setup() throws Exception {
    source = getSource();
    streamName = getSchemaName().map(val -> val + "." + TABLE_NAME).orElse(TABLE_NAME);
    config = getConfig();

    final JsonNode jdbcConfig = source.toJdbcConfig(config);
    database = Databases.createJdbcDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        getDriverClass());

    Preconditions.checkState(getDateTimes().size() == 3, "Must provided 3 date times.");

    database.execute(connection -> {
      try {
        connection.createStatement().execute(String.format("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), updated_at %s);", getDatetimeKeyword()));
        SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'");
        final PreparedStatement preparedStatement = connection.prepareStatement("INSERT INTO id_and_name (id, name, updated_at) VALUES (?,?,?)");
        preparedStatement.setInt(1, 1);
        preparedStatement.setString(2, "picard");
        preparedStatement.setTimestamp(3, Timestamp.from(df.parse(getDateTimes().get(0).getLeft()).toInstant()));
        preparedStatement.execute();
        preparedStatement.setInt(1, 2);
        preparedStatement.setString(2, "crusher");
        preparedStatement.setTimestamp(3, Timestamp.from(df.parse(getDateTimes().get(1).getLeft()).toInstant()));
        preparedStatement.execute();
        preparedStatement.setInt(1, 3);
        preparedStatement.setString(2, "vash");
        preparedStatement.setTimestamp(3, Timestamp.from(df.parse(getDateTimes().get(2).getLeft()).toInstant()));
        preparedStatement.execute();
        // ctx.createStatement().execute(String.format(
        // "INSERT INTO id_and_name (id, name, updated_at) VALUES (1,'picard', '%s'), (2, 'crusher', '%s'),
        // (3, 'vash', '%s');",
        // getDateTimes().get(0).getLeft(),
        // getDateTimes().get(1).getLeft(),
        // getDateTimes().get(2).getLeft()
        // ));
      } catch (ParseException e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Test
  void testIncrementalDatetimeCheckCursorNoInitialCursorValue() throws Exception {
    incrementalCursorCheck(
        "updated_at",
        null,
        getDateTimes().get(2).getRight(),
        Lists.newArrayList(getTestMessages()));
  }

  @Test
  void testIncrementalDatetimeCheckCursor() throws Exception {
    incrementalCursorCheck(
        "updated_at",
        getDateTimes().get(0).getRight(),
        getDateTimes().get(2).getRight(),
        Lists.newArrayList(getTestMessages().get(1), getTestMessages().get(2)));
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
            .withStreamName(streamName)
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
                    .withStreamName(streamName)
                    .withCursorField(ImmutableList.of(cursorField))
                    .withCursor(endCursorValue)))))));

    assertEquals(expectedMessages, actualMessages);
  }

  // get catalog and perform a defensive copy.
  private static ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CatalogHelpers.toDefaultConfiguredCatalog(getCatalog());
  }

  private static AirbyteCatalog getCatalog() {
    return new AirbyteCatalog().withStreams(Lists.newArrayList(CatalogHelpers.createAirbyteStream(
        streamName,
        Field.of("id", JsonSchemaPrimitive.NUMBER),
        Field.of("name", JsonSchemaPrimitive.STRING),
        Field.of("updated_at", JsonSchemaPrimitive.STRING))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))));
  }

  private List<AirbyteMessage> getTestMessages() {
    return Lists.newArrayList(
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName)
                .withData(Jsons.jsonNode(ImmutableMap.of("id", 1, "name", "picard", "updated_at", getDateTimes().get(0).getRight())))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName)
                .withData(Jsons.jsonNode(ImmutableMap.of("id", 2, "name", "crusher", "updated_at", getDateTimes().get(1).getRight())))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName)
                .withData(Jsons.jsonNode(ImmutableMap.of("id", 3, "name", "vash", "updated_at", getDateTimes().get(2).getRight())))));
  }

}
