/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle_strict_encrypt;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.integrations.source.oracle.OracleSource;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleStrictEncryptSource extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleStrictEncryptSource.class);

  public static final String ENCRYPTION_PARAMETERS = "\"encryption_method\"=\"client_nne\", " +
          "\"encryption_algorithm\"=\"3DES168\"";

  OracleStrictEncryptSource() {
    super(OracleSource.sshWrappedSource());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove("encryption");
    //((ObjectNode) spec.getConnectionSpecification().get("properties")).put("encryption", ENCRYPTION_PARAMETERS);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new OracleStrictEncryptSource();
    LOGGER.info("starting source: {}", OracleStrictEncryptSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", OracleStrictEncryptSource.class);
  }

}
