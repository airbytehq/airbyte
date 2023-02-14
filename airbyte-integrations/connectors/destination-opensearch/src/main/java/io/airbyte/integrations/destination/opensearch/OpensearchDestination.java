/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.opensearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OpensearchDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(OpensearchDestination.class);
  private final ObjectMapper mapper = new ObjectMapper();

  public static void main(String[] args) throws Exception {
    final var destination = sshWrappedDestination();
    LOGGER.info("starting destination: {}", OpensearchDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", OpensearchDestination.class);
  }

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new OpensearchDestination(), "endpoint");
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    final ConnectorConfiguration configObject = convertConfig(config);
    if (Objects.isNull(configObject.getEndpoint())) {
      return new AirbyteConnectionStatus()
              .withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage("endpoint must not be empty");
    }
    if (!configObject.getAuthenticationMethod().isValid()) {
      return new AirbyteConnectionStatus()
              .withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage("authentication options are invalid");
    }

    final OpensearchConnection connection = new OpensearchConnection(configObject);
    final var result = connection.checkConnection();
    try {
      connection.close();
    } catch (IOException e) {
      LOGGER.warn("failed while closing connection", e);
    }
    if (result) {
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } else {
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage("failed to ping opensearch");
    }

  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog configuredCatalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {

    final ConnectorConfiguration configObject = convertConfig(config);
    final OpensearchConnection connection = new OpensearchConnection(configObject);

    final List<OpensearchWriteConfig> writeConfigs = new ArrayList<>();
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
      writeConfigs.add(new OpensearchWriteConfig()
              .setSyncMode(syncMode)
              .setNamespace(namespace)
              .setStreamName(stream.getStream().getName())
              .setPrimaryKey(primaryKey)
              .setUpsert(configObject.isUpsert()));
    }

    return OpensearchAirbyteMessageConsumerFactory.create(outputRecordCollector, connection, writeConfigs, configuredCatalog);
  }

  private ConnectorConfiguration convertConfig(JsonNode config) {
    return mapper.convertValue(config, ConnectorConfiguration.class);
  }

}
