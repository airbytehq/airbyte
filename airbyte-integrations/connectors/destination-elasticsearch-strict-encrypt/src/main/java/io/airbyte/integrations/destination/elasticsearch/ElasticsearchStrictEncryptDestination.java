/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import static co.elastic.clients.elasticsearch.watcher.Input.HTTP;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.net.URL;
import java.util.Objects;
import java.util.stream.IntStream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ElasticsearchStrictEncryptDestination extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ElasticsearchStrictEncryptDestination.class);
  private final ObjectMapper mapper = new ObjectMapper();
  private static final String NON_EMPTY_URL_ERR_MSG = "Server Endpoint is a required field";
  private static final String NON_SECURE_URL_ERR_MSG = "Server Endpoint requires HTTPS";

  public ElasticsearchStrictEncryptDestination() {
    super(new ElasticsearchDestination());
  }

  public static void main(String[] args) throws Exception {
    final var destination = new ElasticsearchStrictEncryptDestination();
    LOGGER.info("starting destination: {}", ElasticsearchStrictEncryptDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", ElasticsearchStrictEncryptDestination.class);
  }

  @Override
  public ConnectorSpecification modifySpec(ConnectorSpecification originalSpec) throws Exception {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ArrayNode authMethod = (ArrayNode) spec.getConnectionSpecification().get("properties").get("authenticationMethod").get("oneOf");
    IntStream.range(0, authMethod.size()).filter(i -> authMethod.get(i).get("title").asText().equals("None")).findFirst()
        .ifPresent(authMethod::remove);
    return spec;
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) throws Exception {

    final ConnectorConfiguration configObject = convertConfig(config);
    if (Objects.isNull(configObject.getEndpoint())) {
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage(NON_EMPTY_URL_ERR_MSG);
    }

    if (new URL(configObject.getEndpoint()).getProtocol().equals(HTTP)) {
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage(NON_SECURE_URL_ERR_MSG);
    }

    return super.check(config);
  }

  private ConnectorConfiguration convertConfig(JsonNode config) {
    return mapper.convertValue(config, ConnectorConfiguration.class);
  }

}
