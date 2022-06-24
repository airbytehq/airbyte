/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongodbSourceStrictEncrypt extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongodbSourceStrictEncrypt.class);

  public MongodbSourceStrictEncrypt() {
    super(new MongoDbSource());
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
    final Source source = new MongodbSourceStrictEncrypt();
    LOGGER.info("starting source: {}", MongodbSourceStrictEncrypt.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MongodbSourceStrictEncrypt.class);
  }

}
