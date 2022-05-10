/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle_strict_encrypt;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.io.Closeable;
import java.util.HashMap;
import java.util.List;
import javax.sql.DataSource;

public class OracleStrictEncryptSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String STREAM_NAME = "JDBC_SPACE.ID_AND_NAME";
  private static final String STREAM_NAME2 = "JDBC_SPACE.STARSHIPS";

  protected OracleContainer container;
  protected JsonNode config;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    container = new OracleContainer()
        .withUsername("test")
        .withPassword("oracle")
        .usingSid();;
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("sid", container.getSid())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("schemas", List.of("JDBC_SPACE"))
        .put("encryption", Jsons.jsonNode(ImmutableMap.builder()
            .put("encryption_method", "client_nne")
            .put("encryption_algorithm", "3DES168")
            .build()))
        .build());

    final DataSource dataSource = DataSourceFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.ORACLE.getDriverClassName(),
        String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("sid").asText()),
        JdbcUtils.parseJdbcParameters("oracle.net.encryption_client=REQUIRED;" +
            "oracle.net.encryption_types_client=( 3DES168 )", ";")
    );

    final JdbcDatabase database = new DefaultJdbcDatabase(dataSource);

    database.execute(connection -> {
      connection.createStatement().execute("CREATE USER JDBC_SPACE IDENTIFIED BY JDBC_SPACE DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS");
      connection.createStatement().execute("CREATE TABLE jdbc_space.id_and_name(id NUMERIC(20, 10), name VARCHAR(200), power BINARY_DOUBLE)");
      connection.createStatement().execute("INSERT INTO jdbc_space.id_and_name (id, name, power) VALUES (1,'goku', BINARY_DOUBLE_INFINITY)");
      connection.createStatement().execute("INSERT INTO jdbc_space.id_and_name (id, name, power) VALUES (2, 'vegeta', 9000.1)");
      connection.createStatement().execute("INSERT INTO jdbc_space.id_and_name (id, name, power) VALUES (NULL, 'piccolo', -BINARY_DOUBLE_INFINITY)");
      connection.createStatement().execute("CREATE TABLE jdbc_space.starships(id INTEGER, name VARCHAR(200))");
      connection.createStatement().execute("INSERT INTO jdbc_space.starships (id, name) VALUES (1,'enterprise-d')");
      connection.createStatement().execute("INSERT INTO jdbc_space.starships (id, name) VALUES (2, 'defiant')");
      connection.createStatement().execute("INSERT INTO jdbc_space.starships (id, name) VALUES (3, 'yamato')");
    });

    if(dataSource instanceof Closeable closeable) {
      closeable.close();
    }
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    container.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-oracle-strict-encrypt:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class));
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
            .withCursorField(Lists.newArrayList("ID"))
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME,
                Field.of("ID", JsonSchemaType.NUMBER),
                Field.of("NAME", JsonSchemaType.STRING),
                Field.of("POWER", JsonSchemaType.NUMBER))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("ID"))
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2,
                Field.of("ID", JsonSchemaType.NUMBER),
                Field.of("NAME", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
