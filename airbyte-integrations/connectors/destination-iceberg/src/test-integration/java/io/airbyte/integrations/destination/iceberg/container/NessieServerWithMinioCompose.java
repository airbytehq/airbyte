/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.container;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_FORMAT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.NESSIE_CATALOG_URI_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ACCESS_KEY_ID_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_BUCKET_REGION_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ENDPOINT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_SECRET_KEY_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_WAREHOUSE_URI_CONFIG_KEY;
import static java.util.Map.entry;
import static java.util.Map.ofEntries;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.DockerComposeContainer;
import org.testcontainers.containers.wait.strategy.Wait;

public class NessieServerWithMinioCompose extends DockerComposeContainer<NessieServerWithMinioCompose> {

  private static final Logger LOGGER = LoggerFactory.getLogger(NessieServerWithMinioCompose.class);
  private static final String LOCAL_RELATIVE_PATH = "src/test-integration/resources/";
  private static final String COMPOSE_PATH = LOCAL_RELATIVE_PATH + "nessie-catalog-compose.yml";
  private static final int NESSIE_SERVER_PORT = 19120;
  private static final String NESSIE_API_VERSION = "v1";
  private static final int MINIO_PORT = 9000;
  private static final String NESSIE_SERVICE_NAME = "nessie_1";
  private static final String MINIO_SERVICE_NAME = "minio_1";

  public NessieServerWithMinioCompose() {
    super(Path.of(COMPOSE_PATH).toFile());
    super.withExposedService(NESSIE_SERVICE_NAME,
        NESSIE_SERVER_PORT,
        Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(30)))
            .withExposedService(MINIO_SERVICE_NAME,
                MinioContainer.MINIO_PORT,
                Wait.forHttp(MinioContainer.HEALTH_ENDPOINT).withStartupTimeout(Duration.ofSeconds(60)))
            .withLocalCompose(true);
  }

  @Override
  public void start() {
    long startTime = System.currentTimeMillis();
    super.start();
    LOGGER.info("Nessie Server port: {}", getServicePort(NESSIE_SERVICE_NAME, NESSIE_SERVER_PORT));
    LOGGER.info("Minio port: {}", getServicePort(MINIO_SERVICE_NAME, MINIO_PORT));
    LOGGER.info("Nessie Server docker-compose startup cost: {} ms", System.currentTimeMillis() - startTime);
  }

  public String s3Endpoint() {
    return "http://localhost:" + getServicePort(MINIO_SERVICE_NAME, MINIO_PORT);
  }

  public String nessieServerUri() {
    return "http://localhost:" + getServicePort(NESSIE_SERVICE_NAME, NESSIE_SERVER_PORT) + "/api/" + NESSIE_API_VERSION;
  }

  public JsonNode getComposeConfig(DataFileFormat fileFormat) {
    String s3Endpoint = this.s3Endpoint();
    LOGGER.info("Configure S3 endpoint to {}", s3Endpoint);
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Nessie"),
                entry(NESSIE_CATALOG_URI_CONFIG_KEY, this.nessieServerUri())))),
        entry(ICEBERG_STORAGE_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_STORAGE_TYPE_CONFIG_KEY, "S3"),
                entry(S3_ACCESS_KEY_ID_CONFIG_KEY, "admin"),
                entry(S3_SECRET_KEY_CONFIG_KEY, "password"),
                entry(S3_WAREHOUSE_URI_CONFIG_KEY, "s3://warehouse/nessie"),
                entry(S3_BUCKET_REGION_CONFIG_KEY, "us-east-1"),
                entry(S3_ENDPOINT_CONFIG_KEY, s3Endpoint)))),
        entry(ICEBERG_FORMAT_CONFIG_KEY,
            Jsons.jsonNode(Map.of("format", fileFormat.getConfigValue())))));
  }

  public JsonNode getWrongConfig() {
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Nessie"),
                entry(NESSIE_CATALOG_URI_CONFIG_KEY, "wrong-host:1234")))),
        entry(ICEBERG_STORAGE_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(entry(ICEBERG_STORAGE_TYPE_CONFIG_KEY, "S3"),
                entry(S3_ACCESS_KEY_ID_CONFIG_KEY, "wrong_access_key"),
                entry(S3_SECRET_KEY_CONFIG_KEY, "wrong_secret_key"),
                entry(S3_WAREHOUSE_URI_CONFIG_KEY, "s3://warehouse/"),
                entry(S3_BUCKET_REGION_CONFIG_KEY, "us-east-1"),
                entry(S3_ENDPOINT_CONFIG_KEY, this.s3Endpoint())))),
        entry(ICEBERG_FORMAT_CONFIG_KEY, Jsons.jsonNode(Map.of("format", "wrong-format")))));
  }

}
