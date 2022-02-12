/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.gcs.writer.GcsWriterFactory;
import io.airbyte.integrations.destination.gcs.writer.ProductionWriterFactory;
import io.airbyte.integrations.destination.s3.util.S3StreamTransferManagerHelper;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.function.Consumer;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsDestination.class);
  public static final String EXPECTED_ROLES = "storage.multipartUploads.abort, storage.multipartUploads.create, "
      + "storage.objects.create, storage.objects.delete, storage.objects.get, storage.objects.list";

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new GcsDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final GcsDestinationConfig destinationConfig = GcsDestinationConfig
          .getGcsDestinationConfig(config);
      final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(destinationConfig);

      // Test single upload (for small files) permissions
      testSingleUpload(s3Client, destinationConfig);

      // Test multipart upload with stream transfer manager
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

  private void testSingleUpload(final AmazonS3 s3Client, final GcsDestinationConfig destinationConfig) {
    LOGGER.info("Started testing if all required credentials assigned to user for single file uploading");
    final String testFile = "test_" + System.currentTimeMillis();
    s3Client.putObject(destinationConfig.getBucketName(), testFile, "this is a test file");
    s3Client.deleteObject(destinationConfig.getBucketName(), testFile);
    LOGGER.info("Finished checking for normal upload mode");
  }

  private void testMultipartUpload(final AmazonS3 s3Client, final GcsDestinationConfig destinationConfig) throws IOException {
    final String testFile = "test_" + System.currentTimeMillis();
    final StreamTransferManager manager = S3StreamTransferManagerHelper.getDefault(
        destinationConfig.getBucketName(),
        testFile,
        s3Client,
        (long) S3StreamTransferManagerHelper.DEFAULT_PART_SIZE_MB);

    try (final MultiPartOutputStream outputStream = manager.getMultiPartOutputStreams().get(0);
        final CSVPrinter csvPrinter = new CSVPrinter(new PrintWriter(outputStream, true, StandardCharsets.UTF_8), CSVFormat.DEFAULT)) {
      final String oneMegaByteString = "a".repeat(500_000);
      // write a file larger than the 5 MB, which is the default part size, to make sure it is a multipart upload
      for (int i = 0; i < 7; ++i) {
        csvPrinter.printRecord(System.currentTimeMillis(), oneMegaByteString);
      }
    }

    manager.complete();
    s3Client.deleteObject(destinationConfig.getBucketName(), testFile);
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
