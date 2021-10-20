/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;

public class ElasticsearchDestination extends BaseConnector implements Destination {

    private static final Logger LOGGER = LoggerFactory.getLogger(ElasticsearchDestination.class);
    private final ObjectMapper mapper = new ObjectMapper();


    public static void main(String[] args) throws Exception {
        LOGGER.info("starting destination: {}", ElasticsearchDestination.class);
        new IntegrationRunner(new ElasticsearchDestination()).run(args);
        LOGGER.info("completed destination: {}", ElasticsearchDestination.class);
    }

    @Override
    public AirbyteConnectionStatus check(JsonNode config) {
        final ConnectorConfiguration configObject = convertConfig(config);
        if (Objects.isNull(configObject.getEndpoint())) {
            return new AirbyteConnectionStatus()
                    .withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage("endpoint must not be empty");
        }
        if (configObject.isUsingApiKey() && configObject.isUsingBasicAuth()) {
            return new AirbyteConnectionStatus()
                    .withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage("only one authentication method can be used.");
        }

        final ElasticsearchConnection connection = new ElasticsearchConnection(configObject);

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
            final boolean unsupportedMode = syncMode != DestinationSyncMode.APPEND;
            if (unsupportedMode) {
                LOGGER.warn("upserting records");
            }
            LOGGER.info("adding write config. stream: {}, syncMode: {}", streamName, syncMode);
            writeConfigs.put(stream.getStream().getName(), new ElasticsearchWriteConfig()
                    .setSyncMode(syncMode)
                    .setNamespace(stream.getStream().getNamespace())
                    .setPrimaryKey(stream.getPrimaryKey()));
        }

        return ElasticsearchAirbyteMessageConsumerFactory.create(outputRecordCollector, connection, writeConfigs, configuredCatalog);
    }

    private ConnectorConfiguration convertConfig(JsonNode config) {
        return mapper.convertValue(config, ConnectorConfiguration.class);
    }

}
