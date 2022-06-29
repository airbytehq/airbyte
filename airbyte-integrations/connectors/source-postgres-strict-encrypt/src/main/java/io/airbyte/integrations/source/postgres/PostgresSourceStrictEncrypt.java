/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;

/**
 * This file will soon be removed. Any change to this file should also be duplicated to
 * PostgresSourceStrictEncrypt.java in the source-postgres module.
 */
public class PostgresSourceStrictEncrypt extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSourceStrictEncrypt.class);

  PostgresSourceStrictEncrypt() {
    super(PostgresSource.sshWrappedSource());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove("ssl");
    var i = 1;
    List<JsonNode> a = new ArrayList<>();
    while (spec.getConnectionSpecification().get("properties").get("ssl_mode").get("oneOf").has(i)) {
      a.add(spec.getConnectionSpecification().get("properties").get("ssl_mode").get("oneOf").get(i));
      i++;
    }
    ObjectMapper mapper = new ObjectMapper();
    ArrayNode array = mapper.valueToTree(a);
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).remove("oneOf");
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).put("oneOf", array);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new PostgresSourceStrictEncrypt();
    LOGGER.info("starting source: {}", PostgresSourceStrictEncrypt.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSourceStrictEncrypt.class);
  }

}
