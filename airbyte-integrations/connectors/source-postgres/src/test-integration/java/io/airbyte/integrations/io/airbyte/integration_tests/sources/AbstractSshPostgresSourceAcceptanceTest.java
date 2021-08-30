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

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.SSHTunnel;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import org.jooq.DSLContext;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.SQLDialect;

public abstract class AbstractSshPostgresSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String STREAM_NAME = "public.id_and_name";
  private static final String STREAM_NAME2 = "public.starships";

  private JsonNode config;

  public abstract Path getConfigFilePath();

  // todo (cgardens) - dynamically create data by generating a database with a random name instead of requiring data to already be in place.
  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    final JsonNode secretsConfig = Jsons.deserialize(IOs.readFile(getConfigFilePath()));
    System.out.println("secretsConfig = " + secretsConfig);
    final JsonNode tunnelMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("tunnel_method", secretsConfig.get("tunnel_method").get("tunnel_method"))
        .put("tunnel_host", secretsConfig.get("tunnel_method").get("tunnel_host"))
        .put("tunnel_ssh_port", secretsConfig.get("tunnel_method").get("tunnel_ssh_port"))
        .put("tunnel_username", secretsConfig.get("tunnel_method").get("tunnel_username"))
        .put("tunnel_userpass", Jsons.getOptional(secretsConfig, "tunnel_method", "tunnel_userpass").map(JsonNode::asText).orElse(""))
        .put("tunnel_usersshkey", Jsons.getOptional(secretsConfig, "tunnel_method", "tunnel_usersshkey").map(JsonNode::asText).orElse(""))
        .put("tunnel_db_remote_host", secretsConfig.get("tunnel_method").get("tunnel_db_remote_host"))
        .put("tunnel_db_remote_port", secretsConfig.get("tunnel_method").get("tunnel_db_remote_port"))
        .put("tunnel_localport", secretsConfig.get("tunnel_method").get("tunnel_localport"))
        .build());

    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", secretsConfig.get("host"))
        .put("port", secretsConfig.get("port"))
        .put("username", secretsConfig.get("username"))
        .put("password", secretsConfig.get("password"))
        .put("database", secretsConfig.get("database"))
        .put("tunnel_method", tunnelMethod)
        .put("ssl", false)
        .put("replication_method", replicationMethod)
        .build());

    SSHTunnel.sshWrap(config, () -> {
      final Database database = createDatabaseFromConfig(config);

      database.query(ctx -> {

        // dropAllTablesInPublicSchema(ctx);

        final Result<Record> fetch = ctx.fetch("SELECT *\n"
            + "FROM pg_catalog.pg_tables\n"
            + "WHERE schemaname != 'pg_catalog' AND \n"
            + "    schemaname != 'information_schema';");

        System.out.println("fetch = " + fetch);

        // ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
        // ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'), (2, 'crusher'), (3,
        // 'vash');");
        // ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
        // ctx.fetch("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'), (2, 'defiant'), (3,
        // 'yamato');");
        return null;
      });

      database.close();
    });
  }

  private Database createDatabaseFromConfig(final JsonNode config) {
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

  private void dropAllTablesInPublicSchema(final DSLContext ctx) {
    ctx.execute(""
        + "DO $$ \n"
        + "  DECLARE \n"
        + "    r RECORD;\n"
        + "BEGIN\n"
        + "  FOR r IN \n"
        + "    (\n"
        + "      SELECT table_name \n"
        + "      FROM information_schema.tables \n"
        + "      WHERE public\n"
        + "    ) \n"
        + "  LOOP\n"
        + "     EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.table_name) || ' CASCADE';\n"
        + "  END LOOP;\n"
        + "END $$ ;");
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws SQLException {
    // createDatabaseFromConfig(config).query(ctx -> {
    // dropAllTablesInPublicSchema(ctx);
    // return null;
    // });
    // container.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-postgres:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    final ConnectorSpecification originalSpec = Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
    final ObjectNode propNode = (ObjectNode) originalSpec.getConnectionSpecification().get("properties");
    propNode.set("tunnel_method", Jsons.deserialize(MoreResources.readResource("ssh-tunnel-spec.json")));
    return originalSpec;
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME,
                Field.of("id", JsonSchemaPrimitive.NUMBER),
                Field.of("name", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2,
                Field.of("id", JsonSchemaPrimitive.NUMBER),
                Field.of("name", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected List<String> getRegexTests() {
    return Collections.emptyList();
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
