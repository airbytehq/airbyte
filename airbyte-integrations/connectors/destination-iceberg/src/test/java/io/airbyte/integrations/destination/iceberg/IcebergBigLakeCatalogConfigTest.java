package io.airbyte.integrations.destination.iceberg;

import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import org.mockito.MockedStatic;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageException;
import org.apache.iceberg.data.IcebergGenerics;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import lombok.extern.slf4j.Slf4j;
import java.io.IOException;
import java.util.Map;
import static java.util.Map.entry;
import static java.util.Map.ofEntries;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.config.catalog.BigLakeCatalogConfig;
import org.apache.iceberg.gcp.biglake.BigLakeCatalog;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.FORMAT_TYPE_CONFIG_KEY;
import io.airbyte.integrations.destination.iceberg.config.storage.GCSConfig;
import io.airbyte.integrations.destination.iceberg.config.format.FormatConfig;
import com.google.common.collect.ImmutableMap;
import static org.assertj.core.api.Assertions.assertThat;
import org.apache.iceberg.spark.SparkCatalog;


@Slf4j
class BigLakeCatalogConfigTest {

  private static final String FAKE_PROJECT_ID = "fake-project-id";
  private static final String FAKE_WAREHOUSE_URI = "gcs://fake-uri";
  private static final String FAKE_LOCATION = "fake-location";

  private Storage cloudStorage;

  private BigLakeCatalogConfig config;


  @BeforeEach
  void setup() throws IOException {
    cloudStorage = mock(Storage.class);
    JsonNode jsonNode = Jsons.jsonNode(ofEntries(entry(IcebergConstants.GCP_PROJECT_ID_CONFIG_KEY, FAKE_PROJECT_ID)));
    config = new BigLakeCatalogConfig(jsonNode);
    config.setStorageConfig(GCSConfig.builder()
        .warehouseUri(FAKE_WAREHOUSE_URI)
        .bucketLocation(FAKE_LOCATION)
        .build());
    config.setFormatConfig(new FormatConfig(Jsons.jsonNode(ImmutableMap.of(FORMAT_TYPE_CONFIG_KEY, "Parquet"))));
    config.setDefaultOutputDatabase("default");
  }

  @Test
  public void bigLakeCatalogConfigTest() {
    Map<String, String> sparkConfig = config.sparkConfigMap();
    log.info("Spark Config for BigLake catalog: {}", sparkConfig);

    // Catalog config
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.catalog-impl")).isEqualTo(BigLakeCatalog.class.getName());
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.warehouse")).isEqualTo(FAKE_WAREHOUSE_URI);
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.gcp_project")).isEqualTo(FAKE_PROJECT_ID);
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.gcp_location")).isEqualTo(FAKE_LOCATION);
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg.blms_catalog")).isEqualTo("iceberg");
    assertThat(sparkConfig.get("spark.sql.catalog.iceberg")).isEqualTo(SparkCatalog.class.getName());

  }

  }

