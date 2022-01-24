/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

public class LegacyInfiniteFeedSourceAcceptanceTest extends SourceAcceptanceTest {

  private JsonNode config;

  @Override
  protected String getImageName() {
    return "airbyte/source-e2e-test:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return this.config;
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) {
    this.config = Jsons.jsonNode(ImmutableMap.builder()
        .put("type", TestingSources.TestingSourceType.INFINITE_FEED)
        .put("max_records", 10)
        .build());
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    // do nothing
  }

  @Override
  protected ConnectorSpecification getSpec() throws IOException {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CatalogHelpers.toDefaultConfiguredCatalog(LegacyConstants.DEFAULT_CATALOG);
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Override
  protected List<String> getRegexTests() {
    return Collections.emptyList();
  }

}
