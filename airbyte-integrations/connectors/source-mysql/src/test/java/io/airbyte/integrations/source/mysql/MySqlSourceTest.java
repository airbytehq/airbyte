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

package io.airbyte.integrations.source.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.doCallRealMethod;
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
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

class MySqlSourceTest {

  private static final String TEST_USER = "test";
  private static final String TEST_PASSWORD = "test";
  private static final String STREAM_NAME = "id_and_name";
  private static MySQLContainer<?> container;

  private JsonNode config;

  @BeforeAll
  static void init() {
    // test containers withInitScript only accepts scripts that are mounted as resources.
    MoreResources.writeResource("init.sql",
        "CREATE USER '" + TEST_USER + "'@'%' IDENTIFIED BY '" + TEST_PASSWORD + "';\n"
            + "GRANT ALL PRIVILEGES ON *.* TO '" + TEST_USER + "'@'%';\n");
    container = new MySQLContainer<>("mysql:8.0").withInitScript("init.sql").withUsername("root").withPassword("");
    container.start();
  }

  @BeforeEach
  void setup() throws Exception {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", "db_" + RandomStringUtils.randomAlphabetic(10))
        .put("username", TEST_USER)
        .put("password", TEST_PASSWORD)
        .build());

    final Database database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:mysql://%s:%s",
            config.get("host").asText(),
            config.get("port").asText()),
        "com.mysql.cj.jdbc.Driver",
        SQLDialect.MYSQL);

    database.query(ctx -> {
      ctx.fetch("CREATE DATABASE " + config.get("database").asText());
      ctx.fetch("USE " + config.get("database").asText());
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");

      return null;
    });
    database.close();
  }

  @AfterAll
  static void cleanUp() {
    container.close();
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = new MySqlSource().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  @Test
  void testCheckSuccess() {
    final AirbyteConnectionStatus actual = new MySqlSource().check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @Test
  void testCheckFailure() {
    ((ObjectNode) config).put("password", "fake");
    final AirbyteConnectionStatus actual = new MySqlSource().check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.FAILED)
        .withMessage("Can't connect with provided configuration.");
    assertEquals(expected, actual);
  }

  @Test
  void testDiscover() throws Exception {
    final AirbyteCatalog allStreams = new MySqlSource().discover(config);
    // Filter out streams not related to this test case (from other tests running in parallel)
    final AirbyteCatalog actual = new AirbyteCatalog()
        .withStreams(allStreams.getStreams()
            .stream()
            .filter(s -> s.getName().equals(getStreamName()))
            .collect(Collectors.toList()));
    assertEquals(generateExpectedCatalog(), actual);
  }

  @Test
  void testReadSuccess() throws Exception {
    final Set<AirbyteMessage> actualMessages = new MySqlSource().read(config, generateConfiguredCatalog(), null).collect(Collectors.toSet());

    actualMessages.forEach(r -> {
      if (r.getRecord() != null) {
        r.getRecord().setEmittedAt(null);
      }
    });

    assertEquals(generateExpectedMessages(), actualMessages);
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testReadFailure() throws Exception {
    final ConfiguredAirbyteStream spiedAbStream = spy(generateConfiguredCatalog().getStreams().get(0));
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(spiedAbStream));
    doCallRealMethod().doCallRealMethod().doThrow(new RuntimeException()).when(spiedAbStream).getStream();

    final MySqlSource source = new MySqlSource();

    assertThrows(RuntimeException.class, () -> source.read(config, catalog, null));
  }

  private AirbyteCatalog generateExpectedCatalog() {
    return CatalogHelpers.createAirbyteCatalog(
        getStreamName(),
        Field.of("id", JsonSchemaPrimitive.NUMBER),
        Field.of("name", JsonSchemaPrimitive.STRING));
  }

  private ConfiguredAirbyteCatalog generateConfiguredCatalog() {
    return CatalogHelpers.toDefaultConfiguredCatalog(generateExpectedCatalog());
  }

  private java.util.HashSet<AirbyteMessage> generateExpectedMessages() {
    final String streamName = getStreamName();
    return Sets.newHashSet(
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withData(Jsons.jsonNode(ImmutableMap.of("id", 1, "name", "picard")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withData(Jsons.jsonNode(ImmutableMap.of("id", 2, "name", "crusher")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withData(Jsons.jsonNode(ImmutableMap.of("id", 3, "name", "vash")))));
  }

  private String getStreamName() {
    return String.format("%s.%s", config.get("database").asText(), STREAM_NAME);
  }

}
