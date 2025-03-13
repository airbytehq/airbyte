/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.container;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.HTTP_PREFIX;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_FORMAT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.REST_CATALOG_URI_CONFIG_KEY;
import static java.util.Map.entry;
import static java.util.Map.ofEntries;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;
import io.airbyte.integrations.destination.iceberg.container.MinioContainer.Credentials;
import java.time.Duration;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.wait.strategy.Wait;
import org.testcontainers.utility.DockerImageName;

public class TabularRestCatalogContainer {

  private static final Logger LOGGER = LoggerFactory.getLogger(TabularRestCatalogContainer.class);
  private static final String AWS_ACCESS_KEY_ID = "admin";
  private static final String AWS_SECRET_ACCESS_KEY = "password";
  private static final String AWS_REGION = "us-east-1";

  private static final String DEFAULT_REST_CATALOG_IMAGE = "tabulario/iceberg-rest:1.6.0";
  private static final String DEFAULT_MINIO_CLIENT_IMAGE_NAME = "minio/mc:RELEASE.2024-09-09T07-53-10Z.fips";
  public static final Integer DEFAULT_REST_CATALOG_PORT = 8181;

  private static final String REST_WAREHOUSE_URI = "s3://warehouse/rest";

  private final MinioContainer minioContainer;
  private final GenericContainer<?> minioClientContainer;
  private final GenericContainer<?> icebergRestContainer;

  public TabularRestCatalogContainer() {
    final Credentials credentials = new Credentials(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION);
    minioContainer = new MinioContainer(credentials);

    minioClientContainer =
        new GenericContainer<>(DockerImageName.parse(DEFAULT_MINIO_CLIENT_IMAGE_NAME))
            .withEnv("AWS_ACCESS_KEY_ID", AWS_ACCESS_KEY_ID)
            .withEnv("AWS_SECRET_ACCESS_KEY", AWS_SECRET_ACCESS_KEY)
            .withEnv("AWS_REGION", AWS_REGION);

    icebergRestContainer =
        new GenericContainer<>(DockerImageName.parse(DEFAULT_REST_CATALOG_IMAGE))
            .withEnv("AWS_ACCESS_KEY_ID", AWS_ACCESS_KEY_ID)
            .withEnv("AWS_SECRET_ACCESS_KEY", AWS_SECRET_ACCESS_KEY)
            .withEnv("AWS_REGION", AWS_REGION)
            .withEnv("CATALOG_WAREHOUSE", "s3://warehouse/rest")
            .withEnv("CATALOG_IO__IMPL", "org.apache.iceberg.aws.s3.S3FileIO")
            .withExposedPorts(DEFAULT_REST_CATALOG_PORT)
            .waitingFor(Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(30)));

  }

  public void startAll() {
    minioContainer.start();
    // Grab the resolved host-port of the minio container before starting dependent containers
    // You need the container started before resolving network settings ip address.
    final String minioHost = HostPortResolver.resolveHost(minioContainer);
    final Integer minioPort = HostPortResolver.resolvePort(minioContainer);
    String cmdTpl = """
                    until (/usr/bin/mc config host add minio %s%s:%s admin password) do echo '...waiting...' && sleep 1; done;
                    tail -f /dev/null
                    """;
    String cmd = String.format(cmdTpl, HTTP_PREFIX, minioHost, minioPort);
    minioClientContainer.withCreateContainerCmdModifier(containerCmd -> containerCmd.withTty(true).withCmd(cmd))
        .dependsOn(minioContainer).start();
    icebergRestContainer.withEnv("CATALOG_S3_ENDPOINT", String.format("%s%s:%s", HTTP_PREFIX, minioHost, minioPort))
        .start();
  }

  public void stopAll() {
    icebergRestContainer.stop();
    minioClientContainer.stop();
    minioContainer.stop();
  }

  public JsonNode getConfigWithResolvedHostPort(DataFileFormat fileFormat) {
    final String resetServerEndpoint = String.format("%s%s:%s", HTTP_PREFIX, HostPortResolver.resolveHost(icebergRestContainer),
        HostPortResolver.resolvePort(icebergRestContainer));
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Rest"),
                entry(REST_CATALOG_URI_CONFIG_KEY, resetServerEndpoint)))),
        entry(ICEBERG_STORAGE_CONFIG_KEY, minioContainer.getConfigWithResolvedHostPort(REST_WAREHOUSE_URI)),
        entry(ICEBERG_FORMAT_CONFIG_KEY,
            Jsons.jsonNode(Map.of("format", fileFormat.getConfigValue())))));
  }

  public JsonNode getConfig(DataFileFormat fileFormat) {
    final String resetServerEndpoint = String.format("%s%s:%s", HTTP_PREFIX, icebergRestContainer.getHost(),
        icebergRestContainer.getMappedPort(DEFAULT_REST_CATALOG_PORT));
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Rest"),
                entry(REST_CATALOG_URI_CONFIG_KEY, resetServerEndpoint)))),
        entry(ICEBERG_STORAGE_CONFIG_KEY, minioContainer.getConfig(REST_WAREHOUSE_URI)),
        entry(ICEBERG_FORMAT_CONFIG_KEY,
            Jsons.jsonNode(Map.of("format", fileFormat.getConfigValue())))));
  }

  public JsonNode getWrongConfig() {
    return Jsons.jsonNode(ofEntries(
        entry(ICEBERG_CATALOG_CONFIG_KEY,
            Jsons.jsonNode(ofEntries(
                entry(ICEBERG_CATALOG_TYPE_CONFIG_KEY, "Rest"),
                entry(REST_CATALOG_URI_CONFIG_KEY, "wrong-host:1234")))),
        entry(ICEBERG_STORAGE_CONFIG_KEY, minioContainer.getWrongConfig(REST_WAREHOUSE_URI)),
        entry(ICEBERG_FORMAT_CONFIG_KEY, Jsons.jsonNode(Map.of("format", "wrong-format")))));
  }

}
