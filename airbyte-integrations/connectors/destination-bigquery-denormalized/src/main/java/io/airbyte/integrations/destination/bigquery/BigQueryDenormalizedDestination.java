/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.protocol.models.DestinationSyncMode.APPEND;
import static io.airbyte.protocol.models.DestinationSyncMode.OVERWRITE;
import static java.util.Arrays.asList;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDenormalizedDestination extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedDestination.class);

  public BigQueryDenormalizedDestination() {
    super(BigQueryDestination.wrappedDestination(true));
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    spec.setSupportedDestinationSyncModes(asList(APPEND, OVERWRITE));
    spec.setSupportsNormalization(false);
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove("transformation_priority");
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new BigQueryDenormalizedDestination();
    LOGGER.info("starting destination: {}", BigQueryDenormalizedDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", BigQueryDenormalizedDestination.class);
  }

}
