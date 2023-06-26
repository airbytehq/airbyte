/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql_strict_encrypt;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

public class MssqlStrictEncryptDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static MSSQLServerContainer<?> db;
  private final StandardNameTransformer namingResolver = new StandardNameTransformer();
  private JsonNode config;
  private DSLContext dslContext;

  @BeforeAll
  protected static void init() {
    db = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-GA-ubuntu-16.04").acceptLicense();
    db.start();
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-mssql-strict-encrypt:dev";
  }

  private JsonNode getConfig(final MSSQLServerContainer<?> db) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.DATABASE_KEY, "test")
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.SCHEMA_KEY, "test_schema")
        .build());
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, "wrong password")
        .put(JdbcUtils.DATABASE_KEY, "test")
        .put(JdbcUtils.SCHEMA_KEY, "public")
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put(JdbcUtils.SSL_KEY, false)
        .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
    final List<String> result = new ArrayList<>();
    final String resolved = namingResolver.getIdentifier(identifier);
    result.add(identifier);
    result.add(resolved);
    if (!resolved.startsWith("\"")) {
      result.add(resolved.toLowerCase());
      result.add(resolved.toUpperCase());
    }
    return result;
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    final DSLContext dslContext = DatabaseConnectionHelper.createDslContext(db, null);
    return new Database(dslContext).query(
        ctx -> {
          ctx.fetch(String.format("USE %s;", config.get(JdbcUtils.DATABASE_KEY)));
          return ctx
              .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
              .stream()
              .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
              .map(Jsons::deserialize)
              .collect(Collectors.toList());
        });
  }

  private static DSLContext getDslContext(final JsonNode config) {
    return DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%d",
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt()),
        null);
  }

  private static Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws SQLException {
    final JsonNode configWithoutDbName = getConfig(db);
    final String dbName = Strings.addRandomSuffix("db", "_", 10);
    dslContext = getDslContext(configWithoutDbName);
    final Database database = getDatabase(dslContext);
    database.query(ctx -> {
      ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
      ctx.fetch(String.format("USE %s;", dbName));
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER NOT NULL, name VARCHAR(200), born DATETIMEOFFSET(7));");
      ctx.fetch("INSERT INTO id_and_name (id, name, born) VALUES (1,'picard', '2124-03-04T01:01:01Z'), " +
          " (2, 'crusher', '2124-03-04T01:01:01Z'), (3, 'vash', '2124-03-04T01:01:01Z');");
      return null;
    });

    config = Jsons.clone(configWithoutDbName);
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, dbName);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    dslContext.close();
  }

  @AfterAll
  static void cleanUp() {
    db.stop();
    db.close();
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = new MssqlStrictEncryptDestination().spec();
    final ConnectorSpecification expected =
        SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class));
    assertEquals(expected, actual);
  }

}
