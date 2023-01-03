/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql_strict_encrypt;

import com.fasterxml.jackson.databind.node.ArrayNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.integrations.destination.mssql.MSSQLDestination;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlStrictEncryptDestination extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlStrictEncryptDestination.class);

  public MssqlStrictEncryptDestination() {
    super(MSSQLDestination.sshWrappedDestination());
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new MssqlStrictEncryptDestination();
    LOGGER.info("starting destination: {}", MssqlStrictEncryptDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MssqlStrictEncryptDestination.class);
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    // Remove the first element in the "ssl_method" array, because it allows users to choose an
    // unencrypted connection.
    ((ArrayNode) spec.getConnectionSpecification().get("properties").get("ssl_method").get("oneOf")).remove(0);
    return spec;
  }

}
