/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
import io.airbyte.protocol.models.SyncMode;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureBlobStorageConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageConsumer.class);

  private final AzureBlobStorageDestinationConfig azureBlobStorageDestinationConfig;
  private final ConfiguredAirbyteCatalog configuredCatalog;
  private final AzureBlobStorageWriterFactory writerFactory;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Map<AirbyteStreamNameNamespacePair, AzureBlobStorageWriter> streamNameAndNamespaceToWriters;

  private AirbyteMessage lastStateMessage = null;

  public AzureBlobStorageConsumer(
                                  AzureBlobStorageDestinationConfig azureBlobStorageDestinationConfig,
                                  ConfiguredAirbyteCatalog configuredCatalog,
                                  AzureBlobStorageWriterFactory writerFactory,
                                  Consumer<AirbyteMessage> outputRecordCollector) {
    this.azureBlobStorageDestinationConfig = azureBlobStorageDestinationConfig;
    this.configuredCatalog = configuredCatalog;
    this.writerFactory = writerFactory;
    this.outputRecordCollector = outputRecordCollector;
    this.streamNameAndNamespaceToWriters = new HashMap<>(configuredCatalog.getStreams().size());
  }

  @Override
  protected void startTracked() throws Exception {
    // Init the client itself here
    StorageSharedKeyCredential credential = new StorageSharedKeyCredential(
        azureBlobStorageDestinationConfig.getAccountName(),
        azureBlobStorageDestinationConfig.getAccountKey());

    SpecializedBlobClientBuilder specializedBlobClientBuilder = new SpecializedBlobClientBuilder()
        .endpoint(azureBlobStorageDestinationConfig.getEndpointUrl())
        .credential(credential)
        .containerName(
            azureBlobStorageDestinationConfig
                .getContainerName());// Like schema (or even oracle user) in DB

    for (ConfiguredAirbyteStream configuredStream : configuredCatalog.getStreams()) {

      AppendBlobClient appendBlobClient = specializedBlobClientBuilder
          .blobName(configuredStream.getStream().getName())
          .buildAppendBlobClient();

      boolean isNewlyCreatedBlob = createContainers(appendBlobClient, configuredStream);

      AzureBlobStorageWriter writer = writerFactory
          .create(azureBlobStorageDestinationConfig, appendBlobClient, configuredStream,
              isNewlyCreatedBlob);

      AirbyteStream stream = configuredStream.getStream();
      AirbyteStreamNameNamespacePair streamNamePair = AirbyteStreamNameNamespacePair
          .fromAirbyteSteam(stream);
      streamNameAndNamespaceToWriters.put(streamNamePair, writer);
    }
  }

  private boolean createContainers(AppendBlobClient appendBlobClient,
                                   ConfiguredAirbyteStream configuredStream) {
    // create container if absent (aka SQl Schema)
    final BlobContainerClient containerClient = appendBlobClient.getContainerClient();
    if (!containerClient.exists()) {
      containerClient.create();
    }
    // create a storage container if absent (aka Table is SQL BD)
    if (SyncMode.FULL_REFRESH.equals(configuredStream.getSyncMode())) {
      // full refresh sync. Create blob and override if any
      LOGGER.info("Sync mode is selected to OVERRIDE mode. New container will be automatically"
          + " created or all data would be overridden (if any) for stream:" + configuredStream
              .getStream().getName());
      appendBlobClient.create(true);
      return true;
    } else {
      // incremental sync. Create new container only if still absent
      if (!appendBlobClient.exists()) {
        LOGGER.info("Sync mode is selected to APPEND mode. New container will be automatically"
            + " created for stream:" + configuredStream.getStream().getName());
        appendBlobClient.create(false);
        LOGGER.info(appendBlobClient.getBlobName() + " blob has been created");
        return true;
      } else {
        LOGGER.info(String.format(
            "Sync mode is selected to APPEND mode. Container %s already exists. Append mode is "
                + "only available for \"Append blobs\". For more details please visit"
                + " https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction#blobs",
            configuredStream.getStream().getName()));
        LOGGER.info(appendBlobClient.getBlobName() + " already exists");
        return false;
      }
    }
  }

  @Override
  protected void acceptTracked(AirbyteMessage airbyteMessage) throws Exception {
    if (airbyteMessage.getType() == Type.STATE) {
      this.lastStateMessage = airbyteMessage;
      return;
    } else if (airbyteMessage.getType() != Type.RECORD) {
      return;
    }

    AirbyteRecordMessage recordMessage = airbyteMessage.getRecord();
    AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair
        .fromRecordMessage(recordMessage);

    if (!streamNameAndNamespaceToWriters.containsKey(pair)) {
      String errMsg = String.format(
          "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
          Jsons.serialize(configuredCatalog), Jsons.serialize(recordMessage));
      LOGGER.error(errMsg);
      throw new IllegalArgumentException(errMsg);
    }

    try {
      streamNameAndNamespaceToWriters.get(pair).write(UUID.randomUUID(), recordMessage);

    } catch (Exception e) {
      LOGGER.error(String.format("Failed to write messagefor stream %s, details: %s",
          streamNameAndNamespaceToWriters.get(pair), e.getMessage()));
      throw new RuntimeException(e);
    }
  }

  @Override
  protected void close(boolean hasFailed) throws Exception {
    for (AzureBlobStorageWriter handler : streamNameAndNamespaceToWriters.values()) {
      handler.close(hasFailed);
    }

    if (!hasFailed) {
      outputRecordCollector.accept(lastStateMessage);
    }
  }

}
