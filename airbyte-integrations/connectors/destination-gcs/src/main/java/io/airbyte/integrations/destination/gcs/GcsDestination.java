/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.transfer.TransferManager;
import com.amazonaws.services.s3.transfer.TransferManagerBuilder;
import com.amazonaws.services.s3.transfer.Upload;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.gcs.writer.GcsWriterFactory;
import io.airbyte.integrations.destination.gcs.writer.ProductionWriterFactory;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.File;
import java.io.FileWriter;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsDestination.class);

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new GcsDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final String fileName = "test";
      final String testContent = "check-content";
      final GcsDestinationConfig destinationConfig = GcsDestinationConfig
          .getGcsDestinationConfig(config);
      final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(destinationConfig);
      LOGGER.info("Started testing if all required credentials assigned to user");
      s3Client.putObject(destinationConfig.getBucketName(), fileName, testContent);
      s3Client.deleteObject(destinationConfig.getBucketName(), fileName);
      LOGGER.info("Finished checking for normal upload, started checking multipart uploading...");

      // Test Multipart Upload permissions
      final TransferManager tm = performTestMultipartUpload(s3Client,
          destinationConfig.getBucketName(), fileName, testContent);
      deleteTestObjectAndShutdownClient(s3Client, destinationConfig.getBucketName(), fileName, tm);

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to access the Gcs bucket: {}", e.getMessage());
      LOGGER.error("Please make sure you account has both \"storage.objects.create\" and \"storage.multipartUploads.create\" roles");
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect to the Gcs bucket with the provided configuration. \n" + e
              .getMessage());
    }
  }

  private TransferManager performTestMultipartUpload(final AmazonS3 s3Client,
                                                     final String bucketName,
                                                     final String fileName,
                                                     final String testContent)
      throws Exception {
    final TransferManager tm = TransferManagerBuilder.standard()
        .withS3Client(s3Client)
        .build();
    // TransferManager processes all transfers asynchronously,
    // so this call returns immediately.
    final File tmpFile = File.createTempFile(fileName, ".tmp");
    try (final FileWriter writer = new FileWriter(tmpFile)) {
      writer.write(testContent);
    }
    // TransferManager processes all transfers asynchronously,
    // so this call returns immediately.
    final Upload upload = tm.upload(bucketName, fileName, tmpFile);
    upload.waitForCompletion();
    LOGGER.info("Object upload complete");
    return tm;
  }

  private void deleteTestObjectAndShutdownClient(final AmazonS3 s3Client,
                                                 final String bucketName,
                                                 final String fileName,
                                                 final TransferManager tm) {
    s3Client.deleteObject(bucketName, fileName);
    LOGGER.info("All checks have passed.");
    tm.shutdownNow(true);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog configuredCatalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final GcsWriterFactory formatterFactory = new ProductionWriterFactory();
    return new GcsConsumer(GcsDestinationConfig.getGcsDestinationConfig(config), configuredCatalog,
        formatterFactory, outputRecordCollector);
  }

}
