/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresDestinationStrictEncrypt extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresDestinationStrictEncrypt.class);
  private static final String PROPERTIES = "properties";
  public static final String TUNNEL_METHOD = "tunnel_method";
  public static final String NO_TUNNEL = "NO_TUNNEL";
  public static final String SSL_MODE = "ssl_mode";
  public static final String MODE = "mode";
  public static final String SSL_MODE_ALLOW = "allow";
  public static final String SSL_MODE_PREFER = "prefer";
  public static final String SSL_MODE_DISABLE = "disable";

  public PostgresDestinationStrictEncrypt() {
    super(PostgresDestination.sshWrappedDestination());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ObjectNode) spec.getConnectionSpecification().get(PROPERTIES)).remove(JdbcUtils.SSL_KEY);
    return spec;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    if (config.has(TUNNEL_METHOD)
        && config.get(TUNNEL_METHOD).has(TUNNEL_METHOD)
        && config.get(TUNNEL_METHOD).get(TUNNEL_METHOD).asText().equals(NO_TUNNEL)) {
      // If no SSH tunnel
      if (config.has(SSL_MODE) && config.get(SSL_MODE).has(MODE)) {
        if (Set.of(SSL_MODE_DISABLE, SSL_MODE_ALLOW, SSL_MODE_PREFER).contains(config.get(SSL_MODE).get(MODE).asText())) {
          // Fail in case SSL mode is disable, allow or prefer
          return new AirbyteConnectionStatus()
              .withStatus(Status.FAILED)
              .withMessage(
                  "Unsecured connection not allowed. If no SSH Tunnel set up, please use one of the following SSL modes: require, verify-ca, verify-full");
        }
      }
    }
    return super.check(config);
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new PostgresDestinationStrictEncrypt();
    LOGGER.info("starting destination: {}", PostgresDestinationStrictEncrypt.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", PostgresDestinationStrictEncrypt.class);
  }

}
