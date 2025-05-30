/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.container;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.HTTP_PREFIX;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ACCESS_KEY_ID_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_BUCKET_REGION_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ENDPOINT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_SECRET_KEY_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_WAREHOUSE_URI_CONFIG_KEY;
import static java.util.Map.entry;
import static java.util.Map.ofEntries;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.wait.strategy.HttpWaitStrategy;
import org.testcontainers.utility.DockerImageName;

public class MinioContainer extends GenericContainer<MinioContainer> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MinioContainer.class);
  private static final Credentials DEFAULT_CREDENTIALS = new Credentials("admin", "password", "us-east-1");
  private static final String DEFAULT_IMAGE_NAME = "minio/minio:RELEASE.2024-09-09T16-59-28Z.fips";
  private static final String HEALTH_ENDPOINT = "/minio/health/ready";
  private static final String DEFAULT_DOMAIN_NAME = "minio";
  private static final String DEFAULT_DATA_DIRECTORY = "/data";
  private static final Integer DEFAULT_PORT = 9000;

  public record Credentials(String accessKey, String secretKey, String region) {}

  public MinioContainer() {
    this(DEFAULT_CREDENTIALS);
  }

  public MinioContainer(Credentials credentials) {
    super(DockerImageName.parse(DEFAULT_IMAGE_NAME));

    super.withEnv("MINIO_ROOT_USER", credentials.accessKey)
        .withEnv("MINIO_ROOT_PASSWORD", credentials.secretKey)
        .withEnv("MINIO_DOMAIN", DEFAULT_DOMAIN_NAME)
        .withExposedPorts(DEFAULT_PORT)
        .withCommand("server", DEFAULT_DATA_DIRECTORY)
        .waitingFor(new HttpWaitStrategy()
            .forPort(DEFAULT_PORT)
            .forPath(HEALTH_ENDPOINT)
            .withStartupTimeout(Duration.ofMinutes(2)));
  }

  public JsonNode getConfig(String warehouseUri) {
    final String s3Endpoint = String.format("%s%s:%s", HTTP_PREFIX, this.getHost(),
        this.getMappedPort(DEFAULT_PORT));
    LOGGER.info("Configure S3 endpoint to {}", s3Endpoint);
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_STORAGE_TYPE_CONFIG_KEY, "S3"),
        entry(S3_ACCESS_KEY_ID_CONFIG_KEY, "admin"),
        entry(S3_SECRET_KEY_CONFIG_KEY, "password"),
        entry(S3_WAREHOUSE_URI_CONFIG_KEY, warehouseUri),
        entry(S3_BUCKET_REGION_CONFIG_KEY, "us-east-1"),
        entry(S3_ENDPOINT_CONFIG_KEY, s3Endpoint)));
  }

  public JsonNode getConfigWithResolvedHostPort(String warehouseUri) {
    final String s3Endpoint = String.format("%s%s:%s", HTTP_PREFIX, HostPortResolver.resolveHost(this),
        HostPortResolver.resolvePort(this));
    LOGGER.info("Configure S3 endpoint to {}", s3Endpoint);
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_STORAGE_TYPE_CONFIG_KEY, "S3"),
        entry(S3_ACCESS_KEY_ID_CONFIG_KEY, "admin"),
        entry(S3_SECRET_KEY_CONFIG_KEY, "password"),
        entry(S3_WAREHOUSE_URI_CONFIG_KEY, warehouseUri),
        entry(S3_BUCKET_REGION_CONFIG_KEY, "us-east-1"),
        entry(S3_ENDPOINT_CONFIG_KEY, s3Endpoint)));
  }

  public JsonNode getWrongConfig(String warehouseUri) {
    final String s3Endpoint = String.format("%s%s:%s", HTTP_PREFIX, HostPortResolver.resolveHost(this),
        HostPortResolver.resolvePort(this));
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_STORAGE_TYPE_CONFIG_KEY, "S3"),
        entry(S3_ACCESS_KEY_ID_CONFIG_KEY, "badaccesskey"),
        entry(S3_SECRET_KEY_CONFIG_KEY, "badsecretkey"),
        entry(S3_WAREHOUSE_URI_CONFIG_KEY, warehouseUri),
        entry(S3_BUCKET_REGION_CONFIG_KEY, "us-east-1"),
        entry(S3_ENDPOINT_CONFIG_KEY, s3Endpoint)));
  }

}
