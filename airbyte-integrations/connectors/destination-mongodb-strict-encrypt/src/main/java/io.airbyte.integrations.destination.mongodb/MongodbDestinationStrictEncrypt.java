/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.mongodb.MongoUtils.MongoInstanceType;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongodbDestinationStrictEncrypt extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongodbDestinationStrictEncrypt.class);

  public MongodbDestinationStrictEncrypt() {
    super(MongodbDestination.sshWrappedDestination());
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    final JsonNode instanceConfig = config.get(MongoDbDestinationUtils.INSTANCE_TYPE);
    final MongoInstanceType instance = MongoInstanceType.fromValue(instanceConfig.get(MongoDbDestinationUtils.INSTANCE).asText());
    // If the MongoDb destination connector is not set up to use a TLS connection, then check should fail
    if (instance.equals(MongoInstanceType.STANDALONE) && !MongoDbDestinationUtils.tlsEnabledForStandaloneInstance(config, instanceConfig)) {
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("TLS connection must be used to read from MongoDB.");
    }
    return super.check(config);
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) throws Exception {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    // removing tls property for a standalone instance to disable possibility to switch off a tls
    // connection
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("instance_type").get("oneOf").get(0).get("properties")).remove("tls");
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new MongodbDestinationStrictEncrypt();
    LOGGER.info("starting destination: {}", MongodbDestinationStrictEncrypt.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MongodbDestinationStrictEncrypt.class);
  }

}
