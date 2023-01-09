/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.mongodb.MongoUtils;
import io.airbyte.db.mongodb.MongoUtils.MongoInstanceType;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongodbDestinationStrictEncrypt extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongodbDestinationStrictEncrypt.class);

  public MongodbDestinationStrictEncrypt() {
    super(MongodbDestination.sshWrappedDestination());
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    final JsonNode instanceConfig = config.get(MongoUtils.INSTANCE_TYPE);
    final MongoInstanceType instance = MongoInstanceType.fromValue(instanceConfig.get(MongoUtils.INSTANCE).asText());
    // If the MongoDb destination connector is not set up to use a TLS connection, then check should
    // fail
    if (instance.equals(MongoInstanceType.STANDALONE) && !MongoUtils.tlsEnabledForStandaloneInstance(config, instanceConfig)) {
      throw new ConfigErrorException("TLS connection must be used to read from MongoDB.");
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
