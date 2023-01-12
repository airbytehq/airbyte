/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.integrations.destination.e2e_test.TestingDestinations;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.Iterator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DevNullDestination extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(DevNullDestination.class);
  private static final String DEV_NULL_DESTINATION_TITLE = "E2E Test (/dev/null) Destination Spec";

  public DevNullDestination() {
    super(new TestingDestinations());
  }

  public static void main(final String[] args) throws Exception {
    LOGGER.info("Starting destination: {}", DevNullDestination.class);
    new IntegrationRunner(new DevNullDestination()).run(args);
    LOGGER.info("Completed destination: {}", DevNullDestination.class);
  }

  /**
   * 1. Update the title. 2. Only keep the "silent" mode.
   */
  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);

    ((ObjectNode) spec.getConnectionSpecification()).put("title", DEV_NULL_DESTINATION_TITLE);

    final ArrayNode types = (ArrayNode) spec.getConnectionSpecification().get("oneOf");
    final Iterator<JsonNode> typesIterator = types.elements();
    while (typesIterator.hasNext()) {
      final JsonNode typeNode = typesIterator.next();
      if (!typeNode.get("properties").get("type").get("const").asText().equalsIgnoreCase("silent")) {
        typesIterator.remove();
      }
    }
    return spec;
  }

}
