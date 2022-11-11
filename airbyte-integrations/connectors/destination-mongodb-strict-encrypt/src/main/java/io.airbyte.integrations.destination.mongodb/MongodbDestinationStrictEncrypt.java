/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongodbDestinationStrictEncrypt extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongodbDestinationStrictEncrypt.class);

  public MongodbDestinationStrictEncrypt() {
    super(new MongodbDestination());
  }

  @Override
  public ConnectorSpecification modifySpec(ConnectorSpecification originalSpec) throws Exception {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    // removing tls property for a standalone instance to disable possibility to switch off a tls
    // connection
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("instance_type").get("oneOf").get(0).get("properties")).remove("tls");
    return spec;
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new MongodbDestinationStrictEncrypt();
    LOGGER.info("starting destination: {}", MongodbDestinationStrictEncrypt.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MongodbDestinationStrictEncrypt.class);
  }

}
