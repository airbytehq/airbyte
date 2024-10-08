/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.FORMAT_TYPE_CONFIG_KEY;
import static java.util.Map.entry;
import static java.util.Map.ofEntries;
import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.config.catalog.RESTCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.format.FormatConfig;
import io.airbyte.integrations.destination.iceberg.config.storage.ServerManagedStorageConfig;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.apache.iceberg.rest.RESTCatalog;
import org.apache.iceberg.spark.SparkCatalog;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

@Slf4j
class IcebergRESTCatalogServerManagedConfigTest {

  private static final String FAKE_WAREHOUSE_NAME = "fake-warehouse";
  private static final String FAKE_REST_URI = "http://fake-rest-uri";
  private static final String FAKE_CREDENTIAL = "fake-credential";
  private static final String FAKE_TOKEN = "fake-token";

  private RESTCatalogConfig config;

  @BeforeEach
  void setup() {
    JsonNode jsonNode = Jsons.jsonNode(ofEntries(entry(IcebergConstants.REST_CATALOG_URI_CONFIG_KEY, FAKE_REST_URI),
        entry(IcebergConstants.REST_CATALOG_CREDENTIAL_CONFIG_KEY, FAKE_CREDENTIAL),
        entry(IcebergConstants.REST_CATALOG_TOKEN_CONFIG_KEY, FAKE_TOKEN)));

    config = new RESTCatalogConfig(jsonNode);
    config.setStorageConfig(new ServerManagedStorageConfig(FAKE_WAREHOUSE_NAME));
    config.setFormatConfig(new FormatConfig(Jsons.jsonNode(ImmutableMap.of(FORMAT_TYPE_CONFIG_KEY, "Parquet"))));
    config.setDefaultOutputDatabase("default");
  }

  @Test
  public void checksRESTServerUri() {
    final IcebergOssDestination destinationFail = new IcebergOssDestination();
    final AirbyteConnectionStatus status = destinationFail.check(Jsons.deserialize("""
                                                                                   {
                                                                                     "catalog_config": {
                                                                                       "catalog_type": "REST",
                                                                                       "rest_credential": "fake-credential",
                                                                                       "rest_token": "fake-token",
                                                                                       "database": "test"
                                                                                     },
                                                                                     "storage_config": {
                                                                                       "storage_type": "MANAGED",
                                                                                       "managed_warehouse_name": "fake-warehouse"
                                                                                     },
                                                                                     "format_config": {
                                                                                       "format": "Parquet"
                                                                                     }
                                                                                   }"""));
    log.info("status={}", status);
    assertThat(status.getStatus()).isEqualTo(Status.FAILED);
    assertThat(status.getMessage()).contains("rest_uri is required");
  }

  @Test
  public void restCatalogSparkConfigTest() {
    Map<String, String> sparkConfig = config.sparkConfigMap();
    log.info("Spark Config for REST catalog: {}", sparkConfig);

    // Catalog config
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.catalog-impl")).isEqualTo(RESTCatalog.class.getName());
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.uri")).isEqualTo(FAKE_REST_URI);
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.credential")).isEqualTo(FAKE_CREDENTIAL);
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.token")).isEqualTo(FAKE_TOKEN);
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg")).isEqualTo(SparkCatalog.class.getName());
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.warehouse")).isEqualTo(FAKE_WAREHOUSE_NAME);
  }

  @Test
  public void s3ConfigForCatalogInitializeTest() {
    Map<String, String> properties = config.getStorageConfig().catalogInitializeProperties();
    assertThat(properties).isEmpty();
  }

}
