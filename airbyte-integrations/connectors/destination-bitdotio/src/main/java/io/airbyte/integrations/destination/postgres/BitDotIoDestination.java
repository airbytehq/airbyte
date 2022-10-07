/* * Copyright (c) 2022 Airbyte, Inc., all rights reserved.  */
package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode ;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.integrations.destination.postgres.PostgresDestination;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.net.URI;
import java.net.URISyntaxException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BitDotIoDestination extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BitDotIoDestination.class);
  
  public BitDotIoDestination() {
    super(new PostgresDestination());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    String json = "[ \"database\", \"username\", \"password\"]  ";

    ObjectMapper objectMapper = new ObjectMapper();
    
    JsonNode jsonNode;
    try {
      jsonNode = objectMapper.readTree(json);
      spec.setDocumentationUrl(new URI("https://docs.airbyte.io/integrations/destinations/bitdotio"));
      ((ObjectNode) spec.getConnectionSpecification()).replace("required", jsonNode);
      ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.PORT_LIST_KEY);
      ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.SSL_KEY);
      ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.HOST_KEY);
      ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.PORT_KEY);
      ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.JDBC_URL_PARAMS_KEY);
      ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.SSL_MODE_KEY);
      ((ObjectNode) spec.getConnectionSpecification().get("properties")).put(JdbcUtils.SSL_KEY, "true");
      ((ObjectNode) spec.getConnectionSpecification().get("properties")).put(JdbcUtils.HOST_KEY, "db.bit.io");
      ((ObjectNode) spec.getConnectionSpecification().get("properties")).put(JdbcUtils.SSL_MODE_KEY, "require");
      ((ObjectNode) spec.getConnectionSpecification().get("properties")).put(JdbcUtils.PORT_KEY, "5432");
    } catch (JsonProcessingException e) {
      e.printStackTrace();
    } catch (URISyntaxException e) {
      // This should never happen.
      e.printStackTrace();
    }

    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new BitDotIoDestination();
    LOGGER.info("starting destination: {}", BitDotIoDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", BitDotIoDestination.class);
  }

}
