/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2_strict_encrypt;

import com.fasterxml.jackson.databind.node.ArrayNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.integrations.source.db2.Db2Source;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Db2StrictEncryptSource extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(Db2StrictEncryptSource.class);
  public static final String DRIVER_CLASS = Db2Source.DRIVER_CLASS;

  public Db2StrictEncryptSource() {
    super(new Db2Source());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    // We need to remove the first item from one Of, which is responsible for connecting to the source
    // without encrypted.
    ((ArrayNode) spec.getConnectionSpecification().get("properties").get("encryption").get("oneOf")).remove(0);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new Db2StrictEncryptSource();
    LOGGER.info("starting source: {}", Db2StrictEncryptSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", Db2StrictEncryptSource.class);
  }

}
