/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import io.airbyte.cdk.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.azure_blob_storage.writer.AzureBlobStorageWriter;
import io.airbyte.integrations.destination.azure_blob_storage.writer.AzureBlobStorageWriterFactory;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
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
    // Init the client builder itself here
    final SpecializedBlobClientBuilder specializedBlobClientBuilder =
        AzureBlobStorageDestinationConfig.createSpecializedBlobClientBuilder(azureBlobStorageDestinationConfig);

    for (final ConfiguredAirbyteStream configuredStream : configuredCatalog.getStreams()) {

      StringBuilder blobNameSb = new StringBuilder()
          .append(configuredStream.getStream().getName())
          .append("/")
          .append(getOutputFilename(new Timestamp(System.currentTimeMillis())));

      if (azureBlobStorageDestinationConfig.getFormatConfig().isFileExtensionRequired()) {
        blobNameSb
            .append(".")
            .append(azureBlobStorageDestinationConfig.getFormatConfig().getFormat().getFileExtension());
      }
      String blobName = blobNameSb.toString();

      final AppendBlobClient appendBlobClient = specializedBlobClientBuilder
          .blobName(blobName)
          .buildAppendBlobClient();

      createContainers(specializedBlobClientBuilder, appendBlobClient, configuredStream);

      final AzureBlobStorageWriter writer = writerFactory
          .create(azureBlobStorageDestinationConfig, appendBlobClient, configuredStream);

      final AirbyteStream stream = configuredStream.getStream();
      final AirbyteStreamNameNamespacePair streamNamePair = AirbyteStreamNameNamespacePair
          .fromAirbyteStream(stream);
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
        // Two important notes:
        // 1. There's no option to write to a specific path, so we _always_ write to the root of the
        // container.
        // So the blob name always starts with `<stream_name>/`.
        // 2. We really should include the namespace in the blob name, but we currently don't...
        // So current behavior is that if you have `public1.users` and `public2.users`,
        // those files will probably conflict in some way which is undesired.
        if (!blob.isDeleted() && blob.getName().startsWith(configuredStream.getStream().getName() + "/")) {
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
      LOGGER.error(String.format("Failed to write message for stream %s, details: %s",
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
