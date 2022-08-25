/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql_strict_encrypt;

import com.fasterxml.jackson.databind.node.ArrayNode;
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
  private static final String SSL_MODE_DESCRIPTION = "SSL connection modes. " +
      "<li><b>required</b> - Always connect with SSL. If the MySQL server doesn’t support SSL, the connection will not be established. Certificate Authority (CA) and Hostname are not verified.</li>"
      +
      "<li><b>verify-ca</b> - Always connect with SSL. Verifies CA, but allows connection even if Hostname does not match.</li>" +
      "<li><b>Verify Identity</b> - Always connect with SSL. Verify both CA and Hostname.</li></ul>Read more <a href=\"https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-using-ssl.html\"> in the docs</a>.";

  MySqlStrictEncryptSource() {
    super(MySqlSource.sshWrappedSource());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    // SSL property should be enabled by default for secure versions of connectors
    // that can be used in the Airbyte cloud. User should not be able to change this property.
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.SSL_KEY);
    final ArrayNode modifiedSslModes = spec.getConnectionSpecification().get("properties").get("ssl_mode").get("oneOf").deepCopy();
    // update description for ssl_mode property
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).remove("description");
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).remove("type");
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).remove("order");
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).put("description", SSL_MODE_DESCRIPTION);
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).put("type", "object");
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).put("order", 7);
    // Assume that the first items is the "preferred" option; remove this option
    modifiedSslModes.remove(0);
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).remove("oneOf");
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get("ssl_mode")).put("oneOf", modifiedSslModes);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new MySqlStrictEncryptSource();
    LOGGER.info("starting source: {}", MySqlStrictEncryptSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MySqlStrictEncryptSource.class);
  }

}
