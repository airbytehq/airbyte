/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.integrations.util.HostPortResolver;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.testcontainers.containers.MSSQLServerContainer;
import org.testcontainers.utility.DockerImageName;

public class MSSQLDestinationAcceptanceTestSSL extends JdbcDestinationAcceptanceTest {

  private static MSSQLServerContainer<?> db;
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();
  private JsonNode configWithoutDbName;
  private JsonNode config;
  private DSLContext dslContext;

  @Override
  protected String getImageName() {
    return "airbyte/destination-mssql:dev";
  }

  private JsonNode getConfig(final MSSQLServerContainer<?> db) {

    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(db))
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(db))
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.SCHEMA_KEY, "test_schema")
        .put("ssl_method", Jsons.jsonNode(ImmutableMap.of("ssl_method", "encrypted_trust_server_certificate")))
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
        .map(r -> r.get(JavaBaseConstants.COLUMN_NAME_DATA))
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
    // Temporarily disabling the behavior of the ExtendedNameTransformer, see (issue #1785) so we don't
    // use quoted names
    // if (!tableName.startsWith("\"")) {
    // // Currently, Normalization always quote tables identifiers
    // //tableName = "\"" + tableName + "\"";
    // }
    return retrieveRecordsFromTable(tableName, namespace);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    final DSLContext dslContext = DatabaseConnectionHelper.createDslContext(db, SQLDialect.DEFAULT);
    return new Database(dslContext).query(
        ctx -> {
          ctx.fetch(String.format("USE %s;", config.get(JdbcUtils.DATABASE_KEY)));
          return ctx
              .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
              .stream()
              .map(this::getJsonFromRecord)
              .collect(Collectors.toList());
        });
  }

  @BeforeAll
  protected static void init() {
    db = new MSSQLServerContainer<>(DockerImageName.parse("airbyte/mssql_ssltest:dev").asCompatibleSubstituteFor("mcr.microsoft.com/mssql/server"))
        .acceptLicense();
    db.start();
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

  // how to interact with the mssql test container manually.
  // 1. exec into mssql container (not the test container container)
  // 2. /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P "A_Str0ng_Required_Password"
  @Override
  protected void setup(final TestDestinationEnv testEnv) throws SQLException {
    configWithoutDbName = getConfig(db);
    final String dbName = Strings.addRandomSuffix("db", "_", 10);
    dslContext = getDslContext(configWithoutDbName);
    final Database database = getDatabase(dslContext);
    database.query(ctx -> {
      ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
      ctx.fetch(String.format("USE %s;", dbName));
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER NOT NULL, name VARCHAR(200), born DATETIMEOFFSET(7));");
      ctx.fetch(
          "INSERT INTO id_and_name (id, name, born) VALUES (1,'picard', '2124-03-04T01:01:01Z'),  (2, 'crusher', '2124-03-04T01:01:01Z'), (3, 'vash', '2124-03-04T01:01:01Z');");
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

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new MSSQLTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

}
