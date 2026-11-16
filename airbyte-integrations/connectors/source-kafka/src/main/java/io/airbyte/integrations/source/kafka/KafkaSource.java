/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.source.kafka.format.KafkaFormat;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.net.URI;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.security.auth.login.AppConfigurationEntry;
import org.apache.kafka.common.config.SaslConfigs;
import org.apache.kafka.common.config.types.Password;
import org.apache.kafka.common.security.JaasContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KafkaSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(KafkaSource.class);
  private static final Set<String> CLOUD_LOGIN_MODULES = Set.of(
      "org.apache.kafka.common.security.plain.PlainLoginModule",
      "org.apache.kafka.common.security.scram.ScramLoginModule",
      "org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule",
      "com.sun.security.auth.module.Krb5LoginModule",
      "software.amazon.msk.auth.iam.IAMLoginModule");
  private static final String CLOUD_JAAS_ERROR = "Airbyte Cloud requires one supported Kafka SASL JAAS login module. "
      + "Set SASL JAAS Config to use PlainLoginModule, ScramLoginModule, OAuthBearerLoginModule, Krb5LoginModule, or IAMLoginModule.";

  private final FeatureFlags featureFlags;

  public KafkaSource() {
    this(new EnvVariableFeatureFlags());
  }

  KafkaSource(final FeatureFlags featureFlags) {
    this.featureFlags = featureFlags;
  }

  @Override
  public ConnectorSpecification spec() throws Exception {
    final ConnectorSpecification spec = super.spec();
    if (isCloud()) {
      final ArrayNode protocols = (ArrayNode) spec.getConnectionSpecification().get("properties").get("protocol").get("oneOf");
      final Iterator<JsonNode> options = protocols.elements();
      while (options.hasNext()) {
        if (!"SASL_SSL".equals(options.next().path("properties").path("security_protocol").path("const").asText())) {
          options.remove();
        }
      }
    }
    return spec;
  }

  private boolean isCloud() {
    return "CLOUD".equalsIgnoreCase(featureFlags.deploymentMode());
  }

  private void validateCloudSecurity(final JsonNode config) {
    if (!isCloud()) {
      return;
    }
    if (!"SASL_SSL".equalsIgnoreCase(config.path("protocol").path("security_protocol").asText())) {
      throw new ConfigErrorException("Airbyte Cloud requires TLS for Kafka connections. Set Security Protocol to SASL_SSL.");
    }
    final List<AppConfigurationEntry> entries;
    try {
      entries = JaasContext.loadClientContext(Map.of(SaslConfigs.SASL_JAAS_CONFIG,
          new Password(config.path("protocol").path("sasl_jaas_config").asText()))).configurationEntries();
    } catch (final IllegalArgumentException e) {
      throw new ConfigErrorException(CLOUD_JAAS_ERROR);
    }
    if (entries.size() != 1 || !CLOUD_LOGIN_MODULES.contains(entries.get(0).getLoginModuleName())) {
      throw new ConfigErrorException(CLOUD_JAAS_ERROR);
    }
    if ("OAUTHBEARER".equals(config.path("protocol").path("sasl_mechanism").asText())
        && !isHttpsTokenEndpoint(config.path("protocol").path("oauthbearer_token_endpoint_url").asText())) {
      throw new ConfigErrorException(
          "Airbyte Cloud requires an HTTPS OAuth token endpoint. Set OAuth Bearer Token Endpoint URL to a valid HTTPS URL without credentials or a fragment.");
    }
  }

  private static boolean isHttpsTokenEndpoint(final String value) {
    try {
      final URI endpoint = URI.create(value);
      return "https".equalsIgnoreCase(endpoint.getScheme()) && endpoint.getHost() != null
          && endpoint.getRawUserInfo() == null && endpoint.getRawFragment() == null;
    } catch (final IllegalArgumentException e) {
      return false;
    }
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    validateCloudSecurity(config);
    KafkaFormat kafkaFormat = KafkaFormatFactory.getFormat(config);
    if (kafkaFormat.isAccessible()) {
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    }
    return new AirbyteConnectionStatus()
        .withStatus(Status.FAILED)
        .withMessage("Could not connect to the Kafka brokers with provided configuration. \n");
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) {
    validateCloudSecurity(config);
    KafkaFormat kafkaFormat = KafkaFormatFactory.getFormat(config);
    final List<AirbyteStream> streams = kafkaFormat.getStreams();
    return new AirbyteCatalog().withStreams(streams);
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final JsonNode state)
      throws Exception {
    validateCloudSecurity(config);
    final AirbyteConnectionStatus check = check(config);
    if (check.getStatus().equals(AirbyteConnectionStatus.Status.FAILED)) {
      throw new RuntimeException("Unable establish a connection: " + check.getMessage());
    }
    KafkaFormat kafkaFormat = KafkaFormatFactory.getFormat(config);
    return kafkaFormat.read();
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new KafkaSource();
    LOGGER.info("Starting source: {}", KafkaSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("Completed source: {}", KafkaSource.class);
  }

}
