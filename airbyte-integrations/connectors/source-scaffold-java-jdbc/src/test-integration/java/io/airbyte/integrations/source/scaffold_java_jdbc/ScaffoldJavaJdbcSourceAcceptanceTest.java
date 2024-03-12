/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.scaffold_java_jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.HashMap;
import org.junit.jupiter.api.Disabled;

@Disabled
public class ScaffoldJavaJdbcSourceAcceptanceTest extends SourceAcceptanceTest {

  private ScaffoldJavaJdbcTestDatabase testdb;

  @Override
  protected void setupEnvironment(final TestDestinationEnv testEnv) {
    // TODO: create new TestDatabase instance and assign `testdb` to it.
    // TODO: use it to create and populate test tables in the database.
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-scaffold-java-jdbc:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    // TODO: (optional) call more builder methods.
    return testdb.integrationTestConfigBuilder().build();
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    // TODO Return the ConfiguredAirbyteCatalog with ConfiguredAirbyteStream objects
    return null;
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
