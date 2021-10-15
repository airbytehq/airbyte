/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.protocol.models.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Consumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ElasticsearchDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ElasticsearchDestination.class);
  private final ObjectMapper mapper = new ObjectMapper();
  private static final StandardNameTransformer namingResolver = new StandardNameTransformer();


  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new ElasticsearchDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    final ConnectorConfiguration configObject = convertConfig(config);
    if (Objects.isNull(configObject.getHost())) {
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage("host must not be empty");
    }
    if (configObject.getPort() == 0) {
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage("port must be set");
    }

    final ElasticsearchConnection connection = new ElasticsearchConnection(configObject);
    //return connection.check();

    if (connection.ping()) {
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

    final Map<String, ElasticsearchWriteConfig> writeConfigs = new HashMap<>();
    for (final ConfiguredAirbyteStream stream : configuredCatalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
      if (syncMode == null) {
        throw new IllegalStateException("Undefined destination sync mode");
      }
      final boolean isAppendMode = syncMode != DestinationSyncMode.OVERWRITE;
      if (isAppendMode) {
        // TODO
      }
      LOGGER.info("adding write config. stream: {}, syncMode: {}", streamName, syncMode);
      writeConfigs.put(stream.getStream().getName(), new ElasticsearchWriteConfig()
              .setSyncMode(syncMode).setNamespace(stream.getStream().getNamespace()));
    }

    return ElasticsearchAirbyteMessageConsumerFactory.create(outputRecordCollector, connection, writeConfigs, configuredCatalog);
  }

  private ConnectorConfiguration convertConfig(JsonNode config) {
    return mapper.convertValue(config, ConnectorConfiguration.class);
  }

}
