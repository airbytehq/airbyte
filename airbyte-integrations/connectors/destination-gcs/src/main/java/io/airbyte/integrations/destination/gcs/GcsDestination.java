/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import static io.airbyte.integrations.destination.gcs.util.Consts.CHECK_ACTIONS_TMP_FILE_NAME;
import static io.airbyte.integrations.destination.gcs.util.Consts.DUMMY_MIDDLE_SIZE_TEXT;
import static io.airbyte.integrations.destination.gcs.util.Consts.EXPECTED_ROLES;

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
import java.io.IOException;
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
      final GcsDestinationConfig destinationConfig = GcsDestinationConfig
          .getGcsDestinationConfig(config);
      final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(destinationConfig);

      // Test single Upload (for small files) permissions
      testSingleUpload(s3Client, destinationConfig);

      // Test Multipart Upload permissions
      testMultipartUpload(s3Client, destinationConfig);

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to access the Gcs bucket: {}", e.getMessage());
      LOGGER.error("Please make sure you account has all of these roles: " + EXPECTED_ROLES);

      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect to the Gcs bucket with the provided configuration. \n" + e
              .getMessage());
    }
  }

  private void testSingleUpload(final AmazonS3 s3Client, final GcsDestinationConfig destinationConfig){
    LOGGER.info("Started testing if all required credentials assigned to user for single file uploading");
    s3Client.putObject(destinationConfig.getBucketName(), CHECK_ACTIONS_TMP_FILE_NAME, DUMMY_MIDDLE_SIZE_TEXT);
    s3Client.deleteObject(destinationConfig.getBucketName(), CHECK_ACTIONS_TMP_FILE_NAME);
    LOGGER.info("Finished checking for normal upload mode");
  }

  private void testMultipartUpload(final AmazonS3 s3Client, final GcsDestinationConfig destinationConfig)
      throws Exception {

    LOGGER.info("Started testing if all required credentials assigned to user for Multipart upload");
    final TransferManager tm = TransferManagerBuilder.standard()
        .withS3Client(s3Client)
        // Sets the size threshold, in bytes, for when to use multipart uploads. Uploads over this size will
        // automatically use a multipart upload strategy, while uploads smaller than this threshold will use
        // a single connection to upload the whole object. So we need to set it as small for testing connection
        .withMultipartUploadThreshold(1024L) // set 1KB as part size
        .build();

    try{
      // TransferManager processes all transfers asynchronously,
      // so this call returns immediately.
      final Upload upload = tm.upload(destinationConfig.getBucketName(), CHECK_ACTIONS_TMP_FILE_NAME, getTmpFileToUpload());
      upload.waitForCompletion();
      s3Client.deleteObject(destinationConfig.getBucketName(), CHECK_ACTIONS_TMP_FILE_NAME);
    } finally {
      tm.shutdownNow(true);
    }
    LOGGER.info("Finished verification for multipart upload mode");
  }

  private File getTmpFileToUpload() throws IOException {
    final File tmpFile = File.createTempFile(CHECK_ACTIONS_TMP_FILE_NAME, ".tmp");
    try (final FileWriter writer = new FileWriter(tmpFile)) {
      writer.write(DUMMY_MIDDLE_SIZE_TEXT);
    }
    return tmpFile;
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
