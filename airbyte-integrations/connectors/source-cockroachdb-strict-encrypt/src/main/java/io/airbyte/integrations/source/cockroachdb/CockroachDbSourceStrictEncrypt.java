/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.cockroachdb;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CockroachDbSourceStrictEncrypt extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(CockroachDbSourceStrictEncrypt.class);

  public CockroachDbSourceStrictEncrypt() {
    super(CockroachDbSource.sshWrappedSource());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) throws Exception {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.SSL_KEY);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new CockroachDbSourceStrictEncrypt();
    LOGGER.info("starting source: {}", CockroachDbSourceStrictEncrypt.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", CockroachDbSourceStrictEncrypt.class);
  }

}
