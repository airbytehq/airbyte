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

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.DbSourceDateTimeStandardTest;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.util.List;
import java.util.Optional;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class PostgresSourceDatetimeStandardTest2 extends DbSourceDateTimeStandardTest {

  // private static final String STREAM_NAME = "public.id_and_name";
  // private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
  // CatalogHelpers.createAirbyteStream(
  // STREAM_NAME,
  // Field.of("id", JsonSchemaPrimitive.NUMBER),
  // Field.of("name", JsonSchemaPrimitive.STRING))
  // .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)),
  // CatalogHelpers.createAirbyteStream(
  // "test_another_schema.id_and_name",
  // Field.of("id", JsonSchemaPrimitive.NUMBER),
  // Field.of("name", JsonSchemaPrimitive.STRING))
  // .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))));
  // private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG =
  // CatalogHelpers.createConfiguredAirbyteCatalog(
  // STREAM_NAME,
  // Field.of("id", JsonSchemaPrimitive.NUMBER),
  // Field.of("name", JsonSchemaPrimitive.STRING));
  // private static final Set<AirbyteMessage> ASCII_MESSAGES = Sets.newHashSet(
  // new AirbyteMessage().withType(Type.RECORD)
  // .withRecord(new
  // AirbyteRecordMessage().withStream(STREAM_NAME).withData(Jsons.jsonNode(ImmutableMap.of("id", 1,
  // "name", "goku")))),
  // new AirbyteMessage().withType(Type.RECORD)
  // .withRecord(new
  // AirbyteRecordMessage().withStream(STREAM_NAME).withData(Jsons.jsonNode(ImmutableMap.of("id", 2,
  // "name", "vegeta")))),
  // new AirbyteMessage().withType(Type.RECORD)
  // .withRecord(new
  // AirbyteRecordMessage().withStream(STREAM_NAME).withData(Jsons.jsonNode(ImmutableMap.of("id", 3,
  // "name", "piccolo")))));
  //
  // private static final Set<AirbyteMessage> UTF8_MESSAGES = Sets.newHashSet(
  // new AirbyteMessage().withType(Type.RECORD)
  // .withRecord(
  // new AirbyteRecordMessage().withStream(STREAM_NAME).withData(Jsons.jsonNode(ImmutableMap.of("id",
  // 1, "name", "\u2013 someutfstring")))),
  // new AirbyteMessage().withType(Type.RECORD)
  // .withRecord(new
  // AirbyteRecordMessage().withStream(STREAM_NAME).withData(Jsons.jsonNode(ImmutableMap.of("id", 2,
  // "name", "\u2215")))));

  private static PostgreSQLContainer<?> PSQL_DB;

  private JsonNode config;

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();

  }

  @BeforeEach
  public void setup() throws Exception {
    final String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

    config = getConfig(PSQL_DB, dbName);

    final String initScriptName = "init_" + dbName.concat(".sql");
    MoreResources.writeResource(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource(initScriptName), PSQL_DB);

    final Database database = getDatabaseFromConfig(config);
    database.query(ctx -> {
      // ctx.fetch("SET TIME ZONE 'UTC';");
      // ctx.fetch("ALTER USER postgres SET timezone='UTC';");
      // ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      // ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'goku'), (2, 'vegeta'), (3,
      // 'piccolo');");
      // ctx.fetch("CREATE SCHEMA test_another_schema;");
      // ctx.fetch("CREATE TABLE test_another_schema.id_and_name(id INTEGER, name VARCHAR(200));");
      // ctx.fetch("INSERT INTO test_another_schema.id_and_name (id, name) VALUES (1,'tom'), (2,
      // 'jerry');");
      return null;
    });
    database.close();
    super.setup();
  }

  @Override
  public Optional<String> getSchemaName() {
    return Optional.of("public");
  }

  @Override
  public AbstractJdbcSource getSource() {
    return new PostgresSource();
  }

  @Override
  public String getDatetimeKeyword() {
    return "TIMESTAMP WITH TIME ZONE";
  }

  @Override
  public List<ImmutablePair<String, String>> getDateTimes() {
    return Lists.newArrayList(
        ImmutablePair.of("2004-10-19T14:04:03Z", "2004-10-19T14:04:03Z"),
        ImmutablePair.of("2005-10-19T14:04:03Z", "2005-10-19T14:04:03Z"),
        ImmutablePair.of("2006-10-19T14:04:03Z", "2006-10-19T14:04:03Z"));
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public String getDriverClass() {
    return PostgresSource.DRIVER_CLASS;
  }

  private Database getDatabaseFromConfig(JsonNode config) {
    return Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "org.postgresql.Driver",
        SQLDialect.POSTGRES);
  }

  private JsonNode getConfig(PostgreSQLContainer<?> psqlDb, String dbName) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", psqlDb.getHost())
        .put("port", psqlDb.getFirstMappedPort())
        .put("database", dbName)
        .put("username", psqlDb.getUsername())
        .put("password", psqlDb.getPassword())
        .build());
  }

  private JsonNode getConfig(PostgreSQLContainer<?> psqlDb) {
    return getConfig(psqlDb, psqlDb.getDatabaseName());
  }

  // todo check close for all of them
  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

}
