/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.Iterator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CloudTestingSources extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(CloudTestingSources.class);
  private static final String CLOUD_TESTING_SOURCES_TITLE = "Cloud E2E Test Source Spec";

  public CloudTestingSources() {
    super(new TestingSources());
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new CloudTestingSources();
    LOGGER.info("Starting source: {}", CloudTestingSources.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("Completed source: {}", CloudTestingSources.class);
  }

  /**
   * 1. Update the title. 2. Only keep the "continuous feed" mode.
   */
  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);

    ((ObjectNode) spec.getConnectionSpecification()).put("title", CLOUD_TESTING_SOURCES_TITLE);

    final ArrayNode types = (ArrayNode) spec.getConnectionSpecification().get("oneOf");
    final Iterator<JsonNode> typesIterator = types.elements();
    while (typesIterator.hasNext()) {
      final JsonNode typeNode = typesIterator.next();
      if (!typeNode.get("properties").get("type").get("const").asText().equalsIgnoreCase("CONTINUOUS_FEED")) {
        typesIterator.remove();
      }
    }
    return spec;
  }

}
