/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_strict_encrypt;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.integrations.destination.redshift.RedshiftDestination;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftStrictEncryptDestination extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftStrictEncryptDestination.class);

  public RedshiftStrictEncryptDestination() {
    super(new RedshiftDestination());
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new RedshiftStrictEncryptDestination();
    LOGGER.info("starting destination: {}", RedshiftStrictEncryptDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", RedshiftStrictEncryptDestination.class);
  }

  @Override
  public ConnectorSpecification modifySpec(ConnectorSpecification originalSpec) throws Exception {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove("tls");
    return spec;
  }

}
