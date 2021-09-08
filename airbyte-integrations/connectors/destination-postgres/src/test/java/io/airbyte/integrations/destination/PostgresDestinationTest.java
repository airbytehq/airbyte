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

package io.airbyte.integrations.destination;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.postgres.PostgresDestination;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.time.Instant;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class PostgresDestinationTest {

  private static PostgreSQLContainer<?> PSQL_DB;

  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "id_and_name";
  private static final ConfiguredAirbyteCatalog CATALOG = new ConfiguredAirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createConfiguredAirbyteStream(
          STREAM_NAME,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaPrimitive.NUMBER),
          Field.of("name", JsonSchemaPrimitive.STRING))));

  private JsonNode config;

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();
  }

  @BeforeEach
  void setup() {
    config = PostgreSQLContainerHelper.createDatabaseWithRandomNameAndGetPostgresConfig(PSQL_DB);
  }

  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

  // This test is a bit redundant with PostgresIntegrationTest. It makes it easy to run the
  // destination in the same process as the test allowing us to put breakpoint in, which is handy for
  // debugging (especially since we use postgres as a guinea pig for most features).
  @Test
  void sanityTest() throws Exception {
    final Destination destination = new PostgresDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, CATALOG, Destination::defaultOutputRecordCollector);
    final List<AirbyteMessage> expectedRecords = getNRecords(10);

    consumer.start();
    expectedRecords.forEach(m -> {
      try {
        consumer.accept(m);
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    });
    consumer.accept(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(SCHEMA_NAME + "." + STREAM_NAME, 10)))));
    consumer.close();

    final JdbcDatabase database = PostgreSQLContainerHelper.getJdbcDatabaseFromConfig(config);

    final List<JsonNode> actualRecords = database.bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT * FROM public._airbyte_raw_id_and_name;"),
        JdbcUtils.getDefaultSourceOperations()::rowToJson);

    assertEquals(
        expectedRecords.stream().map(AirbyteMessage::getRecord).map(AirbyteRecordMessage::getData).collect(Collectors.toList()),
        actualRecords.stream().map(o -> o.get("_airbyte_data").asText()).map(Jsons::deserialize).collect(Collectors.toList()));
  }

  private List<AirbyteMessage> getNRecords(int n) {
    return IntStream.range(0, n)
        .boxed()
        .map(i -> new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(STREAM_NAME)
                .withNamespace(SCHEMA_NAME)
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "human " + i)))))
        .collect(Collectors.toList());
  }

}
