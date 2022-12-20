/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.node.ArrayNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlSourceStrictEncrypt extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlSourceStrictEncrypt.class);

  public MssqlSourceStrictEncrypt() {
    super(MssqlSource.sshWrappedSource());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) throws Exception {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ArrayNode) spec.getConnectionSpecification().get("properties").get("ssl_method").get("oneOf")).remove(0);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new MssqlSourceStrictEncrypt();
    LOGGER.info("starting source: {}", MssqlSourceStrictEncrypt.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MssqlSourceStrictEncrypt.class);
  }

}
