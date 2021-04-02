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

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class PostgresSourceCdcTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSourceCdcTest.class);

  private static final String SLOT_NAME = "debezium_slot";
  private static final String STREAM_NAME = "public.id_and_name";
  private static final String STREAM_NAME2 = "public.id_,something";
  private static final String STREAM_NAME3 = "public.n\"aMéS";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME,
          Field.of("id", JsonSchemaPrimitive.NUMBER),
          Field.of("name", JsonSchemaPrimitive.STRING),
          Field.of("power", JsonSchemaPrimitive.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("id"))),
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME2,
          Field.of("id", JsonSchemaPrimitive.NUMBER),
          Field.of("name", JsonSchemaPrimitive.STRING),
          Field.of("power", JsonSchemaPrimitive.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)),
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME3,
          Field.of("first_name", JsonSchemaPrimitive.STRING),
          Field.of("last_name", JsonSchemaPrimitive.STRING),
          Field.of("power", JsonSchemaPrimitive.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("first_name"), List.of("last_name")))));
  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers.toDefaultConfiguredCatalog(CATALOG);

  private static PostgreSQLContainer<?> PSQL_DB;

  private String dbName;
  private Database database;

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine")
        .withCopyFileToContainer(MountableFile.forClasspathResource("postgresql.conf"), "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
    PSQL_DB.start();
  }

  @BeforeEach
  void setup() throws Exception {
    dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

    final String initScriptName = "init_" + dbName.concat(".sql");
    MoreResources.writeResource(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource(initScriptName), PSQL_DB);

    final JsonNode config = getConfig(PSQL_DB, dbName);
    database = getDatabaseFromConfig(config);
    database.query(ctx -> {
      // ctx.execute("SELECT pg_create_logical_replication_slot('" + SLOT_NAME + "', 'pgoutput');");

      // need to re-add record that has -infinity.

      ctx.fetch("CREATE TABLE id_and_name(id NUMERIC(20, 10), name VARCHAR(200), power double precision, PRIMARY KEY (id));");
      ctx.execute("CREATE INDEX i1 ON id_and_name (id);");
      ctx.execute("begin; INSERT INTO id_and_name (id, name, power) VALUES (1,'goku', 'Infinity'),  (2, 'vegeta', 9000.1); commit;");

      ctx.fetch("CREATE TABLE \"id_,something\"(id NUMERIC(20, 10), name VARCHAR(200), power double precision);");
      ctx.fetch("INSERT INTO \"id_,something\" (id, name, power) VALUES (1,'goku', 'Infinity'),  (2, 'vegeta', 9000.1);");

      ctx.fetch(
          "CREATE TABLE \"n\"\"aMéS\"(first_name VARCHAR(200), last_name VARCHAR(200), power double precision, PRIMARY KEY (first_name, last_name));");
      ctx.fetch(
          "INSERT INTO \"n\"\"aMéS\"(first_name, last_name, power) VALUES ('san', 'goku', 'Infinity'),  ('prince', 'vegeta', 9000.1);");

      return null;
    });
    database.query(ctx -> {
      ctx.execute("begin; INSERT INTO id_and_name (id, name, power) VALUES (4,'picard', '10'); commit;");
      return null;
    });
    database.query(ctx -> {
      ctx.execute("begin; UPDATE id_and_name SET name='picard2' WHERE id=4; commit;");
      return null;
    });
    // database.close();
  }

  private JsonNode getConfig(PostgreSQLContainer<?> psqlDb, String dbName) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", psqlDb.getHost())
        .put("port", psqlDb.getFirstMappedPort())
        .put("database", dbName)
        .put("username", psqlDb.getUsername())
        .put("password", psqlDb.getPassword())
        .put("replication_slot", SLOT_NAME)
        .build());
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

  @Test
  public void testIt() throws Exception {
    final PostgresSource source = new PostgresSource();
    final ConfiguredAirbyteCatalog configuredCatalog = CONFIGURED_CATALOG;
    // coerce to incremental so it uses CDC.
    configuredCatalog.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));

    AirbyteCatalog catalog = source.discover(getConfig(PSQL_DB, dbName));

    LOGGER.info("catalog = " + catalog);

    final AutoCloseableIterator<AirbyteMessage> read = source.read(getConfig(PSQL_DB, dbName), configuredCatalog, null);

    Thread.sleep(5000);
    final JsonNode config = getConfig(PSQL_DB, dbName);
    final Database database = getDatabaseFromConfig(config);
    // database.query(ctx -> {
    // ctx.fetch(
    // "UPDATE names SET power = 10000.2 WHERE first_name = 'san';");
    // ctx.fetch(
    // "DELETE FROM names WHERE first_name = 'san';");
    // return null;
    // });
    // database.close();

    long startMillis = System.currentTimeMillis();
    final AtomicInteger i = new AtomicInteger(10);
    while (read.hasNext()) {
      database.query(ctx -> {
        ctx.execute(
            String.format("begin; INSERT INTO id_and_name (id, name, power) VALUES (%s,'goku%s', 'Infinity'),  (%s, 'vegeta%s', 9000.1); commit;",
                i.incrementAndGet(), i.incrementAndGet(), i.incrementAndGet(), i.incrementAndGet()));
        // ctx.execute(String.format("begin; UPDATE id_and_name SET name='goku%s' WHERE id=1; UPDATE
        // id_and_name SET name='picard%s' WHERE id=4; commit;", i.incrementAndGet(), i.incrementAndGet()));
        // ctx.execute(String.format("begin; UPDATE id_and_name SET name='goku%s' WHERE id=1; commit;",
        // i.incrementAndGet()));
        // ctx.execute(String.format("begin; UPDATE id_and_name SET name='picard%s' WHERE id=4; commit;",
        // i.incrementAndGet()));

        return null;
      });
      if (read.hasNext()) {
        System.out.println("it said it had next");
        System.out.println("read.next() = " + read.next());
      }
    }
  }

  @Test
  public void testWhitelistCreation() {
    final String expectedWhitelist = "public.id_and_name,public.id_\\,something,public.naMéS";
    final String actualWhitelist = PostgresSource.getTableWhitelist(CONFIGURED_CATALOG);

    assertEquals(expectedWhitelist, actualWhitelist);
  }

  @Test
  public void testItState() throws Exception {
    final PostgresSource source = new PostgresSource();
    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_CATALOG.withStreams(CONFIGURED_CATALOG.getStreams()
            .stream()
            .filter(s -> s.getStream().getName().equals(STREAM_NAME))
            .collect(Collectors.toList()));
    // coerce to incremental so it uses CDC.
    configuredCatalog.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));

    final AutoCloseableIterator<AirbyteMessage> read1 = source.read(getConfig(PSQL_DB, dbName), configuredCatalog, null);

    Thread.sleep(5000);
    final JsonNode config = getConfig(PSQL_DB, dbName);
    final Database database = getDatabaseFromConfig(config);

    // strategy run it once. then run it again with the state and verify no duplicate records are sent.
    final List<AirbyteMessage> messages1 = new ArrayList<>();
    while (read1.hasNext()) {
      messages1.add(read1.next());
    }
    final AirbyteMessage stateMessage = messages1.get(messages1.size() - 1);

    final AtomicInteger i = new AtomicInteger(10);
    while (i.get() < 20) {
      final int iValue = i.incrementAndGet();
      database.query(ctx -> {
        ctx.execute(
            String.format("begin; INSERT INTO id_and_name (id, name, power) VALUES (%s,'goku%s', 'Infinity'); commit;",
                iValue, iValue, iValue, iValue));
        return null;
      });
    }

    final AutoCloseableIterator<AirbyteMessage> read2 = source.read(config, configuredCatalog, stateMessage.getState().getData());
    final List<AirbyteMessage> messages2 = new ArrayList<>();
    while (read2.hasNext()) {
      final AirbyteMessage el = read2.next();
      messages2.add(el);
      System.out.println("it said it had next");
      System.out.println("read.next() = " + el);
    }

    assertEquals(11, messages2.size());
  }

}
