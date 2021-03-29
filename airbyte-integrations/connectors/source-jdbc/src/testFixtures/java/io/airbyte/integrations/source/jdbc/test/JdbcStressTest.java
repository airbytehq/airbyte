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
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.BitSet;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Runs a "large" amount of data through a JdbcSource to ensure that it streams / chunks records.
 */
// todo (cgardens) - this needs more love and thought. we should be able to test this without having
// to rewrite so much data. it is enough for now to sanity check that our JdbcSources can actually
// handle more data than fits in memory.
public abstract class JdbcStressTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(JdbcStressTest.class);

  // this will get rounded down to the nearest 1000th.
  private static final long TOTAL_RECORDS = 10_000_000L;
  private static final int BATCH_SIZE = 1000;
  private static final String TABLE_NAME = "id_and_name";

  private static String streamName;

  private BitSet bitSet;
  private JsonNode config;
  private AbstractJdbcSource source;

  /**
   * These tests write records without specifying a namespace (schema name). They will be written into
   * whatever the default schema is for the database. When they are discovered they will be namespaced
   * by the schema name (e.g. <default-schema-name>.<table_name>). Thus the source needs to tell the
   * tests what that default schema name is. If the database does not support schemas, then database
   * name should used instead.
   *
   * @return name that will be used to namespace the record.
   */
  public abstract Optional<String> getDefaultSchemaName();

  /**
   * A valid configuration to connect to a test database.
   *
   * @return config
   */
  public abstract JsonNode getConfig();

  /**
   * Full qualified class name of the JDBC driver for the database.
   *
   * @return driver
   */
  public abstract String getDriverClass();

  /**
   * An instance of the source that should be tests.
   *
   * @return source
   */
  public abstract AbstractJdbcSource getSource();

  public void setup() throws Exception {
    LOGGER.info("running for driver:" + getDriverClass());
    bitSet = new BitSet((int) TOTAL_RECORDS);

    source = getSource();
    streamName = getDefaultSchemaName().map(val -> val + "." + TABLE_NAME).orElse(TABLE_NAME);
    config = getConfig();

    final JsonNode jdbcConfig = source.toJdbcConfig(config);
    JdbcDatabase database = Databases.createJdbcDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        getDriverClass());

    database.execute(connection -> connection.createStatement().execute("CREATE TABLE id_and_name(id BIGINT, name VARCHAR(200));"));
    final long batchCount = TOTAL_RECORDS / BATCH_SIZE;
    LOGGER.info("writing {} batches of {}", batchCount, BATCH_SIZE);
    for (int i = 0; i < batchCount; i++) {
      if (i % 1000 == 0)
        LOGGER.info("writing batch: " + i);
      final List<String> insert = new ArrayList<>();
      for (int j = 0; j < BATCH_SIZE; j++) {
        int recordNumber = (i * BATCH_SIZE) + j;
        insert.add(String.format("(%s,'picard-%s')", recordNumber, recordNumber));
      }
      final String sql = String.format("INSERT INTO id_and_name (id, name) VALUES %s;", Strings.join(insert, ", "));
      database.execute(connection -> connection.createStatement().execute(sql));
    }

  }

  // todo (cgardens) - restructure these tests so that testFullRefresh() and testIncremental() can be
  // separate tests. current constrained by only wanting to setup the fixture in the database once,
  // but it is not trivial to move them to @BeforeAll because it is static and we are doing
  // inheritance. Not impossible, just needs to be done thoughtfully and for all JdbcSources.
  @Test
  public void stressTest() throws Exception {
    testFullRefresh();
    testIncremental();
  }

  private void testFullRefresh() throws Exception {
    runTest(getConfiguredCatalogFullRefresh(), "full_refresh");
  }

  private void testIncremental() throws Exception {
    runTest(getConfiguredCatalogIncremental(), "incremental");
  }

  private void runTest(ConfiguredAirbyteCatalog configuredCatalog, String testName) throws Exception {
    LOGGER.info("running stress test for: " + testName);
    final Iterator<AirbyteMessage> read = source.read(config, configuredCatalog, Jsons.jsonNode(Collections.emptyMap()));
    final long actualCount = MoreStreams.toStream(read)
        .filter(m -> m.getType() == Type.RECORD)
        .peek(m -> {
          if (m.getRecord().getData().get("id").asLong() % 100000 == 0) {
            LOGGER.info("reading batch: " + m.getRecord().getData().get("id").asLong() / 1000);
          }
        })
        .peek(m -> assertExpectedMessage(m))
        .count();
    ByteBuffer a;
    final long expectedRoundedRecordsCount = TOTAL_RECORDS - TOTAL_RECORDS % 1000;
    LOGGER.info("expected records count: " + TOTAL_RECORDS);
    LOGGER.info("actual records count: " + actualCount);
    assertEquals(expectedRoundedRecordsCount, actualCount, "testing: " + testName);
    assertEquals(expectedRoundedRecordsCount, bitSet.cardinality(), "testing: " + testName);
  }

  // each is roughly 106 bytes.
  private void assertExpectedMessage(AirbyteMessage actualMessage) {
    final long recordNumber = actualMessage.getRecord().getData().get("id").asLong();
    bitSet.set((int) recordNumber);
    actualMessage.getRecord().setEmittedAt(null);

    final AirbyteMessage expectedMessage = new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName)
            .withData(Jsons.jsonNode(ImmutableMap.of("id", recordNumber, "name", "picard-" + recordNumber))));
    assertEquals(expectedMessage, actualMessage);
  }

  private static ConfiguredAirbyteCatalog getConfiguredCatalogFullRefresh() {
    return CatalogHelpers.toDefaultConfiguredCatalog(getCatalog());
  }

  private static ConfiguredAirbyteCatalog getConfiguredCatalogIncremental() {
    return new ConfiguredAirbyteCatalog()
        .withStreams(Collections.singletonList(new ConfiguredAirbyteStream().withStream(getCatalog().getStreams().get(0))
            .withCursorField(Collections.singletonList("id"))
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)));
  }

  private static AirbyteCatalog getCatalog() {
    return new AirbyteCatalog().withStreams(Lists.newArrayList(CatalogHelpers.createAirbyteStream(
        streamName,
        Field.of("id", JsonSchemaPrimitive.NUMBER),
        Field.of("name", JsonSchemaPrimitive.STRING))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))));
  }

}
