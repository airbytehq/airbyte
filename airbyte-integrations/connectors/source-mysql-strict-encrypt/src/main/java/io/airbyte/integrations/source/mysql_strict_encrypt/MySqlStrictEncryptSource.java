/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql_strict_encrypt;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.integrations.source.mysql.MySqlSource;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Secure-only version of MySQL source that can be used in the Airbyte cloud. This connector
 * inherently prevent certain insecure connections such as connecting to a database over the public
 * internet without encryption.
 */
public class MySqlStrictEncryptSource extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlStrictEncryptSource.class);

  MySqlStrictEncryptSource() {
    super(MySqlSource.sshWrappedSource());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    // SSL property should be enabled by default for secure versions of connectors
    // that can be used in the Airbyte cloud. User should not be able to change this property.
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.SSL_KEY);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new MySqlStrictEncryptSource();
    LOGGER.info("starting source: {}", MySqlStrictEncryptSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MySqlStrictEncryptSource.class);
  }

}
