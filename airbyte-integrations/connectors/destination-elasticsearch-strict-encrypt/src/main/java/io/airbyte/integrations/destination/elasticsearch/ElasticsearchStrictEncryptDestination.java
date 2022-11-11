/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.node.ArrayNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.stream.IntStream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ElasticsearchStrictEncryptDestination extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ElasticsearchStrictEncryptDestination.class);

  public ElasticsearchStrictEncryptDestination() {
    super(new ElasticsearchDestination());
  }

  public static void main(String[] args) throws Exception {
    final var destination = new ElasticsearchStrictEncryptDestination();
    LOGGER.info("starting destination: {}", ElasticsearchStrictEncryptDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", ElasticsearchStrictEncryptDestination.class);
  }

  @Override
  public ConnectorSpecification modifySpec(ConnectorSpecification originalSpec) throws Exception {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ArrayNode authMethod = (ArrayNode) spec.getConnectionSpecification().get("properties").get("authenticationMethod").get("oneOf");
    IntStream.range(0, authMethod.size()).filter(i -> authMethod.get(i).get("title").asText().equals("None")).findFirst()
        .ifPresent(authMethod::remove);
    return spec;
  }

}
