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
import io.airbyte.integrations.destination.azure_blob_storage.file.formatter.AzureRecordFormatter;
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

public class AzureUploaderFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureUploaderFactory.class);

  public static AbstractAzureUploader<?> getUploader(UploaderConfig uploaderConfig)
      throws IOException {

    final boolean isGcsUploadingMode = UploadingMethod.GCS.equals(uploaderConfig.getUploadingMethod());
    final boolean isCsvUploadingType = UploaderType.CSV.equals(uploaderConfig.getUploaderType());
    var recordFormatter = uploaderConfig.getFormatterMap().get(UploaderType.STANDARD);
    if (isGcsUploadingMode) {
      if (isCsvUploadingType) {
        recordFormatter = uploaderConfig.getFormatterMap().get(UploaderType.CSV);
      } else {
        recordFormatter = uploaderConfig.getFormatterMap().get(UploaderType.JSONL);
      }
    }
    DestinationSyncMode syncMode = uploaderConfig.getConfigStream().getDestinationSyncMode();

    return getGcsUploader(
            syncMode,
            uploaderConfig.getUploaderType(),
            uploaderConfig.getStagingConfig(),
            uploaderConfig.getConfigStream(),
            uploaderConfig.getAppendBlobClient(),
            recordFormatter,
            uploaderConfig.isKeepFilesInStorage());
  }

  private static AbstractGcsAzureUploader<?> getGcsUploader(DestinationSyncMode syncMode,
                                                            UploaderType uploaderType,
                                                            JsonNode stagingConfig,
                                                            ConfiguredAirbyteStream configStream,
                                                            AppendBlobClient appendBlobClient,
                                                            AzureRecordFormatter formatter,
                                                            boolean keepFilesInStorage)
          throws IOException {

    final GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig.getGcsDestinationConfig(stagingConfig);
    AbstractGcsAzureUploader result;
    if (UploaderType.CSV.equals(uploaderType)) {
      GcsCsvWriter gcsWriter = initGcsCsvWriter(gcsDestinationConfig, configStream);
      gcsWriter.initialize();
      result = new GcsCsvAzureUploader(syncMode, gcsWriter, gcsDestinationConfig,
              appendBlobClient, keepFilesInStorage, formatter);
    } else {
      GcsJsonlWriter jsonWriter = initGcsJsonWriter(gcsDestinationConfig, configStream);
      jsonWriter.initialize();
      result = new GcsJsonlAzureUploader(syncMode, jsonWriter, gcsDestinationConfig,
              appendBlobClient, keepFilesInStorage, formatter);
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

}
