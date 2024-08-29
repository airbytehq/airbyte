/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import io.airbyte.integrations.destination.teradata.typing_deduping.TeradataDataTransformer;
import io.airbyte.integrations.destination.teradata.typing_deduping.TeradataDestinationHandler;
import io.airbyte.integrations.destination.teradata.typing_deduping.TeradataRawTableAirbyteMetaMigration;
import io.airbyte.integrations.destination.teradata.typing_deduping.TeradataSqlGenerator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
  Main class for hte destination-teradata connector
 */
public class TeradataDestination extends AbstractJdbcDestination<MinimumDestinationState> implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataDestination.class);

  private static final NamingConventionTransformer NAMING_CONVENTION_TRANSFORMER = new StandardNameTransformer();

  /**
   * Teradata JDBC driver
   */
  public static final String DRIVER_CLASS = DatabaseDriver.TERADATA.getDriverClassName();
  /**
   * Default schema name
   */
  protected static final String DEFAULT_SCHEMA_NAME = "def_airbyte_db";
  protected static final String PARAM_MODE = "mode";
  protected static final String PARAM_SSL = "ssl";
  protected static final String PARAM_SSL_MODE = "ssl_mode";
  protected static final String PARAM_SSLMODE = "sslmode";
  protected static final String PARAM_SSLCA = "sslca";
  protected static final String REQUIRE = "require";

  protected static final String VERIFY_CA = "verify-ca";

  protected static final String VERIFY_FULL = "verify-full";

  protected static final String ALLOW = "allow";

  protected static final String CA_CERTIFICATE = "ca.pem";

  protected static final String CA_CERT_KEY = "ssl_ca_certificate";

  protected static final String ENCRYPTDATA = "ENCRYPTDATA";

  protected static final String ENCRYPTDATA_ON = "ON";
  private static final String DROP_CASCADE_OPTION = "drop_cascade";


  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new TeradataDestination()).run(args);
  }

  public TeradataDestination() {
    super(DRIVER_CLASS, new StandardNameTransformer(), new TeradataSqlOperations());
  }

  private static void createCertificateFile(String fileName, String fileValue) throws IOException {
    try (final PrintWriter out = new PrintWriter(fileName, StandardCharsets.UTF_8)) {
      out.print(fileValue);
    }
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    final Map<String, String> additionalParameters = new HashMap<>();
    if (config.has(PARAM_SSL) && config.get(PARAM_SSL).asBoolean()) {
      LOGGER.debug("SSL Enabled");
      if (config.has(PARAM_SSL_MODE)) {
        LOGGER.debug("Selected SSL Mode : " + config.get(PARAM_SSL_MODE).get(PARAM_MODE).asText());
        additionalParameters.putAll(obtainConnectionOptions(config.get(PARAM_SSL_MODE)));
      } else {
        additionalParameters.put(PARAM_SSLMODE, REQUIRE);
      }
    }
    additionalParameters.put(ENCRYPTDATA, ENCRYPTDATA_ON);
    return additionalParameters;
  }

  private Map<String, String> obtainConnectionOptions(final JsonNode encryption) {
    final Map<String, String> additionalParameters = new HashMap<>();
    if (!encryption.isNull()) {
      final var method = encryption.get(PARAM_MODE).asText();
      switch (method) {
        case "verify-ca", "verify-full" -> {
          additionalParameters.put(PARAM_SSLMODE, method);
          try {
            createCertificateFile(CA_CERTIFICATE, encryption.get("ssl_ca_certificate").asText());
          } catch (final IOException ioe) {
            throw new RuntimeException("Failed to create certificate file");
          }
          additionalParameters.put(PARAM_SSLCA, CA_CERTIFICATE);
        }
        default -> {
          additionalParameters.put(PARAM_SSLMODE, method);
        }
      }
    }
    return additionalParameters;
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final String schema = Optional.ofNullable(config.get(JdbcUtils.SCHEMA_KEY)).map(JsonNode::asText).orElse(DEFAULT_SCHEMA_NAME);

    final String jdbcUrl = String.format("jdbc:teradata://%s/",
        config.get(JdbcUtils.HOST_KEY).asText());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl)
        .put(JdbcUtils.SCHEMA_KEY, schema);

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }
    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public boolean isV2Destination() {
    return true;
  }


  @Override
  protected JdbcSqlGenerator getSqlGenerator(final JsonNode config) {
    final JsonNode dropCascadeNode = config.get(DROP_CASCADE_OPTION);
    final boolean dropCascade = dropCascadeNode != null && dropCascadeNode.asBoolean();
    return new TeradataSqlGenerator(new TeradataNameTransformer(), dropCascade);
  }

  @Override
  protected JdbcDestinationHandler<MinimumDestinationState> getDestinationHandler(String databaseName, JdbcDatabase database, String rawTableSchema) {
    return new TeradataDestinationHandler(databaseName, database, rawTableSchema);
  }

  @Override
  protected List<Migration<MinimumDestinationState>> getMigrations(JdbcDatabase database,
                                                         String databaseName,
                                                         SqlGenerator sqlGenerator,
                                                         DestinationHandler<MinimumDestinationState> destinationHandler) {
    return List.of(new TeradataRawTableAirbyteMetaMigration(database, databaseName));
  }

  @Override
  protected StreamAwareDataTransformer getDataTransformer(ParsedCatalog parsedCatalog, String defaultNamespace) {
    return new TeradataDataTransformer();
  }
}
