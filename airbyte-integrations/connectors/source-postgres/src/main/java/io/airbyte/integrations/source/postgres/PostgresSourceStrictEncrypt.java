/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is copied from source-postgres-strict-encrypt. The original file can be deleted
 * completely once the migration of multi-variant connector is done.
 */
public class PostgresSourceStrictEncrypt extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSourceStrictEncrypt.class);

  PostgresSourceStrictEncrypt() {
    super(PostgresSource.sshWrappedSource());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.SSL_KEY);
    final ArrayNode modifiedSslModes = spec.getConnectionSpecification().get("properties").get("ssl_mode").get("oneOf").deepCopy();
    // Assume that the first item is the "disable" option; remove it
    modifiedSslModes.remove(0);
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).remove("oneOf");
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).put("oneOf", modifiedSslModes);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new PostgresSourceStrictEncrypt();
    LOGGER.info("starting source: {}", PostgresSourceStrictEncrypt.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSourceStrictEncrypt.class);
  }

}
