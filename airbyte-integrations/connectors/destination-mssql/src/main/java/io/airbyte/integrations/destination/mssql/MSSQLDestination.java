/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MSSQLDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MSSQLDestination.class);

  public static final String DRIVER_CLASS = "com.microsoft.sqlserver.jdbc.SQLServerDriver";
  public static final List<String> HOST_KEY = List.of("host");
  public static final List<String> PORT_KEY = List.of("port");

  public MSSQLDestination() {
    super(DRIVER_CLASS, new MSSQLNameTransformer(), new SqlServerOperations());
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
    final String schema = Optional.ofNullable(config.get("schema")).map(JsonNode::asText).orElse("public");

    List<String> additionalParameters = new ArrayList<>();

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:sqlserver://%s:%s;databaseName=%s;",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));

    if (config.has("ssl_method")) {
      readSsl(config, additionalParameters);
    }

    if (!additionalParameters.isEmpty()) {
      jdbcUrl.append(String.join(";", additionalParameters));
    }

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("jdbc_url", jdbcUrl.toString())
        .put("username", config.get("username").asText())
        .put("password", config.get("password").asText())
        .put("schema", schema);

    return Jsons.jsonNode(configBuilder.build());
  }

  private void readSsl(JsonNode config, List<String> additionalParameters) {
    switch (config.get("ssl_method").asText()) {
      case "unencrypted":
        additionalParameters.add("encrypt=false");
        break;
      case "encrypted_trust_server_certificate":
        additionalParameters.add("encrypt=true");
        additionalParameters.add("trustServerCertificate=true");
        break;
      case "encrypted_verify_certificate":
        additionalParameters.add("encrypt=true");

        // trust store location code found at https://stackoverflow.com/a/56570588
        String trustStoreLocation = Optional.ofNullable(System.getProperty("javax.net.ssl.trustStore"))
            .orElseGet(() -> System.getProperty("java.home") + "/lib/security/cacerts");
        File trustStoreFile = new File(trustStoreLocation);
        if (!trustStoreFile.exists()) {
          throw new RuntimeException("Unable to locate the Java TrustStore: the system property javax.net.ssl.trustStore is undefined or "
              + trustStoreLocation + " does not exist.");
        }
        String trustStorePassword = System.getProperty("javax.net.ssl.trustStorePassword");

        additionalParameters.add("trustStore=" + trustStoreLocation);
        if (trustStorePassword != null && !trustStorePassword.isEmpty()) {
          additionalParameters.add("trustStorePassword=" + config.get("trustStorePassword").asText());
        }
        if (config.has("hostNameInCertificate")) {
          additionalParameters.add("hostNameInCertificate=" + config.get("hostNameInCertificate").asText());
        }
        break;
    }
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new SshWrappedDestination(new MSSQLDestination(), HOST_KEY, PORT_KEY);
    LOGGER.info("starting destination: {}", MSSQLDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MSSQLDestination.class);
  }

}
