/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.opensearch;

import static io.airbyte.integrations.source.opensearch.typemapper.OpenSearchTypeMapper.formatJSONSchema;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OpenSearchSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(OpenSearchSource.class);
  private final ObjectMapper mapper = new ObjectMapper();

  public static void main(String[] args) throws Exception {
    final var Source = new OpenSearchSource();
    LOGGER.info("starting Source: {}", OpenSearchSource.class);
    new IntegrationRunner(Source).run(args);
    LOGGER.info("completed Source: {}", OpenSearchSource.class);
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

    final OpenSearchConnection connection = new OpenSearchConnection(configObject);
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
  public AirbyteCatalog discover(JsonNode config) throws Exception {
    final ConnectorConfiguration configObject = convertConfig(config);
    final OpenSearchConnection connection = new OpenSearchConnection(configObject);
    final var indices = connection.userIndices();
    final var mappings = connection.getMappings(indices);

    List<AirbyteStream> streams = new ArrayList<>();

    for (var index : indices) {
      JsonNode JSONSchema = mapper.convertValue(mappings.get(index).sourceAsMap(), JsonNode.class);
      JsonNode formattedJSONSchema = formatJSONSchema(JSONSchema);
      AirbyteStream stream = new AirbyteStream();
      stream.setSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
      stream.setName(index);
      stream.setJsonSchema(formattedJSONSchema);
      streams.add(stream);
    }
    try {
      connection.close();
    } catch (IOException e) {
      LOGGER.warn("failed while closing connection", e);
    }
    return new AirbyteCatalog().withStreams(streams);
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) {
    final ConnectorConfiguration configObject = convertConfig(config);
    final OpenSearchConnection connection = new OpenSearchConnection(configObject);
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();

    catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .forEach(stream -> {
          AutoCloseableIterator<JsonNode> data = OpenSearchUtils.getDataIterator(connection, stream);
          AutoCloseableIterator<AirbyteMessage> messageIterator = OpenSearchUtils.getMessageIterator(data, stream.getName());
          iteratorList.add(messageIterator);
        });
    return AutoCloseableIterators
        .appendOnClose(AutoCloseableIterators.concatWithEagerClose(iteratorList), () -> {
          LOGGER.info("Closing server connection.");
          connection.close();
          LOGGER.info("Closed server connection.");
        });
  }

  private ConnectorConfiguration convertConfig(JsonNode config) {
    return mapper.convertValue(config, ConnectorConfiguration.class);
  }

}
