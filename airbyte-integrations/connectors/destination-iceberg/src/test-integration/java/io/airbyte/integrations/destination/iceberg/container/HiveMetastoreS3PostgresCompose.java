/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.container;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.DEFAULT_DATABASE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.HIVE_THRIFT_URI_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_FORMAT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ACCESS_KEY_ID_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_BUCKET_REGION_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ENDPOINT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_SECRET_KEY_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_WAREHOUSE_URI_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil.WAREHOUSE_BUCKET_NAME;
import static io.airbyte.integrations.destination.iceberg.container.MinioContainerOldToDelete.DEFAULT_ACCESS_KEY;
import static io.airbyte.integrations.destination.iceberg.container.MinioContainerOldToDelete.DEFAULT_SECRET_KEY;
import static java.util.Map.entry;
import static java.util.Map.ofEntries;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;
import io.airbyte.integrations.destination.iceberg.hive.IcebergHiveCatalogS3ParquetIntegrationTest;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.DockerComposeContainer;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.containers.wait.strategy.Wait;

/**
 * @author Leibniz on 2022/11/4.
 */
public class HiveMetastoreS3PostgresCompose extends DockerComposeContainer<HiveMetastoreS3PostgresCompose> {

  private static final Logger LOGGER = LoggerFactory.getLogger(IcebergHiveCatalogS3ParquetIntegrationTest.class);

  private static final String LOCAL_RELATIVE_PATH = "src/test-integration/resources/";
  private static final String METASTORE_COMPOSE_PATH = LOCAL_RELATIVE_PATH + "hive-metastore-compose.yml";
  public static final int METASTORE_PORT = 9083;
  private static final String POSTGRES_SERVICE_NAME = "postgres_1";
  private static final String MINIO_SERVICE_NAME = "minio_1";
  private static final String METASTORE_SERVICE_NAME = "hive_metastore_1";

  public HiveMetastoreS3PostgresCompose() {
    super(Path.of(METASTORE_COMPOSE_PATH).toFile());
    super.withExposedService(POSTGRES_SERVICE_NAME,
        PostgreSQLContainer.POSTGRESQL_PORT,
        Wait.forLogMessage(".*database system is ready to accept connections.*\\s", 2)
            .withStartupTimeout(Duration.ofSeconds(60)))
                .withExposedService(MINIO_SERVICE_NAME,
                    MinioContainerOldToDelete.DEFAULT_PORT,
                    Wait.forHttp(MinioContainerOldToDelete.HEALTH_ENDPOINT).withStartupTimeout(Duration.ofSeconds(60)))
                .withExposedService(METASTORE_SERVICE_NAME,
                    METASTORE_PORT,
                    Wait.forListeningPort().withStartupTimeout(Duration.ofMinutes(5)))
                .withLocalCompose(true);
  }

  @Override
  public void start() {
    long startTime = System.currentTimeMillis();
    super.start();
    LOGGER.info("PostgreSQL port: {}", getServicePort(POSTGRES_SERVICE_NAME, PostgreSQLContainer.POSTGRESQL_PORT));
    LOGGER.info("Minio port: {}", getServicePort(MINIO_SERVICE_NAME, MinioContainerOldToDelete.DEFAULT_PORT));
    LOGGER.info("Hive Metastore port: {}", getServicePort(METASTORE_SERVICE_NAME, METASTORE_PORT));
    LOGGER.info("Hive Metastore docker-compose startup cost: {} ms", System.currentTimeMillis() - startTime);
  }

  public String s3Endpoint() {
    return "http://localhost:" + getServicePort(MINIO_SERVICE_NAME, MinioContainerOldToDelete.DEFAULT_PORT);
  }

  public String thriftUri() {
    return "thrift://localhost:" + getServicePort(METASTORE_SERVICE_NAME, METASTORE_PORT);
  }

  public JsonNode getComposeConfig(DataFileFormat fileFormat) {
    String s3Endpoint = this.s3Endpoint();
    LOGGER.info("Configurate S3 endpoint to {}", s3Endpoint);
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Hive"),
                entry(HIVE_THRIFT_URI_CONFIG_KEY, this.thriftUri()),
                entry(DEFAULT_DATABASE_CONFIG_KEY, "test")))),
        entry(ICEBERG_STORAGE_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_STORAGE_TYPE_CONFIG_KEY, "S3"),
                entry(S3_ACCESS_KEY_ID_CONFIG_KEY, DEFAULT_ACCESS_KEY),
                entry(S3_SECRET_KEY_CONFIG_KEY, DEFAULT_SECRET_KEY),
                entry(S3_WAREHOUSE_URI_CONFIG_KEY, "s3a://" + WAREHOUSE_BUCKET_NAME + "/hadoop"),
                entry(S3_BUCKET_REGION_CONFIG_KEY, "us-east-1"),
                entry(S3_ENDPOINT_CONFIG_KEY, s3Endpoint)))),
        entry(ICEBERG_FORMAT_CONFIG_KEY,
            Jsons.jsonNode(Map.of("format", fileFormat.getConfigValue())))));
  }

  public JsonNode getWrongConfig() {
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Hive"),
                entry(HIVE_THRIFT_URI_CONFIG_KEY, "wrong-host:1234"),
                entry(DEFAULT_DATABASE_CONFIG_KEY, "default")))),
        entry(ICEBERG_STORAGE_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(entry(ICEBERG_STORAGE_TYPE_CONFIG_KEY, "S3"),
                entry(S3_ACCESS_KEY_ID_CONFIG_KEY, DEFAULT_ACCESS_KEY),
                entry(S3_SECRET_KEY_CONFIG_KEY, "wrong_secret_key"),
                entry(S3_WAREHOUSE_URI_CONFIG_KEY, "s3a://warehouse/hadoop"),
                entry(S3_BUCKET_REGION_CONFIG_KEY, "us-east-1"),
                entry(S3_ENDPOINT_CONFIG_KEY, this.s3Endpoint())))),
        entry(ICEBERG_FORMAT_CONFIG_KEY, Jsons.jsonNode(Map.of("format", "wrong-format")))));
  }

}
