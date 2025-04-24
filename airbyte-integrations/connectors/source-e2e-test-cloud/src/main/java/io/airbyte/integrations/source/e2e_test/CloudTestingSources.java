/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.ConnectorSpecification;

/**
 * Since 2.0.0, the cloud version is the same as the OSS version. This connector should be removed.
 */
public class CloudTestingSources extends SpecModifyingSource implements Source {

  private static final String CLOUD_TESTING_SOURCES_TITLE = "Cloud E2E Test Source Spec";

  public CloudTestingSources() {
    super(new TestingSources());
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new CloudTestingSources();
    new IntegrationRunner(source).run(args);
  }

  /**
   * 1. Update the title. 2. Only keep the "continuous feed" mode.
   */
  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final JsonNode continuousFeedMode = getContinuousFeedMode(originalSpec);
    return createSpecWithModesReplacedWith(originalSpec, continuousFeedMode);
  }

  private static ConnectorSpecification createSpecWithModesReplacedWith(final ConnectorSpecification originalSpec, final JsonNode... newModes) {
    final ConnectorSpecification clone = Jsons.clone(originalSpec);
    ((ObjectNode) clone.getConnectionSpecification()).put("title", CLOUD_TESTING_SOURCES_TITLE);
    ((ObjectNode) clone.getConnectionSpecification()).set("oneOf", createArrayNodeWithNewModes(newModes));
    return clone;
  }

  private static ArrayNode createArrayNodeWithNewModes(final JsonNode... newModes) {
    final ArrayNode newOneOfArray = Jsons.arrayNode();

    for (final JsonNode newMode : newModes) {
      newOneOfArray.add(newMode);
    }

    return newOneOfArray;
  }

  private static JsonNode getContinuousFeedMode(final ConnectorSpecification originalSpec) {
    final ArrayNode oneOf = ((ArrayNode) originalSpec.getConnectionSpecification().get("oneOf"));
    for (final JsonNode mode : oneOf) {
      if (mode.get("properties").get("type").get("const").asText().equals("CONTINUOUS_FEED")) {
        return mode;
      }
    }
    return null;
  }

}
