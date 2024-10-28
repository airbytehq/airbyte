/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.jdbc;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.DEFAULT_DATABASE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_FORMAT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.JDBC_CATALOG_SCHEMA_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.JDBC_PASSWORD_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.JDBC_SSL_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.JDBC_URL_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.JDBC_USERNAME_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ACCESS_KEY_ID_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_BUCKET_REGION_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ENDPOINT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_SECRET_KEY_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_WAREHOUSE_URI_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil.ICEBERG_IMAGE_NAME;
import static io.airbyte.integrations.destination.iceberg.container.MinioContainerOldToDelete.DEFAULT_ACCESS_KEY;
import static java.util.Map.entry;
import static java.util.Map.ofEntries;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil;
import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;
import io.airbyte.integrations.destination.iceberg.container.MinioContainer;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.junit.jupiter.api.Disabled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * @author Leibniz on 2022/11/3.
 */
public abstract class BaseIcebergJdbcCatalogS3IntegrationTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseIcebergJdbcCatalogS3IntegrationTest.class);

  private static final String WAREHOUSE_URI = "s3a://warehouse/jdbc";
  private static final String PG_SCHEMA = "public";

  private PostgreSQLContainer<?> catalogDb;
  private MinioContainer minioContainer;

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    catalogDb = new PostgreSQLContainer<>("postgres:13-alpine");
    catalogDb.start();
    LOGGER.info("==> Started PostgreSQL docker container...");

    minioContainer = new MinioContainer();
    minioContainer.start();
    IcebergIntegrationTestUtil.createS3WarehouseBucket(getConfigForTestRunner());
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    catalogDb.stop();
    minioContainer.stop();
  }

  @Override
  protected String getImageName() {
    return ICEBERG_IMAGE_NAME;
  }

  @Override
  protected JsonNode getConfig() {
    final String jdbcUrl = getJdbcUrl(catalogDb);
    LOGGER.info("Postgresql jdbc url: {}", jdbcUrl);
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Jdbc"),
                entry(DEFAULT_DATABASE_CONFIG_KEY, PG_SCHEMA),
                entry(JDBC_URL_CONFIG_KEY, jdbcUrl),
                entry(JDBC_USERNAME_CONFIG_KEY, catalogDb.getUsername()),
                entry(JDBC_PASSWORD_CONFIG_KEY, catalogDb.getPassword()),
                entry(JDBC_SSL_CONFIG_KEY, false),
                entry(JDBC_CATALOG_SCHEMA_CONFIG_KEY, PG_SCHEMA)))),
        entry(ICEBERG_STORAGE_CONFIG_KEY, minioContainer.getConfigWithResolvedHostPort(WAREHOUSE_URI)),
        entry(ICEBERG_FORMAT_CONFIG_KEY, Jsons.jsonNode(Map.of("format", fileFormat().getConfigValue())))));
  }

  private String getJdbcUrl(PostgreSQLContainer<?> postgresContainer) {
    return ("jdbc:postgresql://" +
        HostPortResolver.resolveHost(postgresContainer) +
        ":" +
        HostPortResolver.resolvePort(postgresContainer) +
        "/test");
  }

  private JsonNode getConfigForTestRunner() {
    final String jdbcUrl = catalogDb.getJdbcUrl();
    LOGGER.info("Postgresql jdbc url: {}", jdbcUrl);
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Jdbc"),
                entry(DEFAULT_DATABASE_CONFIG_KEY, PG_SCHEMA),
                entry(JDBC_URL_CONFIG_KEY, jdbcUrl),
                entry(JDBC_USERNAME_CONFIG_KEY, catalogDb.getUsername()),
                entry(JDBC_PASSWORD_CONFIG_KEY, catalogDb.getPassword()),
                entry(JDBC_SSL_CONFIG_KEY, false),
                entry(JDBC_CATALOG_SCHEMA_CONFIG_KEY, PG_SCHEMA)))),
        entry(ICEBERG_STORAGE_CONFIG_KEY, minioContainer.getConfig(WAREHOUSE_URI)),
        entry(ICEBERG_FORMAT_CONFIG_KEY, Jsons.jsonNode(Map.of("format", fileFormat().getConfigValue())))));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final String jdbcUrl = "jdbc:postgresql://%s:%d/%s".formatted(HostPortResolver.resolveHost(catalogDb),
        HostPortResolver.resolvePort(catalogDb),
        catalogDb.getDatabaseName());
    final String s3Endpoint = "http://%s:%s".formatted(HostPortResolver.resolveHost(minioContainer),
        HostPortResolver.resolvePort(minioContainer));
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Jdbc"),
                entry(DEFAULT_DATABASE_CONFIG_KEY, PG_SCHEMA),
                entry(JDBC_URL_CONFIG_KEY, jdbcUrl),
                entry(JDBC_USERNAME_CONFIG_KEY, catalogDb.getUsername()),
                entry(JDBC_PASSWORD_CONFIG_KEY, "wrong_password"),
                entry(JDBC_SSL_CONFIG_KEY, false),
                entry(JDBC_CATALOG_SCHEMA_CONFIG_KEY, PG_SCHEMA)))),
        entry(ICEBERG_STORAGE_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(entry(ICEBERG_STORAGE_TYPE_CONFIG_KEY, "S3"),
                entry(S3_ACCESS_KEY_ID_CONFIG_KEY, DEFAULT_ACCESS_KEY),
                entry(S3_SECRET_KEY_CONFIG_KEY, "wrong_secret_key"),
                entry(S3_WAREHOUSE_URI_CONFIG_KEY, "s3a://warehouse/jdbc"),
                entry(S3_BUCKET_REGION_CONFIG_KEY, "us-east-1"),
                entry(S3_ENDPOINT_CONFIG_KEY, s3Endpoint)))),
        entry(ICEBERG_FORMAT_CONFIG_KEY, Jsons.jsonNode(Map.of("format", fileFormat().getConfigValue())))));
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return IcebergIntegrationTestUtil.retrieveRecords(getConfigForTestRunner(), namespace, streamName);
  }

  abstract DataFileFormat fileFormat();

  @Nullable
  @Override
  protected String getDefaultSchema(@NotNull JsonNode config) throws Exception {
    // TODO: This was NPE'ing without this return value because of Kotlin's non-null in base,
    // but whats the actual value to pass instead of empty ?
    return "";
  }

  @Disabled("Existing connector does not support flattened rows yet")
  @Override
  public void testAirbyteFields() throws Exception {}

}
