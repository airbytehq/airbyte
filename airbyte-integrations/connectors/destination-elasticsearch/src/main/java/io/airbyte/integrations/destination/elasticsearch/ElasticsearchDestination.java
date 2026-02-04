/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import static co.elastic.clients.elasticsearch.watcher.Input.HTTP;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.stream.IntStream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ElasticsearchDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ElasticsearchDestination.class);
  private final ObjectMapper mapper = new ObjectMapper();
  private final FeatureFlags featureFlags;

  public ElasticsearchDestination() {
    this(new EnvVariableFeatureFlags());
  }

  ElasticsearchDestination(final FeatureFlags featureFlags) {
    this.featureFlags = featureFlags;
  }

  private boolean cloudDeploymentMode() {
    return AdaptiveSourceRunner.CLOUD_MODE.equalsIgnoreCase(featureFlags.deploymentMode());
  }

  public static void main(String[] args) throws Exception {
    final var destination = sshWrappedDestination();
    LOGGER.info("starting destination: {}", ElasticsearchDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", ElasticsearchDestination.class);
  }

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new ElasticsearchDestination(), "endpoint");
  }

  private static final String NON_SECURE_URL_ERR_MSG = "Server Endpoint requires HTTPS";

  /**
   * When running in cloud deployment mode, remove the "None" authentication option from the spec to
   * enforce authentication. This replaces the need for a separate strict-encrypt connector.
   */
  @Override
  public ConnectorSpecification spec() throws Exception {
    final ConnectorSpecification spec = Jsons.clone(super.spec());
    if (cloudDeploymentMode()) {
      ArrayNode authMethod =
          (ArrayNode) spec.getConnectionSpecification()
              .get("properties")
              .get("authenticationMethod")
              .get("oneOf");
      IntStream.range(0, authMethod.size())
          .filter(i -> authMethod.get(i).get("title").asText().equals("None"))
          .findFirst()
          .ifPresent(authMethod::remove);
    }
    return spec;
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) throws Exception {
    final ConnectorConfiguration configObject = convertConfig(config);
    if (Objects.isNull(configObject.getEndpoint())) {
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("endpoint must not be empty");
    }

    // In cloud deployment mode, require HTTPS for secure connections
    if (cloudDeploymentMode()
        && new URL(configObject.getEndpoint()).getProtocol().equals(HTTP)) {
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage(NON_SECURE_URL_ERR_MSG);
    }

    if (!configObject.getAuthenticationMethod().isValid()) {
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("authentication options are invalid");
    }

    final ElasticsearchConnection connection = new ElasticsearchConnection(configObject);
    final var result = connection.checkConnection();
    try {
      connection.close();
    } catch (IOException e) {
      LOGGER.warn("failed while closing connection", e);
    }
    if (result) {
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } else {
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage("failed to ping elasticsearch");
    }

  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog configuredCatalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {

    final ConnectorConfiguration configObject = convertConfig(config);
    final ElasticsearchConnection connection = new ElasticsearchConnection(configObject);

    final List<ElasticsearchWriteConfig> writeConfigs = new ArrayList<>();
    for (final ConfiguredAirbyteStream stream : configuredCatalog.getStreams()) {
      final String namespace = stream.getStream().getNamespace();
      final String streamName = stream.getStream().getName();
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
      if (syncMode == null) {
        throw new IllegalStateException("Undefined destination sync mode");
      }
      List<List<String>> primaryKey = null;
      if (syncMode != DestinationSyncMode.APPEND) {
        LOGGER.info("not using DestinationSyncMode.APPEND, so using primary key");
        primaryKey = stream.getPrimaryKey();
      }
      LOGGER.info("adding write config. namespace: {}, stream: {}, syncMode: {}", namespace, streamName, syncMode);
      writeConfigs.add(new ElasticsearchWriteConfig()
          .setSyncMode(syncMode)
          .setNamespace(namespace)
          .setStreamName(stream.getStream().getName())
          .setPrimaryKey(primaryKey)
          .setUpsert(configObject.isUpsert()));
    }

    return ElasticsearchAirbyteMessageConsumerFactory.create(outputRecordCollector, connection, writeConfigs, configuredCatalog);
  }

  private ConnectorConfiguration convertConfig(JsonNode config) {
    return mapper.convertValue(config, ConnectorConfiguration.class);
  }

}
