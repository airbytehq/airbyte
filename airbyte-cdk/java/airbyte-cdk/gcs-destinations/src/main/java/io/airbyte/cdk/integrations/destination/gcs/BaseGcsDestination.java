/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.gcs;

import static io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.AmazonS3Exception;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks;
import io.airbyte.cdk.integrations.destination.s3.S3ConsumerFactory;
import io.airbyte.cdk.integrations.destination.s3.SerializedBufferFactory;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseGcsDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseGcsDestination.class);
  public static final String EXPECTED_ROLES = "storage.multipartUploads.abort, storage.multipartUploads.create, "
      + "storage.objects.create, storage.objects.delete, storage.objects.get, storage.objects.list";

  private final NamingConventionTransformer nameTransformer;

  public BaseGcsDestination() {
    this.nameTransformer = new GcsNameTransformer();
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final GcsDestinationConfig destinationConfig = GcsDestinationConfig.getGcsDestinationConfig(config);
      final AmazonS3 s3Client = destinationConfig.getS3Client();

      // Test single upload (for small files) permissions
      S3BaseChecks.testSingleUpload(s3Client, destinationConfig.getBucketName(), destinationConfig.getBucketPath());

      // Test multipart upload with stream transfer manager
      S3BaseChecks.testMultipartUpload(s3Client, destinationConfig.getBucketName(), destinationConfig.getBucketPath());

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final AmazonS3Exception e) {
      LOGGER.error("Exception attempting to access the Gcs bucket", e);
      final String message = getErrorMessage(e.getErrorCode(), 0, e.getMessage(), e);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, message);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(message);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to access the Gcs bucket: {}. Please make sure you account has all of these roles: " + EXPECTED_ROLES, e);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, e.getMessage());
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
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
