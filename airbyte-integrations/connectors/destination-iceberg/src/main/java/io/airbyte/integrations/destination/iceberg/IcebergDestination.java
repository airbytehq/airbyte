/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.ListObjectsRequest;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.iceberg.config.S3Config;
import io.airbyte.integrations.destination.iceberg.config.S3Config.S3ConfigFactory;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Consumer;
import lombok.extern.slf4j.Slf4j;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.SparkSession.Builder;

@Slf4j
public class IcebergDestination extends BaseConnector implements Destination {

    private final S3ConfigFactory s3ConfigFactory;

    public IcebergDestination() {
        this.s3ConfigFactory = new S3ConfigFactory();
    }

    @VisibleForTesting
    public IcebergDestination(S3ConfigFactory s3ConfigFactory) {
        this.s3ConfigFactory = Objects.requireNonNullElseGet(s3ConfigFactory, S3ConfigFactory::new);
    }

    public static void main(String[] args) throws Exception {
        new IntegrationRunner(new IcebergDestination()).run(args);
    }

    @Override
    public AirbyteConnectionStatus check(JsonNode config) {
        try {
            final S3Config destinationConfig = this.s3ConfigFactory.parseS3Config(config);
            final AmazonS3 s3Client = destinationConfig.getS3Client();

            //normalize path
            final var prefix = destinationConfig.getBucketPath().isEmpty() ? ""
                : destinationConfig.getBucketPath() + (destinationConfig.getBucketPath().endsWith("/") ? "" : "/");
            final String tempObjectName =
                prefix + "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
            final var bucket = destinationConfig.getBucketName();

            //check bucket exists
            if (!s3Client.doesBucketExistV2(bucket)) {
                log.info("Bucket {} does not exist; creating...", bucket);
                s3Client.createBucket(bucket);
                log.info("Bucket {} has been created.", bucket);
            }

            //try puts temp object
            s3Client.putObject(bucket, tempObjectName, "check-content");

            //check listObjects
            log.info("Started testing if IAM user can call listObjects on the destination bucket");
            final ListObjectsRequest request = new ListObjectsRequest().withBucketName(bucket).withMaxKeys(1);
            s3Client.listObjects(request);
            log.info("Finished checking for listObjects permission");

            //delete temp object
            s3Client.deleteObject(bucket, tempObjectName);

            destinationConfig.getCatalogConfig().check(destinationConfig);

            //getting here means s3 check success
            return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
        } catch (final Exception e) {
            log.error("Exception attempting to access the S3 bucket: ", e);
            return new AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage("Could not connect to the S3 bucket with the provided configuration. \n" + e
                    .getMessage());
        }
    }

    @Override
    public AirbyteMessageConsumer getConsumer(JsonNode config,
        ConfiguredAirbyteCatalog catalog,
        Consumer<AirbyteMessage> outputRecordCollector) {
        final S3Config s3Config = this.s3ConfigFactory.parseS3Config(config);
        Map<String, String> sparkConfMap = s3Config.getCatalogConfig().sparkConfigMap(s3Config);

        log.debug("s3Config:{}, sparkConfMap:{}", s3Config, sparkConfMap);

        Builder sparkBuilder = SparkSession.builder()
            .master("local")
            .appName("Airbyte->Iceberg-" + System.currentTimeMillis());
        sparkConfMap.forEach(sparkBuilder::config);
        SparkSession spark = sparkBuilder.getOrCreate();

        return new IcebergConsumer(spark, outputRecordCollector, catalog, s3Config.getCatalogConfig());
    }

}
