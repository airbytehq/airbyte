/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.BaseS3Destination;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import io.airbyte.integrations.destination.s3.SerializedBufferFactory;
import io.airbyte.integrations.destination.s3.StorageProvider;
import io.airbyte.integrations.destination.s3.util.S3NameTransformer;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class S3GlueDestination extends BaseS3Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3GlueDestination.class);

  public S3GlueDestination() {
    super();
  }

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new S3GlueDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    var status = super.check(config);
    if (status.getStatus() == AirbyteConnectionStatus.Status.FAILED) {
      return status;
    }
    final GlueDestinationConfig glueConfig = GlueDestinationConfig.getInstance(config);
    MetastoreOperations metastoreOperations = null;
    String tableName = "test_table";
    try {
      metastoreOperations = new GlueOperations(glueConfig.getAWSGlueInstance());
      metastoreOperations.upsertTable(glueConfig.getDatabase(), tableName, "s3://", Jsons.emptyObject(), glueConfig.getSerializationLibrary());

      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Error while trying to perform check with Glue: ", e);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED);
    } finally {
      if (metastoreOperations != null) {
        try {
          metastoreOperations.deleteTable(glueConfig.getDatabase(), tableName);
        } catch (Exception e) {
          LOGGER.error("Error while deleting Glue table");
        }
        metastoreOperations.close();
      }
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog configuredCatalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {
    final S3DestinationConfig s3Config = configFactory.getS3DestinationConfig(config, storageProvider());
    final GlueDestinationConfig glueConfig = GlueDestinationConfig.getInstance(config);
    final NamingConventionTransformer nameTransformer = new S3NameTransformer();
    return new S3GlueConsumerFactory().create(
        outputRecordCollector,
        new S3StorageOperations(nameTransformer, s3Config.getS3Client(), s3Config),
        // TODO (itaseski) add Glue name transformer
        new GlueOperations(glueConfig.getAWSGlueInstance()),
        nameTransformer,
        SerializedBufferFactory.getCreateFunction(s3Config, FileBuffer::new),
        s3Config,
        glueConfig,
        configuredCatalog);
  }

  @Override
  public StorageProvider storageProvider() {
    return StorageProvider.AWS_S3;
  }

}
