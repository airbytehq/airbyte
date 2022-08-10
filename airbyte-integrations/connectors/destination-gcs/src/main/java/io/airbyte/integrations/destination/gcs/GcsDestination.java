/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.S3ConsumerFactory;
import io.airbyte.integrations.destination.s3.S3Destination;
import io.airbyte.integrations.destination.s3.SerializedBufferFactory;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsDestination.class);
  public static final String EXPECTED_ROLES = "storage.multipartUploads.abort, storage.multipartUploads.create, "
      + "storage.objects.create, storage.objects.delete, storage.objects.get, storage.objects.list";

  private final NamingConventionTransformer nameTransformer;

  public GcsDestination() {
    this.nameTransformer = new GcsNameTransformer();
  }

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new GcsDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final GcsDestinationConfig destinationConfig = GcsDestinationConfig.getGcsDestinationConfig(config);
      final AmazonS3 s3Client = destinationConfig.getS3Client();

      // Test single upload (for small files) permissions
      S3Destination.testSingleUpload(s3Client, destinationConfig.getBucketName(), destinationConfig.getBucketPath());

      // Test multipart upload with stream transfer manager
      S3Destination.testMultipartUpload(s3Client, destinationConfig.getBucketName(), destinationConfig.getBucketPath());

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

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog configuredCatalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final GcsDestinationConfig gcsConfig = GcsDestinationConfig.getGcsDestinationConfig(config);
    return new S3ConsumerFactory().create(
        outputRecordCollector,
        new GcsStorageOperations(nameTransformer, gcsConfig.getS3Client(), gcsConfig),
        nameTransformer,
        SerializedBufferFactory.getCreateFunction(gcsConfig, FileBuffer::new),
        gcsConfig,
        configuredCatalog);
  }

}
