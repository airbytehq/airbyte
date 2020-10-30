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
import io.airbyte.integrations.source.jdbc.MySqlSource;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.dbcp2.BasicDataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.utility.MountableFile;

class MySqlSourceTest {

  private static final Instant NOW = Instant.now();
  private static final String STREAM_NAME = "id_and_name";
  private static final AirbyteCatalog CATALOG = CatalogHelpers.createAirbyteCatalog(
      STREAM_NAME,
      Field.of("id", JsonSchemaPrimitive.NUMBER),
      Field.of("name", JsonSchemaPrimitive.STRING));
  private static final Set<AirbyteMessage> MESSAGES = Sets.newHashSet(
      new AirbyteMessage().withType(Type.RECORD)
          .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME).withData(Jsons.jsonNode(ImmutableMap.of("id", 1, "name", "picard")))),
      new AirbyteMessage().withType(Type.RECORD)
          .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME).withData(Jsons.jsonNode(ImmutableMap.of("id", 2, "name", "crusher")))),
      new AirbyteMessage().withType(Type.RECORD)
          .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME).withData(Jsons.jsonNode(ImmutableMap.of("id", 3, "name", "vash"))))
  );

  private JsonNode config;

  private static MySQLContainer<?> db;

  @BeforeAll
  static void before() {
    // the start up on this container takes a minute. we can't start and stop between each test and live to tell the tale.
    db = new MySQLContainer<>("mysql:8.0");
    db.start();
  }

  @AfterAll
  static void after() {
    db.stop();
  }

  @BeforeEach
  void setup() throws SQLException, IOException {

    // rip mysql.
//    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("init_ascii.sql"), db);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("database", db.getDatabaseName())
        .put("user", db.getUsername())
        .put("password", db.getPassword())
        .build());

    final JsonNode jdbcConfig = MySqlSource.toJdbcConfig(config);
    final BasicDataSource connectionPool = new BasicDataSource();
    connectionPool.setDriverClassName("com.mysql.cj.jdbc.Driver");
    connectionPool.setUsername(jdbcConfig.get("username").asText());
    connectionPool.setPassword(jdbcConfig.get("password").asText());
    connectionPool.setUrl(jdbcConfig.get("jdbc_url").asText());

    // do the get tables version of this
//    DatabaseHelper.query(connectionPool, ctx -> ctx.dropTableIfExists("id_and_name"));
    DatabaseHelper.query(connectionPool, ctx -> ctx.fetch("DROP TABLE IF EXISTS id_and_name"));
    DatabaseHelper.query(connectionPool, ctx -> {
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");

      return null;
    });

//    final String sql = MoreResources.readResource("init_ascii.sql");
  }

  // todo - same test as csv destination
  @Test
  void testSpec() throws IOException {
    final ConnectorSpecification actual = new MySqlSource().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  // todo - same test as csv destination
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
        .withMessage("Cannot create PoolableConnectionFactory (FATAL: password authentication failed for user \"test\")");
    assertEquals(expected, actual);
  }

  @Test
  void testDiscover() throws Exception {
    final AirbyteCatalog actual = new MySqlSource().discover(config);
    assertEquals(CATALOG, actual);
  }

  @Test
  void testReadSuccess() throws Exception {
    final Set<AirbyteMessage> actualMessages = new MySqlSource().read(config, CATALOG, null).collect(Collectors.toSet());

    actualMessages.forEach(r -> {
      if (r.getRecord() != null) {
        r.getRecord().setEmittedAt(null);
      }
    });

    assertEquals(MESSAGES, actualMessages);
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testReadFailure() throws Exception {
    final AirbyteStream spiedAbStream = spy(CATALOG.getStreams().get(0));
    final AirbyteCatalog catalog = new AirbyteCatalog().withStreams(Lists.newArrayList(spiedAbStream));
    doThrow(new RuntimeException()).when(spiedAbStream).getName();

    final Stream<AirbyteMessage> stream = new MySqlSource().read(config, catalog, null);

    assertThrows(RuntimeException.class, () -> stream.collect(Collectors.toList()));
  }
}
