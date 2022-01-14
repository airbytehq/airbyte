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
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvWriter;
import io.airbyte.integrations.destination.s3.jsonl.S3JsonlWriter;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.IOException;
import java.sql.Timestamp;
import java.util.Arrays;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureUploaderFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureUploaderFactory.class);

  public static AbstractAzureUploader<?> getUploader(UploaderConfig uploaderConfig) throws IOException {
    final boolean isGcsUploadingMode = UploadingMethod.GCS.equals(uploaderConfig.getUploadingMethod());
    return isGcsUploadingMode ? getGcsUploader(
        uploaderConfig.getUploaderType(),
        uploaderConfig.getStagingConfig(),
        uploaderConfig.getConfigStream(),
        uploaderConfig.getAppendBlobClient(),
        uploaderConfig.isKeepFilesInStorage(),
        uploaderConfig.isNewlyCreatedBlob())
        : getS3Uploader(
            uploaderConfig.getUploaderType(),
            uploaderConfig.getStagingConfig(),
            uploaderConfig.getConfigStream(),
            uploaderConfig.getAppendBlobClient(),
            uploaderConfig.isKeepFilesInStorage(),
            uploaderConfig.isNewlyCreatedBlob());
  }

  private static AbstractGcsAzureUploader<?> getGcsUploader(UploaderType uploaderType,
                                                            JsonNode stagingConfig,
                                                            ConfiguredAirbyteStream configStream,
                                                            AppendBlobClient appendBlobClient,
                                                            boolean keepFilesInStorage,
                                                            boolean newlyCreatedBlob)
      throws IOException {
    final GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig.getGcsDestinationConfig(stagingConfig);
    AbstractGcsAzureUploader result;
    int headerByteSize = 0;
    final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());
    if (UploaderType.CSV.equals(uploaderType)) {
      GcsCsvWriter gcsWriter = initGcsCsvWriter(gcsDestinationConfig, configStream, uploadTimestamp);
      gcsWriter.initialize();
      var headersNames = Arrays.asList(gcsWriter.getHeader());
      headerByteSize = calculateHeaderByteSize(newlyCreatedBlob, headersNames);
      result = new GcsCsvAzureUploader(gcsWriter, gcsDestinationConfig, appendBlobClient, keepFilesInStorage, headerByteSize);
    } else {
      GcsJsonlWriter jsonWriter = initGcsJsonWriter(gcsDestinationConfig, configStream, uploadTimestamp);
      jsonWriter.initialize();
      result = new GcsJsonlAzureUploader(jsonWriter, gcsDestinationConfig, appendBlobClient, keepFilesInStorage, headerByteSize);
    }
    return result;

  }

  private static AbstractS3AzureUploader<?> getS3Uploader(UploaderType uploaderType,
                                                          JsonNode stagingConfig,
                                                          ConfiguredAirbyteStream configStream,
                                                          AppendBlobClient appendBlobClient,
                                                          boolean keepFilesInStorage,
                                                          boolean newlyCreatedBlob)
      throws IOException {
    final S3DestinationConfig s3DestinationConfig = S3DestinationConfig.getS3DestinationConfig(stagingConfig);
    AbstractS3AzureUploader result;
    int headerByteSize = 0;
    final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());
    if (UploaderType.CSV.equals(uploaderType)) {
      S3CsvWriter csvWriter = initS3CsvWriter(s3DestinationConfig, configStream, uploadTimestamp);
      csvWriter.initialize();
      var headersNames = Arrays.asList(csvWriter.getHeader());
      headerByteSize = calculateHeaderByteSize(newlyCreatedBlob, headersNames);
      result = new S3CsvAzureUploader(csvWriter, s3DestinationConfig, appendBlobClient, keepFilesInStorage, headerByteSize);
    } else {
      S3JsonlWriter jsonWriter = initS3JsonWriter(s3DestinationConfig, configStream, uploadTimestamp);
      jsonWriter.initialize();
      result = new S3JsonlAzureUploader(jsonWriter, s3DestinationConfig, appendBlobClient, keepFilesInStorage, headerByteSize);
    }
    return result;

  }

  private static GcsCsvWriter initGcsCsvWriter(final GcsDestinationConfig gcsDestinationConfig,
                                               final ConfiguredAirbyteStream configuredStream,
                                               final Timestamp uploadTimestamp)
      throws IOException {
    final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);
    return new GcsCsvWriter(gcsDestinationConfig, s3Client, configuredStream, uploadTimestamp);
  }

  private static GcsJsonlWriter initGcsJsonWriter(final GcsDestinationConfig gcsDestinationConfig,
                                                  final ConfiguredAirbyteStream configuredStream,
                                                  final Timestamp uploadTimestamp) {
    final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);
    return new GcsJsonlWriter(gcsDestinationConfig, s3Client, configuredStream, uploadTimestamp);
  }

  private static S3CsvWriter initS3CsvWriter(final S3DestinationConfig s3DestinationConfig,
                                             final ConfiguredAirbyteStream configuredStream,
                                             final Timestamp uploadTimestamp)
      throws IOException {
    return new S3CsvWriter.Builder(s3DestinationConfig, s3DestinationConfig.getS3Client(),
        configuredStream, uploadTimestamp).build();
  }

  private static S3JsonlWriter initS3JsonWriter(final S3DestinationConfig s3DestinationConfig,
                                                final ConfiguredAirbyteStream configuredStream,
                                                final Timestamp uploadTimestamp) {
    return new S3JsonlWriter(s3DestinationConfig, s3DestinationConfig.getS3Client(),
        configuredStream, uploadTimestamp);
  }

  private static int calculateHeaderByteSize(boolean newlyCreatedBlob,
                                             List<String> headersNames) {
    int headerByteSize = 0;
    if (!newlyCreatedBlob) {
      for (String header : headersNames) {
        headerByteSize = headerByteSize + header.length();
      }
      headerByteSize = headerByteSize + headersNames.size() * 2 + headersNames.size() + 1;
    }
    return headerByteSize;
  }

}
