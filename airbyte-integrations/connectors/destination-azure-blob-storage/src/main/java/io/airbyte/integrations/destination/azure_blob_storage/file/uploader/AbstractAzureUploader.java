/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.uploader;

import static io.airbyte.integrations.destination.azure_blob_storage.file.AzureConsts.BUTCH_SIZE;
import static io.airbyte.integrations.destination.azure_blob_storage.file.helpers.LoggerHelper.printHeapMemoryConsumption;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.azure.storage.blob.models.BlobRange;
import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.s3.writer.S3Writer;
import io.airbyte.protocol.models.AirbyteMessage;
import java.io.IOException;
import java.net.URL;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.List;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractAzureUploader<T extends S3Writer> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractAzureUploader.class);

  private final T writer;
  private final long headerByteSize;
  private final boolean keepFilesInStaging;
  private final AppendBlobClient appendBlobClient;

  public AbstractAzureUploader(T writer,
                               boolean keepFilesInStaging,
                               AppendBlobClient appendBlobClient,
                               long headerByteSize) {
    this.writer = writer;
    this.headerByteSize = headerByteSize;
    this.appendBlobClient = appendBlobClient;
    this.keepFilesInStaging = keepFilesInStaging;
  }

  public void postProcessAction() {
    if (!keepFilesInStaging) {
      deleteGcsFiles();
    }
  }

  public void upload(AirbyteMessage airbyteMessage) {
    try {
      writer.write(UUID.randomUUID(), airbyteMessage.getRecord());
    } catch (final IOException | RuntimeException e) {
      LOGGER.error("Got an error while writing message: {}", e.getMessage(), e);
      LOGGER.error(String.format(
          "Failed to process a message for job: \n%s, \nAirbyteMessage: %s",
          writer.toString(),
          airbyteMessage.getRecord()));
      printHeapMemoryConsumption();
      throw new RuntimeException(e);
    }
  }

  public void close(boolean hasFailed, Consumer<AirbyteMessage> outputRecordCollector, AirbyteMessage lastStateMessage) {
    try {
      LOGGER.info("Closing connector:" + this);
      this.writer.close(hasFailed);

      if (!hasFailed) {
        uploadData(outputRecordCollector, lastStateMessage);
      }
      this.postProcessAction();
      LOGGER.info("Closed connector:" + this);
    } catch (final Exception e) {
      LOGGER.error(String.format("Failed to close %s writer, \n details: %s", this, e.getMessage()));
      printHeapMemoryConsumption();
      throw new RuntimeException(e);
    }
  }

  protected abstract AmazonS3 getS3Client();

  protected abstract String getBucketName();

  protected abstract String getBucketPath();

  protected void uploadData(Consumer<AirbyteMessage> outputRecordCollector, AirbyteMessage lastStateMessage) {
    uploadDataFromBlobToStagingFile();
    try {
      outputRecordCollector.accept(lastStateMessage);
      LOGGER.info("Final state message is accepted.");
    } catch (Exception e) {
      LOGGER.error("Upload data is failed!");
      throw e;
    }
  }

  protected void uploadDataFromBlobToStagingFile() {
    final AmazonS3 s3Client = getS3Client();

    final String gcsBucketName = getBucketName();
    long contentLength = s3Client.getObjectMetadata(gcsBucketName, this.writer.getOutputPath()).getContentLength();
    if (contentLength > 0) {
      LocalDateTime date = LocalDateTime.now().plusHours(25);
      Date out = Date.from(date.atZone(ZoneId.systemDefault()).toInstant());
      var url = s3Client.generatePresignedUrl(gcsBucketName, this.writer.getOutputPath(), out);
      long fileSize = s3Client.getObjectMetadata(gcsBucketName, this.writer.getOutputPath()).getContentLength();
      uploadToAzureByButch(url, fileSize);
    }
  }

  private void uploadToAzureByButch(URL url, long fileByteSize) {
    long startTempBytes = headerByteSize;
    var chunk = BUTCH_SIZE;
    if ((startTempBytes + chunk) >= fileByteSize) {
      appendBlobClient.appendBlockFromUrl(url.toString(), new BlobRange(startTempBytes, fileByteSize));
    } else {
      var tempFileByteSize = startTempBytes + chunk;
      while (fileByteSize > tempFileByteSize) {
        appendBlobClient.appendBlockFromUrl(url.toString(), new BlobRange(startTempBytes, chunk));
        startTempBytes = startTempBytes + chunk + 1;
        if (fileByteSize - (tempFileByteSize + 1) < chunk) {
          chunk = fileByteSize - tempFileByteSize;
        }
        tempFileByteSize = tempFileByteSize + chunk + 1;
      }
      appendBlobClient.appendBlockFromUrl(url.toString(), new BlobRange(startTempBytes, chunk - 1));
    }
  }

  private void deleteGcsFiles() {
    final AmazonS3 s3Client = getS3Client();

    final String bucketName = getBucketName();
    final String bucketPath = getBucketPath();

    final List<S3ObjectSummary> objects = s3Client
        .listObjects(bucketName, bucketPath)
        .getObjectSummaries();

    objects.stream().filter(s3ObjectSummary -> s3ObjectSummary.getKey().equals(writer.getOutputPath())).forEach(s3ObjectSummary -> {
      s3Client.deleteObject(bucketName, new DeleteObjectsRequest.KeyVersion(s3ObjectSummary.getKey()).getKey());
      LOGGER.info("File is deleted : " + s3ObjectSummary.getKey());
    });
    s3Client.shutdown();
  }

}
