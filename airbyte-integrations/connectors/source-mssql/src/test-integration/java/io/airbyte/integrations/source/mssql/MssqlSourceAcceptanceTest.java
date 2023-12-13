/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.sql.SQLException;
import java.util.HashMap;

public class MssqlSourceAcceptanceTest extends SourceAcceptanceTest {

  protected static final String SCHEMA_NAME = "dbo";
  protected static final String STREAM_NAME = "id_and_name";

  protected MsSQLTestDatabase testdb;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws SQLException {
    testdb = MsSQLTestDatabase.in("mcr.microsoft.com/mssql/server:2022-RTM-CU2-ubuntu-20.04")
        .with("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));")
        .with("INSERT INTO id_and_name (id, name, born) VALUES " +
            "(1, 'picard', '2124-03-04T01:01:01Z'), " +
            "(2, 'crusher', '2124-03-04T01:01:01Z'), " +
            "(3, 'vash', '2124-03-04T01:01:01Z');");
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mssql:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return SshHelpers.getSpecAndInjectSsh();
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withoutSsl()
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
