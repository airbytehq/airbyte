/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.sql.JDBCType;
import java.util.function.Function;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

public class MssqlStrictEncryptJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private static MSSQLServerContainer<?> dbContainer;
  private static DataSource dataSource;
  private JsonNode config;

  @BeforeAll
  static void init() {
    dbContainer = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-latest").acceptLicense();
    dbContainer.start();
  }

  @BeforeEach
  public void setup() throws Exception {
    final JsonNode configWithoutDbName = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", dbContainer.getHost())
        .put("port", dbContainer.getFirstMappedPort())
        .put("username", dbContainer.getUsername())
        .put("password", dbContainer.getPassword())
        .build());

    dataSource =  DataSourceFactory.create(
        configWithoutDbName.get("username").asText(),
        configWithoutDbName.get("password").asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%d",
            configWithoutDbName.get("host").asText(),
            configWithoutDbName.get("port").asInt())
    );

    try {
      database = new DefaultJdbcDatabase(dataSource);

      final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

      database.execute(ctx -> ctx.createStatement().execute(String.format("CREATE DATABASE %s;", dbName)));

      config = Jsons.clone(configWithoutDbName);
      ((ObjectNode) config).put("database", dbName);

      super.setup();
    } finally {
      DataSourceFactory.close(dataSource);
    }
  }

  @AfterAll
  public static void cleanUp() throws Exception {
    dbContainer.close();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public Function<JsonNode, JsonNode> getToDatabaseConfigFunction() {
    return new MssqlSource()::toDatabaseConfig;
  }

  @Override
  public String getDriverClass() {
    return MssqlSource.DRIVER_CLASS;
  }

  @Override
  public AbstractJdbcSource<JDBCType> getJdbcSource() {
    return null;
  }

  @Override
  public Source getSource() {
    return new MssqlSourceStrictEncrypt();
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source.spec();
    final ConnectorSpecification expected =
        SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class));

    assertEquals(expected, actual);
  }

}
