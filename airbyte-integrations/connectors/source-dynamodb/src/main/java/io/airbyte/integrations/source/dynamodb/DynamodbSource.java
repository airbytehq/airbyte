/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.StateDecoratingIterator;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.integrations.source.relationaldb.state.StateManagerFactory;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DynamodbSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(DynamodbSource.class);

  private final FeatureFlags featureFlags = new EnvVariableFeatureFlags();

  private final ObjectMapper objectMapper = new ObjectMapper();

  public static void main(final String[] args) throws Exception {
    final Source source = new DynamodbSource();
    LOGGER.info("starting Source: {}", DynamodbSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed Source: {}", DynamodbSource.class);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final var dynamodbConfig = DynamodbConfig.createDynamodbConfig(config);

    try (final var dynamodbOperations = new DynamodbOperations(dynamodbConfig)) {
      dynamodbOperations.listTables();

      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Error while listing Dynamodb tables with reason: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED);
    }

  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) {

    final var dynamodbConfig = DynamodbConfig.createDynamodbConfig(config);

    try (final var dynamodbOperations = new DynamodbOperations(dynamodbConfig)) {

      final var airbyteStreams = dynamodbOperations.listTables().stream()
          .map(tb -> new AirbyteStream()
              .withName(tb)
              .withJsonSchema(Jsons.jsonNode(ImmutableMap.builder()
                  .put("type", "object")
                  .put("properties", dynamodbOperations.inferSchema(tb, 1000))
                  .build()))
              .withSourceDefinedPrimaryKey(Collections.singletonList(dynamodbOperations.primaryKey(tb)))
              .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))
          .toList();

      return new AirbyteCatalog().withStreams(airbyteStreams);
    }

  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config,
                                                    final ConfiguredAirbyteCatalog catalog,
                                                    final JsonNode state) {

    final var streamState = DynamodbUtils.deserializeStreamState(state, featureFlags.useStreamCapableState());

    final StateManager stateManager = StateManagerFactory
        .createStateManager(streamState.airbyteStateType(), streamState.airbyteStateMessages(), catalog);

    final var dynamodbConfig = DynamodbConfig.createDynamodbConfig(config);

    try (final var dynamodbOperations = new DynamodbOperations(dynamodbConfig)) {

      final var streamIterators = catalog.getStreams().stream()
          .map(str -> switch (str.getSyncMode()) {
          case INCREMENTAL -> scanIncremental(dynamodbOperations, str.getStream(), str.getCursorField().get(0), stateManager);
          case FULL_REFRESH -> scanFullRefresh(dynamodbOperations, str.getStream());
          })
          .toList();

      return AutoCloseableIterators.concatWithEagerClose(streamIterators, AirbyteTraceMessageUtility::emitStreamStatusTrace);

    }
  }

  private AutoCloseableIterator<AirbyteMessage> scanIncremental(final DynamodbOperations dynamodbOperations,
                                                                final AirbyteStream airbyteStream,
                                                                final String cursorField,
                                                                final StateManager stateManager) {

    final var streamPair = new AirbyteStreamNameNamespacePair(airbyteStream.getName(), airbyteStream.getNamespace());

    final Optional<CursorInfo> cursorInfo = stateManager.getCursorInfo(streamPair);

    final Map<String, JsonNode> properties = objectMapper.convertValue(airbyteStream.getJsonSchema().get("properties"), new TypeReference<>() {});
    final Set<String> selectedAttributes = properties.keySet();

    // cursor type will be retrieved from the json schema to save time on db schema crawling reading
    // large amount of items
    final String cursorType = properties.get(cursorField).get("type").asText();

    final var messageStream = cursorInfo.map(cursor -> {

      final var filterType = switch (cursorType) {
        case "string" -> DynamodbOperations.FilterAttribute.FilterType.S;
        case "integer" -> DynamodbOperations.FilterAttribute.FilterType.N;
        case "number" -> {
          final JsonNode airbyteType = properties.get(cursorField).get("airbyte_type");
          if (airbyteType != null && airbyteType.asText().equals("integer")) {
            yield DynamodbOperations.FilterAttribute.FilterType.N;
          } else {
            throw new UnsupportedOperationException("Unsupported attribute type for filtering");
          }
        }
        default -> throw new UnsupportedOperationException("Unsupported attribute type for filtering");
      };

      final DynamodbOperations.FilterAttribute filterAttribute = new DynamodbOperations.FilterAttribute(
          cursor.getCursorField(),
          cursor.getCursor(),
          filterType);

      return dynamodbOperations.scanTable(airbyteStream.getName(), selectedAttributes, filterAttribute);

    })
        // perform full refresh if cursor is not present
        .orElse(dynamodbOperations.scanTable(airbyteStream.getName(), selectedAttributes, null))
        .stream()
        .map(jn -> DynamodbUtils.mapAirbyteMessage(airbyteStream.getName(), jn));

    // wrap stream in state emission iterator
    return AutoCloseableIterators.transform(autoCloseableIterator -> new StateDecoratingIterator(
        autoCloseableIterator,
        stateManager,
        streamPair,
        cursorField,
        cursorInfo.map(CursorInfo::getCursor).orElse(null),
        JsonSchemaPrimitive.valueOf(cursorType.toUpperCase()),
        // emit state after full stream has been processed
        0),
        AutoCloseableIterators.fromStream(messageStream));

  }

  private AutoCloseableIterator<AirbyteMessage> scanFullRefresh(final DynamodbOperations dynamodbOperations,
                                                                final AirbyteStream airbyteStream) {
    final Map<String, JsonNode> properties = objectMapper.convertValue(airbyteStream.getJsonSchema().get("properties"), new TypeReference<>() {});
    final Set<String> selectedAttributes = properties.keySet();

    final var messageStream = dynamodbOperations
        .scanTable(airbyteStream.getName(), selectedAttributes, null)
        .stream()
        .map(jn -> DynamodbUtils.mapAirbyteMessage(airbyteStream.getName(), jn));

    return AutoCloseableIterators.fromStream(messageStream);
  }

}
