package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.StateDecoratingIterator;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.integrations.source.relationaldb.state.StateManagerFactory;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
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

    public static void main(String[] args) throws Exception {
        Source source = new DynamodbSource();
        LOGGER.info("starting Source: {}", DynamodbSource.class);
        new IntegrationRunner(source).run(args);
        LOGGER.info("completed Source: {}", DynamodbSource.class);
    }

    @Override
    public AirbyteConnectionStatus check(JsonNode config) {
        var dynamodbConfig = DynamodbConfig.initConfigFromJson(config);

        try (var dynamodbOperations = new DynamodbOperations(dynamodbConfig)) {
            dynamodbOperations.listTables();

            return new AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
        } catch (Exception e) {
            LOGGER.error("Error while listing Dynamodb tables with reason: ", e);
            return new AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED);
        }

    }

    @Override
    public AirbyteCatalog discover(JsonNode config) throws Exception {

        var dynamodbConfig = DynamodbConfig.initConfigFromJson(config);

        try (var dynamodbOperations = new DynamodbOperations(dynamodbConfig)) {

            var airbyteStreams = dynamodbOperations.listTables().stream()
                .map(tb -> new AirbyteStream()
                    .withName(tb)
                    .withJsonSchema(dynamodbOperations.inferSchema(tb, 1000))
                    .withSourceDefinedPrimaryKey(Collections.singletonList(dynamodbOperations.primaryKey(tb)))
                    .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH)))
                .toList();

            return new AirbyteCatalog().withStreams(airbyteStreams);
        }

    }

    @Override
    public AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog,
                                                      JsonNode state) {

        var streamState = DynamodbUtils.deserializeStreamState(state, featureFlags.useStreamCapableState());

        StateManager stateManager =
            StateManagerFactory.createStateManager(streamState.airbyteStateType(), streamState.airbyteStateMessages(),
                catalog);

        var dynamodbConfig = DynamodbConfig.initConfigFromJson(config);

        try (var dynamodbOperations = new DynamodbOperations(dynamodbConfig)) {

            var streamIterators = catalog.getStreams().stream()
                .map(str -> switch (str.getSyncMode()) {
                    case INCREMENTAL ->
                        scanIncremental(dynamodbOperations, str.getStream(), str.getCursorField().get(0), stateManager);
                    case FULL_REFRESH -> scanFullRefresh(dynamodbOperations, str.getStream());
                })
                .toList();


            return AutoCloseableIterators.concatWithEagerClose(streamIterators);

        }
    }

    private AutoCloseableIterator<AirbyteMessage> scanIncremental(DynamodbOperations dynamodbOperations,
                                                                  AirbyteStream airbyteStream,
                                                                  String cursorField, StateManager stateManager) {


        var streamPair = new AirbyteStreamNameNamespacePair(airbyteStream.getName(), airbyteStream.getNamespace());

        Optional<CursorInfo> cursorInfo = stateManager.getCursorInfo(streamPair);

        Set<String> properties = Jsons.object(airbyteStream.getJsonSchema().get("properties"), Map.class).keySet();
        String cursorType = airbyteStream.getJsonSchema().get("properties").get(cursorField).get("type").asText();

        var messageStream = cursorInfo.map(cursor -> {

                var filterType = switch (cursorType) {
                    case "string" -> DynamodbOperations.FilterAttribute.FilterType.S;
                    case "integer" -> DynamodbOperations.FilterAttribute.FilterType.N;
                    case "number" -> {
                        JsonNode airbyteType =
                            airbyteStream.getJsonSchema().get("properties").get(cursorField).get("airbyte_type");
                        if (airbyteType != null && airbyteType.asText().equals("integer")) {
                            yield DynamodbOperations.FilterAttribute.FilterType.N;
                        } else {
                            throw new UnsupportedOperationException("Unsupported attribute type for filtering");
                        }
                    }
                    default -> throw new UnsupportedOperationException("Unsupported attribute type for filtering");
                };

                DynamodbOperations.FilterAttribute filterAttribute = new DynamodbOperations.FilterAttribute(
                    cursor.getCursorField(),
                    cursor.getCursor(),
                    filterType
                );

                return dynamodbOperations.scanTable(airbyteStream.getName(), properties, filterAttribute);

            })
            // perform full refresh if cursor is not present
            .orElse(dynamodbOperations.scanTable(airbyteStream.getName(), properties, null))
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
                //emit state after full stream has been processed
                0),
            AutoCloseableIterators.fromStream(messageStream));

    }

    private AutoCloseableIterator<AirbyteMessage> scanFullRefresh(DynamodbOperations dynamodbOperations,
                                                                  AirbyteStream airbyteStream) {
        Set<String> properties = Jsons.object(airbyteStream.getJsonSchema().get("properties"), Map.class).keySet();

        var messageStream = dynamodbOperations.scanTable(airbyteStream.getName(), properties, null).stream()
            .map(jn -> DynamodbUtils.mapAirbyteMessage(airbyteStream.getName(), jn));

        return AutoCloseableIterators.fromStream(messageStream);
    }

}
