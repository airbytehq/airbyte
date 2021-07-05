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

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlSource.class);

  static final String DRIVER_CLASS = "com.microsoft.sqlserver.jdbc.SQLServerDriver";

  public MssqlSource() {
    super(DRIVER_CLASS, new MssqlJdbcStreamingQueryConfiguration());
  }

  @Override
  public JsonNode toDatabaseConfig(JsonNode mssqlConfig) {
    List<String> additionalParameters = new ArrayList<>();

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:sqlserver://%s:%s;databaseName=%s;",
        mssqlConfig.get("host").asText(),
        mssqlConfig.get("port").asText(),
        mssqlConfig.get("database").asText()));

    if (mssqlConfig.has("ssl_method")) {
      readSsl(mssqlConfig, additionalParameters);
    }

    if (!additionalParameters.isEmpty()) {
      jdbcUrl.append(String.join(";", additionalParameters));
    }

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", mssqlConfig.get("username").asText())
        .put("password", mssqlConfig.get("password").asText())
        .put("jdbc_url", jdbcUrl.toString())
        .build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "INFORMATION_SCHEMA",
        "sys",
        "spt_fallback_db",
        "spt_monitor",
        "spt_values",
        "spt_fallback_usg",
        "MSreplication_options",
        "spt_fallback_dev");
  }

  private void readSsl(JsonNode sslMethod, List<String> additionalParameters) {
    JsonNode config = sslMethod.get("ssl_method");
    switch (config.get("ssl_method").asText()) {
      case "unencrypted" -> additionalParameters.add("encrypt=false");
      case "encrypted_trust_server_certificate" -> {
        additionalParameters.add("encrypt=true");
        additionalParameters.add("trustServerCertificate=true");
      }
      case "encrypted_verify_certificate" -> {
        additionalParameters.add("encrypt=true");

        // trust store location code found at https://stackoverflow.com/a/56570588
        String trustStoreLocation = Optional.ofNullable(System.getProperty("javax.net.ssl.trustStore"))
            .orElseGet(() -> System.getProperty("java.home") + "/lib/security/cacerts");
        File trustStoreFile = new File(trustStoreLocation);
        if (!trustStoreFile.exists()) {
          throw new RuntimeException(
              "Unable to locate the Java TrustStore: the system property javax.net.ssl.trustStore is undefined or "
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
      }
    }
  }

  public static void main(String[] args) throws Exception {
    final Source source = new MssqlSource();
    LOGGER.info("starting source: {}", MssqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MssqlSource.class);
  }

}
