/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql_strict_encrypt;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.integrations.source.mysql.MySqlSource;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Secure-only version of MySQL source that can be used in the Airbyte cloud. This connector
 * inherently prevent certain insecure connections such as connecting to a database over the public
 * internet without encryption.
 */
public class MySqlStrictEncryptSource extends SpecModifyingSource implements Source {

  public static final String TUNNEL_METHOD = "tunnel_method";
  public static final String NO_TUNNEL = "NO_TUNNEL";
  public static final String SSL_MODE = "ssl_mode";
  public static final String MODE = "mode";
  public static final String SSL_MODE_PREFERRED = "preferred";

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
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.SSL_KEY);
    return spec;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    // #15808 Disallow connecting to db with disable, prefer or allow SSL mode when connecting directly
    // and not over SSH tunnel
    if (config.has(TUNNEL_METHOD)
        && config.get(TUNNEL_METHOD).has(TUNNEL_METHOD)
        && config.get(TUNNEL_METHOD).get(TUNNEL_METHOD).asText().equals(NO_TUNNEL)) {
      // If no SSH tunnel
      if (config.has(SSL_MODE) && config.get(SSL_MODE).has(MODE)) {
        if (Set.of(SSL_MODE_PREFERRED).contains(config.get(SSL_MODE).get(MODE).asText())) {
          // Fail in case SSL mode is preferred
          return new AirbyteConnectionStatus()
              .withStatus(Status.FAILED)
              .withMessage(
                  "Unsecured connection not allowed. If no SSH Tunnel set up, please use one of the following SSL modes: required, verify-ca, verify-identity");
        }
      }
    }
    return super.check(config);
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new MySqlStrictEncryptSource();
    LOGGER.info("starting source: {}", MySqlStrictEncryptSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MySqlStrictEncryptSource.class);
  }

}
