/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql_strict_encrypt;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.mssql.MsSQLContainerFactory;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.HashMap;
import java.util.Map;

public class MssqlStrictEncryptSourceAcceptanceTest extends SourceAcceptanceTest {

  protected static final String SCHEMA_NAME = "dbo";
  protected static final String STREAM_NAME = "id_and_name";

  private MsSQLTestDatabase testdb;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) {
    final var container = new MsSQLContainerFactory().shared("mcr.microsoft.com/mssql/server:2022-RTM-CU2-ubuntu-20.04");
    testdb = new MsSQLTestDatabase(container);
    testdb = testdb
        .withConnectionProperty("encrypt", "true")
        .withConnectionProperty("trustServerCertificate", "true")
        .withConnectionProperty("databaseName", testdb.getDatabaseName())
        .initialized()
        .with("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));")
        .with("INSERT INTO id_and_name (id, name, born) VALUES " +
            "(1,'picard', '2124-03-04T01:01:01Z'),  " +
            "(2, 'crusher', '2124-03-04T01:01:01Z'), " +
            "(3, 'vash', '2124-03-04T01:01:01Z');");
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mssql-strict-encrypt:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class));
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withSsl(Map.of("ssl_method", "encrypted_trust_server_certificate"))
        .build();
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CatalogHelpers.createConfiguredAirbyteCatalog(
        STREAM_NAME,
        SCHEMA_NAME,
        Field.of("id", JsonSchemaType.NUMBER),
        Field.of("name", JsonSchemaType.STRING),
        Field.of("born", JsonSchemaType.STRING));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
