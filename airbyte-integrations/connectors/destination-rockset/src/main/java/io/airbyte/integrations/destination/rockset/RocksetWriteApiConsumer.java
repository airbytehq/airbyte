/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.rockset;

import static io.airbyte.integrations.destination.rockset.RocksetUtils.*;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.rockset.client.ApiClient;
import com.rockset.client.api.DocumentsApi;
import com.rockset.client.model.AddDocumentsRequest;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.DestinationSyncMode;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RocksetWriteApiConsumer implements AirbyteMessageConsumer {

    private static final Logger LOGGER = LoggerFactory.getLogger(RocksetWriteApiConsumer.class);
    private static final ObjectMapper mapper = new ObjectMapper();
    // IO bound tasks, use cached thread pool
    private static final ExecutorService exec = Executors.newCachedThreadPool();

    private final String apiKey;
    private final String apiServer;
    private final String workspace;

    private final ConfiguredAirbyteCatalog catalog;
    private final Consumer<AirbyteMessage> outputRecordCollector;

    private final RocksetSQLNameTransformer nameTransformer = new RocksetSQLNameTransformer();

    private ApiClient client;

    public RocksetWriteApiConsumer(
            JsonNode config,
            ConfiguredAirbyteCatalog catalog,
            Consumer<AirbyteMessage> outputRecordCollector) {
        this.apiKey = config.get(API_KEY_ID).asText();
        this.apiServer = config.get(API_SERVER_ID).asText();
        this.workspace = config.get(ROCKSET_WORKSPACE_ID).asText();

        this.catalog = catalog;
        this.outputRecordCollector = outputRecordCollector;
    }

    @Override
    public void start() throws Exception {
        this.client = RocksetUtils.apiClient(apiKey, apiServer);
        LOGGER.info("Creating workspace");

        RocksetUtils.createWorkspaceIfNotExists(client, workspace);

        CompletableFuture<?>[] overwrittenStreams = catalog.getStreams()
                .stream()
                .filter(s -> s.getDestinationSyncMode() == DestinationSyncMode.OVERWRITE)
                .map(s -> s.getStream().getName())
                .map(nameTransformer::convertStreamName)
                .map(this::emptyCollection)
                .collect(Collectors.toList())
                .toArray(CompletableFuture[]::new);

        CompletableFuture<?>[] appendStreams = catalog.getStreams().stream()
                .filter(s -> s.getDestinationSyncMode() == DestinationSyncMode.APPEND)
                .map(s -> s.getStream().getName())
                .map(nameTransformer::convertStreamName)
                .map(this::createCollectionIntoReadyState)
                .collect(Collectors.toList())
                .toArray(CompletableFuture[]::new);

        CompletableFuture<?> initStreams = CompletableFuture.allOf(
                CompletableFuture.allOf(overwrittenStreams),
                CompletableFuture.allOf(appendStreams));

        // Creating and readying many collections at once can be slow
        initStreams.get(30, TimeUnit.MINUTES);
    }

    @Override
    public void accept(AirbyteMessage message) throws Exception {
        if (message.getType() == AirbyteMessage.Type.RECORD) {
            String cname = nameTransformer.convertStreamName(message.getRecord().getStream());

            AddDocumentsRequest req = new AddDocumentsRequest();
            req.addDataItem(mapper.convertValue(message.getRecord().getData(), new TypeReference<>() {
            }));

            new DocumentsApi(this.client).add(workspace, cname, req);
        } else if (message.getType() == AirbyteMessage.Type.STATE) {
            this.outputRecordCollector.accept(message);
        }
    }

    @Override
    public void close() throws Exception {
        // Nothing to do
    }

    private CompletableFuture<Void> emptyCollection(String cname) {
        return CompletableFuture.runAsync(() -> {
            RocksetUtils.clearCollectionIfCollectionExists(client, workspace, cname);
            RocksetUtils.createCollectionIfNotExists(client, workspace, cname);
            RocksetUtils.waitUntilCollectionReady(client, workspace, cname);
        }, exec);
    }

    private CompletableFuture<Void> createCollectionIntoReadyState(String cname) {
        return CompletableFuture.runAsync(() -> {
            RocksetUtils.createCollectionIfNotExists(client, workspace, cname);
            RocksetUtils.waitUntilCollectionReady(client, workspace, cname);
        }, exec);
    }


}
