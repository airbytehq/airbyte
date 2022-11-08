/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.rockset;

import static io.airbyte.integrations.destination.rockset.RocksetUtils.API_KEY_ID;
import static io.airbyte.integrations.destination.rockset.RocksetUtils.API_SERVER_ID;
import static io.airbyte.integrations.destination.rockset.RocksetUtils.ROCKSET_WORKSPACE_ID;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.rockset.client.ApiClient;
import com.rockset.client.api.DocumentsApi;
import com.rockset.client.model.AddDocumentsRequest;
import com.rockset.client.model.AddDocumentsResponse;
import com.rockset.client.model.DocumentStatus;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RocksetWriteApiConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(RocksetWriteApiConsumer.class);
  private static final ObjectMapper mapper = new ObjectMapper();
  // IO bound tasks, use cached thread pool
  private final ExecutorService exec = Executors.newFixedThreadPool(5);

  private final ScheduledExecutorService schedExec = Executors.newSingleThreadScheduledExecutor();

  private final String apiKey;
  private final String apiServer;
  private final String workspace;

  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;

  // records to be sent per collection
  private final Map<String, List<Object>> records;
  private final RocksetSQLNameTransformer nameTransformer = new RocksetSQLNameTransformer();
  private long lastSentDocumentMicroSeconds = 0L;
  private ApiClient client;

  public RocksetWriteApiConsumer(
                                 JsonNode config,
                                 ConfiguredAirbyteCatalog catalog,
                                 Consumer<AirbyteMessage> outputRecordCollector) {
    this.apiKey = config.get(API_KEY_ID).asText();
    this.apiServer = config.get(API_SERVER_ID).asText();
    this.workspace = config.get(ROCKSET_WORKSPACE_ID).asText();
    this.records = new HashMap<>();

    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
  }

  @Override
  protected void startTracked() throws Exception {
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

    // Schedule sending of records at a fixed rate
    schedExec.scheduleAtFixedRate(this::sendBatches, 0L, 5L, TimeUnit.SECONDS);
  }

  @Override
  protected void acceptTracked(AirbyteMessage message) throws Exception {
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      String cname = nameTransformer.convertStreamName(message.getRecord().getStream());

      Map<String, Object> obj = mapper.convertValue(message.getRecord().getData(), new TypeReference<>() {});
      long current = ChronoUnit.MICROS.between(Instant.EPOCH, Instant.now());

      // ensure a monotonic timestamp on records at microsecond precision.
      while (current <= lastSentDocumentMicroSeconds) {
        current = ChronoUnit.MICROS.between(Instant.EPOCH, Instant.now());
      }
      lastSentDocumentMicroSeconds = current;

      // microsecond precision
      // See https://rockset.com/docs/special-fields/#the-_event_time-field
      obj.put("_event_time", current);
      addRequestToBatch(obj, cname);
    } else if (message.getType() == AirbyteMessage.Type.STATE) {
      this.outputRecordCollector.accept(message);
    }
  }

  @Override
  protected void close(boolean hasFailed) throws Exception {
    // Nothing to do
    LOGGER.info("Shutting down!");
    LOGGER.info("Sending final batch of records if any remain!");
    sendBatches();
    LOGGER.info("Final batch of records sent!");
    LOGGER.info("Shutting down executors");
    this.schedExec.shutdown();
    exec.shutdown();
    LOGGER.info("Executors shut down");
  }

  private void addRequestToBatch(Object document, String cname) {
    synchronized (this.records) {
      List<Object> collectionRecords = this.records.getOrDefault(cname, new ArrayList<>());
      collectionRecords.add(document);
      this.records.put(cname, collectionRecords);
    }
  }

  private void sendBatches() {
    List<Map.Entry<String, AddDocumentsRequest>> requests;
    synchronized (this.records) {
      requests = this.records.entrySet().stream().filter(e -> e.getValue().size() > 0)
          .map((e) -> {
            AddDocumentsRequest adr = new AddDocumentsRequest();
            e.getValue().forEach(adr::addDataItem);
            return Map.entry(e.getKey(), adr);
          }

          ).collect(Collectors.toList());
      this.records.clear();
    }
    List<AddDocumentsResponse> responses;
    responses = requests.stream().map((e) -> Exceptions.toRuntime(() -> new DocumentsApi(client).add(workspace, e.getKey(), e.getValue())))
        .collect(Collectors.toList());

    responses
        .stream()
        .flatMap(d -> d.getData().stream())
        .collect(Collectors.groupingBy(DocumentStatus::getStatus))
        .entrySet()
        .stream()
        .forEach((e) -> LOGGER.info("{} documents added with a status of {}", e.getValue().size(), e.getKey()));
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
