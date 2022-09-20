/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.azure.storage.common.StorageSharedKeyCredential;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.azure_blob_storage.writer.AzureBlobStorageWriter;
import io.airbyte.integrations.destination.azure_blob_storage.writer.AzureBlobStorageWriterFactory;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.Timestamp;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.HashMap;
import java.util.Map;
import java.util.TimeZone;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureBlobStorageConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageConsumer.class);
  private static final String YYYY_MM_DD_FORMAT_STRING = "yyyy_MM_dd";

  private final AzureBlobStorageDestinationConfig azureBlobStorageDestinationConfig;
  private final ConfiguredAirbyteCatalog configuredCatalog;
  private final AzureBlobStorageWriterFactory writerFactory;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Map<AirbyteStreamNameNamespacePair, AzureBlobStorageWriter> streamNameAndNamespaceToWriters;

  public AzureBlobStorageConsumer(
                                  final AzureBlobStorageDestinationConfig azureBlobStorageDestinationConfig,
                                  final ConfiguredAirbyteCatalog configuredCatalog,
                                  final AzureBlobStorageWriterFactory writerFactory,
                                  final Consumer<AirbyteMessage> outputRecordCollector) {
    this.azureBlobStorageDestinationConfig = azureBlobStorageDestinationConfig;
    this.configuredCatalog = configuredCatalog;
    this.writerFactory = writerFactory;
    this.outputRecordCollector = outputRecordCollector;
    this.streamNameAndNamespaceToWriters = new HashMap<>(configuredCatalog.getStreams().size());
  }

  @Override
  protected void startTracked() throws Exception {
    // Init the client itself here
    final StorageSharedKeyCredential credential = new StorageSharedKeyCredential(
        azureBlobStorageDestinationConfig.getAccountName(),
        azureBlobStorageDestinationConfig.getAccountKey());

    final SpecializedBlobClientBuilder specializedBlobClientBuilder = new SpecializedBlobClientBuilder()
        .endpoint(azureBlobStorageDestinationConfig.getEndpointUrl())
        .credential(credential)
        .containerName(
            azureBlobStorageDestinationConfig
                .getContainerName());// Like schema (or even oracle user) in DB

    for (final ConfiguredAirbyteStream configuredStream : configuredCatalog.getStreams()) {

      final String blobName = configuredStream.getStream().getName() + "/" +
          getOutputFilename(new Timestamp(System.currentTimeMillis()));
      final AppendBlobClient appendBlobClient = specializedBlobClientBuilder
          .blobName(blobName)
          .buildAppendBlobClient();

      createContainers(specializedBlobClientBuilder, appendBlobClient, configuredStream);

      final AzureBlobStorageWriter writer = writerFactory
          .create(azureBlobStorageDestinationConfig, appendBlobClient, configuredStream);

      final AirbyteStream stream = configuredStream.getStream();
      final AirbyteStreamNameNamespacePair streamNamePair = AirbyteStreamNameNamespacePair
          .fromAirbyteSteam(stream);
      streamNameAndNamespaceToWriters.put(streamNamePair, writer);
    }
  }

  private void createContainers(final SpecializedBlobClientBuilder specializedBlobClientBuilder,
                                final AppendBlobClient appendBlobClient,
                                final ConfiguredAirbyteStream configuredStream) {
    // create container if absent (aka SQl Schema)
    final BlobContainerClient containerClient = appendBlobClient.getContainerClient();
    if (!containerClient.exists()) {
      containerClient.create();
    }
    if (DestinationSyncMode.OVERWRITE.equals(configuredStream.getDestinationSyncMode())) {
      LOGGER.info("Sync mode is selected to OVERRIDE mode. New container will be automatically"
          + " created or all data would be overridden (if any) for stream:" + configuredStream
              .getStream().getName());
      var blobItemList = StreamSupport.stream(containerClient.listBlobs().spliterator(), false)
          .collect(Collectors.toList());
      blobItemList.forEach(blob -> {
        if (!blob.isDeleted() && blob.getName().contains(configuredStream.getStream().getName() + "/")) {
          final AppendBlobClient abc = specializedBlobClientBuilder
              .blobName(blob.getName())
              .buildAppendBlobClient();
          abc.delete();
        }
      });
    }
    appendBlobClient.create(true);
  }

  @Override
  protected void acceptTracked(final AirbyteMessage airbyteMessage) throws Exception {
    if (airbyteMessage.getType() == Type.STATE) {
      outputRecordCollector.accept(airbyteMessage);
      return;
    } else if (airbyteMessage.getType() != Type.RECORD) {
      return;
    }

    final AirbyteRecordMessage recordMessage = airbyteMessage.getRecord();
    final AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair
        .fromRecordMessage(recordMessage);

    if (!streamNameAndNamespaceToWriters.containsKey(pair)) {
      final String errMsg = String.format(
          "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
          Jsons.serialize(configuredCatalog), Jsons.serialize(recordMessage));
      LOGGER.error(errMsg);
      throw new IllegalArgumentException(errMsg);
    }

    try {
      streamNameAndNamespaceToWriters.get(pair).write(UUID.randomUUID(), recordMessage);

    } catch (final Exception e) {
      LOGGER.error(String.format("Failed to write messagefor stream %s, details: %s",
          streamNameAndNamespaceToWriters.get(pair), e.getMessage()));
      throw new RuntimeException(e);
    }
  }

  @Override
  protected void close(final boolean hasFailed) throws Exception {
    for (final AzureBlobStorageWriter handler : streamNameAndNamespaceToWriters.values()) {
      handler.close(hasFailed);
    }
  }

  private static String getOutputFilename(final Timestamp timestamp) {
    final DateFormat formatter = new SimpleDateFormat(YYYY_MM_DD_FORMAT_STRING);
    formatter.setTimeZone(TimeZone.getTimeZone("UTC"));
    return String.format(
        "%s_%d_0",
        formatter.format(timestamp),
        timestamp.getTime());
  }

}
