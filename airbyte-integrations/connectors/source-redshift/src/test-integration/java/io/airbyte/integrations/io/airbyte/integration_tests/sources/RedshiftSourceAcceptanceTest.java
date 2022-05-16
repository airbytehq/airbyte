/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.redshift.RedshiftSource;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;

public class RedshiftSourceAcceptanceTest extends SourceAcceptanceTest {

  protected static final List<Field> FIELDS = List.of(
      Field.of("c_custkey", JsonSchemaType.NUMBER),
      Field.of("c_name", JsonSchemaType.STRING),
      Field.of("c_nation", JsonSchemaType.STRING));

  // This test case expects an active redshift cluster that is useable from outside of vpc
  protected ObjectNode config;
  protected JdbcDatabase database;
  protected String testUserName;
  protected String testUserPassword;
  protected String schemaName;
  protected String schemaToIgnore;
  protected String streamName;

  protected static ObjectNode getStaticConfig() {
    return (ObjectNode) Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    config = getStaticConfig();

    database = createDatabase(config);
    testUserName = "foo";
    testUserPassword = "BarBarBar1&";
    createTestUser(database, config, testUserName, testUserPassword);
    schemaName = Strings.addRandomSuffix("integration_test", "_", 5).toLowerCase();
    schemaToIgnore = schemaName + "shouldIgnore";
    streamName = "customer";

    // limit the connection to one schema only
    config = config.set("schemas", Jsons.jsonNode(List.of(schemaName)));

    // use test user user
    config = config.set("username", Jsons.jsonNode(testUserName));
    config = config.set("password", Jsons.jsonNode(testUserPassword));

    // create a test data
    createTestData(database, schemaName, streamName, testUserName, true);
    createTestData(database, schemaName, "not_readable", testUserName, false);

    // create a schema with data that will not be used for testing, but would be used to check schema
    // filtering. This one should not be visible in results
    createTestData(database, schemaToIgnore, streamName, testUserName, true);
  }

  protected JdbcDatabase createDatabase(final JsonNode config) {
    return new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get("username").asText(),
            config.get("password").asText(),
            RedshiftSource.DRIVER_CLASS,
            String.format(DatabaseDriver.REDSHIFT.getUrlFormatString(),
                config.get("host").asText(),
                config.get("port").asInt(),
                config.get("database").asText())
        )
    );
  }

  protected void createTestUser(final JdbcDatabase database, final JsonNode config, final String testUserName, final String testUserPassword)
      throws SQLException {
    final String createTestUserQuery = String.format("CREATE USER %s PASSWORD '%s'", testUserName, testUserPassword);
    database.execute(connection -> {
      connection.createStatement().execute(createTestUserQuery);
    });
    final String grantSelectOnPgTablesQuery = String.format("GRANT SELECT ON TABLE pg_tables TO %s ", testUserName);
    database.execute(connection -> {
      connection.createStatement().execute(grantSelectOnPgTablesQuery);
    });
  }

  protected void createTestData(final JdbcDatabase database,
                                final String schemaName,
                                final String tableName,
                                final String testUserName,
                                final Boolean isReadableByTestUser)
      throws SQLException {
    final String createSchemaQuery = String.format("CREATE SCHEMA IF NOT EXISTS %s", schemaName);
    database.execute(connection -> {
      connection.createStatement().execute(createSchemaQuery);
    });

    final String fqTableName = JdbcUtils.getFullyQualifiedTableName(schemaName, tableName);
    final String createTestTable =
        String.format(
            "CREATE TABLE IF NOT EXISTS %s (c_custkey INTEGER, c_name VARCHAR(16), c_nation VARCHAR(16));\n",
            fqTableName);
    database.execute(connection -> {
      connection.createStatement().execute(createTestTable);
    });

    final String insertTestData = String.format("insert into %s values (1, 'Chris', 'France');\n",
        fqTableName);
    database.execute(connection -> {
      connection.createStatement().execute(insertTestData);
    });

    if (!isReadableByTestUser) {
      final String revokeSelect = String.format("REVOKE SELECT ON TABLE %s FROM %s;\n", fqTableName, testUserName);
      database.execute(connection -> {
        connection.createStatement().execute(revokeSelect);
      });
    } else {
      final String grantUsageQuery = String.format("GRANT USAGE ON SCHEMA %s TO %s;\n", schemaName, testUserName);
      database.execute(connection -> {
        connection.createStatement().execute(grantUsageQuery);
      });
      final String grantSelectQuery = String.format("GRANT SELECT ON TABLE %s TO %s;\n", fqTableName, testUserName);
      database.execute(connection -> {
        connection.createStatement().execute(grantSelectQuery);
      });
    }
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws SQLException {
    database.execute(connection -> connection.createStatement()
        .execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE", schemaName)));
    database.execute(connection -> connection.createStatement()
        .execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE", schemaToIgnore)));
    database.execute(connection -> connection.createStatement()
        .execute(String.format("REVOKE SELECT ON table pg_tables FROM %s", testUserName)));
    database.execute(connection -> connection.createStatement()
        .execute(String.format("DROP USER IF EXISTS %s", testUserName)));
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-redshift:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CatalogHelpers.createConfiguredAirbyteCatalog(streamName, schemaName, FIELDS);
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Override
  protected void verifyCatalog(final AirbyteCatalog catalog) {
    final List<AirbyteStream> streams = catalog.getStreams();
    // only one stream is expected; the schema that should be ignored
    // must not be included in the retrieved catalog
    assertEquals(1, streams.size());
    final AirbyteStream actualStream = streams.get(0);
    assertEquals(schemaName, actualStream.getNamespace());
    assertEquals(streamName, actualStream.getName());
    assertEquals(CatalogHelpers.fieldsToJsonSchema(FIELDS), actualStream.getJsonSchema());
  }

}
