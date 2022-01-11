/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.uploader;

import com.amazonaws.services.s3.AmazonS3;
import com.azure.storage.blob.specialized.AppendBlobClient;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.azure_blob_storage.file.UploaderType;
import io.airbyte.integrations.destination.azure_blob_storage.file.UploadingMethod;
import io.airbyte.integrations.destination.azure_blob_storage.file.config.UploaderConfig;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsS3Helper;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;
import io.airbyte.integrations.destination.gcs.jsonl.GcsJsonlWriter;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.sql.Timestamp;
import java.util.Arrays;

public class AzureUploaderFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureUploaderFactory.class);

  public static AbstractAzureUploader<?> getUploader(UploaderConfig uploaderConfig)
      throws IOException {

    final boolean isGcsUploadingMode = UploadingMethod.GCS.equals(uploaderConfig.getUploadingMethod());

    DestinationSyncMode syncMode = uploaderConfig.getConfigStream().getDestinationSyncMode();

    return getGcsUploader(
            syncMode,
            uploaderConfig.getUploaderType(),
            uploaderConfig.getStagingConfig(),
            uploaderConfig.getConfigStream(),
            uploaderConfig.getAppendBlobClient(),
            uploaderConfig.isKeepFilesInStorage(),
            uploaderConfig.isNewlyCreatedBlob());
  }

  private static AbstractGcsAzureUploader<?> getGcsUploader(DestinationSyncMode syncMode,
                                                            UploaderType uploaderType,
                                                            JsonNode stagingConfig,
                                                            ConfiguredAirbyteStream configStream,
                                                            AppendBlobClient appendBlobClient,
                                                            boolean keepFilesInStorage,
                                                            boolean newlyCreatedBlob)
          throws IOException {

    final GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig.getGcsDestinationConfig(stagingConfig);
    AbstractGcsAzureUploader result;
    int headerByteSize = 0;
    if (UploaderType.CSV.equals(uploaderType)) {
      GcsCsvWriter gcsWriter = initGcsCsvWriter(gcsDestinationConfig, configStream);
      gcsWriter.initialize();
      headerByteSize = calculateHeaderByteSize(newlyCreatedBlob, gcsWriter);
      result = new GcsCsvAzureUploader(syncMode, gcsWriter, gcsDestinationConfig,
              appendBlobClient, keepFilesInStorage, headerByteSize);
    } else {
      GcsJsonlWriter jsonWriter = initGcsJsonWriter(gcsDestinationConfig, configStream);
      jsonWriter.initialize();
      result = new GcsJsonlAzureUploader(syncMode, jsonWriter, gcsDestinationConfig,
              appendBlobClient, keepFilesInStorage, headerByteSize);
    }
    return result;

  }

  private static GcsCsvWriter initGcsCsvWriter(final GcsDestinationConfig gcsDestinationConfig,
                                               final ConfiguredAirbyteStream configuredStream)
      throws IOException {
    final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());

    final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);
    return new GcsCsvWriter(gcsDestinationConfig, s3Client, configuredStream, uploadTimestamp);
  }

  private static GcsJsonlWriter initGcsJsonWriter(final GcsDestinationConfig gcsDestinationConfig,
                                                  final ConfiguredAirbyteStream configuredStream) {
    final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());

    final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);
    return new GcsJsonlWriter(gcsDestinationConfig, s3Client, configuredStream, uploadTimestamp);
  }

  private static int calculateHeaderByteSize(boolean newlyCreatedBlob,
                                      GcsCsvWriter gcsWriter) {
    int headerByteSize = 0;
    if (!newlyCreatedBlob) {
      var headersNames = Arrays.asList(gcsWriter.getHeader());
      for (String header : headersNames) {
        headerByteSize = headerByteSize + header.length();
      }
      headerByteSize = headerByteSize + headersNames.size()*2 + headersNames.size() + 1;
    }
    return headerByteSize;
  }

}
