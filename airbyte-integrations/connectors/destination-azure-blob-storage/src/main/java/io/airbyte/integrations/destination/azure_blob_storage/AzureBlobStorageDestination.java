/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.azure.storage.common.StorageSharedKeyCredential;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.azure_blob_storage.file.AzureUtils;
import io.airbyte.integrations.destination.azure_blob_storage.file.UploaderType;
import io.airbyte.integrations.destination.azure_blob_storage.file.UploadingMethod;
import io.airbyte.integrations.destination.azure_blob_storage.file.config.UploaderConfig;
import io.airbyte.integrations.destination.azure_blob_storage.file.uploader.AbstractAzureUploader;
import io.airbyte.integrations.destination.azure_blob_storage.file.uploader.AzureUploaderFactory;
import io.airbyte.integrations.destination.azure_blob_storage.writer.ProductionWriterFactory;
import io.airbyte.integrations.destination.gcs.GcsDestination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureBlobStorageDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageDestination.class);

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new AzureBlobStorageDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final AzureBlobStorageConnectionChecker client = new AzureBlobStorageConnectionChecker(
          AzureBlobStorageDestinationConfig.getAzureBlobStorageConfig(config));
      final UploadingMethod uploadingMethod = AzureUtils.getLoadingMethod(config);
      final UploaderType uploaderType = AzureUtils.getUploaderType(config);

      // GCS upload time re-uses destination-GCS for check and other uploading (CSV format writer)
      if (UploadingMethod.GCS.equals(uploadingMethod)) {
        final GcsDestination gcsDestination = new GcsDestination();
        final JsonNode gcsJsonNodeConfig = AzureUtils.getStagingJsonConfig(uploadingMethod, uploaderType, config);
        final AirbyteConnectionStatus airbyteConnectionStatus = gcsDestination.check(gcsJsonNodeConfig);
        if (Status.FAILED == airbyteConnectionStatus.getStatus()) {
          return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(airbyteConnectionStatus.getMessage());
        }
      }

      client.attemptWriteAndDelete();
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to access the azure blob storage bucket: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(
              "Could not connect to the azure blob storage with the provided configuration. \n" + e
                  .getMessage());
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog configuredCatalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
          throws IOException {
    final UploadingMethod uploadingMethod = AzureUtils.getLoadingMethod(config);
    final AzureBlobStorageDestinationConfig azureConfig = AzureBlobStorageDestinationConfig.getAzureBlobStorageConfig(config);

    return UploadingMethod.STANDARD.equals(uploadingMethod) ?
            new AzureBlobStorageConsumer(azureConfig, configuredCatalog, new ProductionWriterFactory(), outputRecordCollector) :
            getRecordConsumer(getUploaderMap(config, configuredCatalog), outputRecordCollector);

  }

  /* Helpers */

  protected AirbyteMessageConsumer getRecordConsumer(final Map<AirbyteStreamNameNamespacePair, AbstractAzureUploader<?>> writeConfigs,
                                                     final Consumer<AirbyteMessage> outputRecordCollector) {
    return new AzureFileRecordConsumer(writeConfigs, outputRecordCollector);
  }

  protected Map<AirbyteStreamNameNamespacePair, AbstractAzureUploader<?>> getUploaderMap(final JsonNode config,
                                                                                         final ConfiguredAirbyteCatalog catalog)
          throws IOException {
    final AzureBlobStorageDestinationConfig azureConfig = AzureBlobStorageDestinationConfig.getAzureBlobStorageConfig(config);
    final UploadingMethod uploadingMethod = AzureUtils.getLoadingMethod(config);
    final UploaderType uploaderType = AzureUtils.getUploaderType(config);

    final Map<AirbyteStreamNameNamespacePair, AbstractAzureUploader<?>> uploaderMap = new HashMap<>();
    for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
      final AirbyteStream stream = configStream.getStream();
      final String streamName = stream.getName();

      final StorageSharedKeyCredential credential = new StorageSharedKeyCredential(
              azureConfig.getAccountName(), azureConfig.getAccountKey());
      final SpecializedBlobClientBuilder specializedBlobClientBuilder = new SpecializedBlobClientBuilder()
              .endpoint(azureConfig.getEndpointUrl())
              .credential(credential)
              .containerName(azureConfig.getContainerName());
      final AppendBlobClient appendBlobClient = specializedBlobClientBuilder
              .blobName(streamName)
              .buildAppendBlobClient();
      boolean newlyCreatedBlob = createContainers(appendBlobClient, configStream);

      UploaderConfig uploaderConfig = UploaderConfig
              .builder()
              .configStream(configStream)
              .uploaderType(uploaderType)
              .uploadingMethod(uploadingMethod)
              .newlyCreatedBlob(newlyCreatedBlob)
              .appendBlobClient(appendBlobClient)
              .keepFilesInStorage(AzureUtils.isKeepFilesInStorage(config))
              .stagingConfig(AzureUtils.getStagingJsonConfig(uploadingMethod, uploaderType, config))
              .build();

      uploaderMap.put(
              AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream),
              AzureUploaderFactory.getUploader(uploaderConfig));
    }
    return uploaderMap;
  }

  private boolean createContainers(final AppendBlobClient appendBlobClient,
                                   final ConfiguredAirbyteStream configuredStream) {
    // create container if absent (aka SQl Schema)
    final BlobContainerClient containerClient = appendBlobClient.getContainerClient();
    if (!containerClient.exists()) {
      containerClient.create();
    }
    // create a storage container if absent (aka Table is SQL BD)
    if (DestinationSyncMode.OVERWRITE.equals(configuredStream.getDestinationSyncMode())) {
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

}
