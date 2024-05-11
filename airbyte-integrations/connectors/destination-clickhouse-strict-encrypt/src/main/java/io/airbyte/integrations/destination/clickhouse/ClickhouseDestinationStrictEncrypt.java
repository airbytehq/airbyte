/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickhouseDestinationStrictEncrypt extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickhouseDestinationStrictEncrypt.class);

  public ClickhouseDestinationStrictEncrypt() {
    super(ClickhouseDestination.sshWrappedDestination());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.SSL_KEY);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new ClickhouseDestinationStrictEncrypt();
    LOGGER.info("starting destination: {}", ClickhouseDestinationStrictEncrypt.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", ClickhouseDestinationStrictEncrypt.class);
  }

  @Override
  public boolean isV2Destination() {
    return true;
  }

}
