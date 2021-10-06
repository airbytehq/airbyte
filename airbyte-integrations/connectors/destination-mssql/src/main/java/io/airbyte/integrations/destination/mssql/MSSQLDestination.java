/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
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
    final Destination destination = new MSSQLDestination();
    LOGGER.info("starting destination: {}", MSSQLDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MSSQLDestination.class);
  }

}
