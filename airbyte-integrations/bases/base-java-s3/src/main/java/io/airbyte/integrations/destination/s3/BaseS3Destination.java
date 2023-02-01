/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.util.S3NameTransformer;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseS3Destination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseS3Destination.class);

  protected final S3DestinationConfigFactory configFactory;

  private final NamingConventionTransformer nameTransformer;

  protected BaseS3Destination() {
    this(new S3DestinationConfigFactory());
  }

  protected BaseS3Destination(final S3DestinationConfigFactory configFactory) {
    this.configFactory = configFactory;
    this.nameTransformer = new S3NameTransformer();
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final S3DestinationConfig destinationConfig = configFactory.getS3DestinationConfig(config, storageProvider());
      final AmazonS3 s3Client = destinationConfig.getS3Client();

      S3BaseChecks.testIAMUserHasListObjectPermission(s3Client, destinationConfig.getBucketName());
      S3BaseChecks.testSingleUpload(s3Client, destinationConfig.getBucketName(), destinationConfig.getBucketPath());
      S3BaseChecks.testMultipartUpload(s3Client, destinationConfig.getBucketName(), destinationConfig.getBucketPath());

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to access the S3 bucket: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect to the S3 bucket with the provided configuration. \n" + e
              .getMessage());
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final S3DestinationConfig s3Config = configFactory.getS3DestinationConfig(config, storageProvider());
    return new S3ConsumerFactory().create(
        outputRecordCollector,
        new S3StorageOperations(nameTransformer, s3Config.getS3Client(), s3Config),
        nameTransformer,
        SerializedBufferFactory.getCreateFunction(s3Config, FileBuffer::new),
        s3Config,
        catalog);
  }

  public abstract StorageProvider storageProvider();

}
