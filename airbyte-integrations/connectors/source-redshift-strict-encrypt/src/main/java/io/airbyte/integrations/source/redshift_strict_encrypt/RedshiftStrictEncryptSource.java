/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift_strict_encrypt;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.integrations.source.redshift.RedshiftSource;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftStrictEncryptSource extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftStrictEncryptSource.class);

  public RedshiftStrictEncryptSource() {
    super(new RedshiftSource());
  }

  public static void main(String[] args) throws Exception {
    final Source source = new RedshiftStrictEncryptSource();
    LOGGER.info("starting source: {}", RedshiftStrictEncryptSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", RedshiftStrictEncryptSource.class);
  }

  @Override
  public ConnectorSpecification modifySpec(ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    // removing tls property to enforce a secure connection by preventing users from switching off tls
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove("tls");
    return spec;
  }

}
