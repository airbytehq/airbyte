/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle_strict_encrypt;

import com.fasterxml.jackson.databind.node.ArrayNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.integrations.destination.oracle.OracleDestination;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleStrictEncryptDestination extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleStrictEncryptDestination.class);

  public OracleStrictEncryptDestination() {
    super(OracleDestination.sshWrappedDestination());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ArrayNode) spec.getConnectionSpecification().get("required")).add("encryption");
    // We need to remove the first item from one Of, which is responsible for connecting to the source
    // without encrypted.
    ((ArrayNode) spec.getConnectionSpecification().get("properties").get("encryption").get("oneOf")).remove(0);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new OracleStrictEncryptDestination();
    LOGGER.info("starting destination: {}", OracleStrictEncryptDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", OracleStrictEncryptDestination.class);
  }

}
