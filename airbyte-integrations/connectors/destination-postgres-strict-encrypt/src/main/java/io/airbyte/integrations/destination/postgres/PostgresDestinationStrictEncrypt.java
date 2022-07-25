/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresDestinationStrictEncrypt extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresDestinationStrictEncrypt.class);
  private static final String PROPERTIES = "properties";
  private static final String ONE_OF_PROPERTY = "oneOf";

  public PostgresDestinationStrictEncrypt() {
    super(PostgresDestination.sshWrappedDestination());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ObjectNode) spec.getConnectionSpecification().get(PROPERTIES)).remove(JdbcUtils.SSL_KEY);
    ArrayNode modifiedSslModes = spec.getConnectionSpecification().get(PROPERTIES).get(JdbcUtils.SSL_MODE_KEY).get(ONE_OF_PROPERTY).deepCopy();
    // Assume that the first item is the "allow" option; remove it
    modifiedSslModes.remove(1);
    // Assume that the first item is the "disable" option; remove it
    modifiedSslModes.remove(0);
    ((ObjectNode) spec.getConnectionSpecification().get(PROPERTIES).get(JdbcUtils.SSL_MODE_KEY)).remove(ONE_OF_PROPERTY);
    ((ObjectNode) spec.getConnectionSpecification().get(PROPERTIES).get(JdbcUtils.SSL_MODE_KEY)).put(ONE_OF_PROPERTY, modifiedSslModes);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new PostgresDestinationStrictEncrypt();
    LOGGER.info("starting destination: {}", PostgresDestinationStrictEncrypt.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", PostgresDestinationStrictEncrypt.class);
  }

}
