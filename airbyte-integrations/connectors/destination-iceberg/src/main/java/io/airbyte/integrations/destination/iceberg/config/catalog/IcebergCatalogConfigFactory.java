/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.catalog;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.DEFAULT_DATABASE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_CATALOG_TYPE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_FORMAT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.ICEBERG_STORAGE_TYPE_CONFIG_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.iceberg.config.format.FormatConfig;
import io.airbyte.integrations.destination.iceberg.config.storage.S3Config;
import io.airbyte.integrations.destination.iceberg.config.storage.StorageConfig;
import io.airbyte.integrations.destination.iceberg.config.storage.StorageType;
import javax.annotation.Nonnull;
import org.jetbrains.annotations.NotNull;

/**
 * @author Leibniz on 2022/10/31.
 */
public class IcebergCatalogConfigFactory {

  public IcebergCatalogConfig fromJsonNodeConfig(@Nonnull final JsonNode config) {
    // storage config
    final JsonNode storageConfigJson = config.get(ICEBERG_STORAGE_CONFIG_KEY);
    StorageConfig storageConfig = genStorageConfig(storageConfigJson);

    // format config
    final JsonNode formatConfigJson = config.get(ICEBERG_FORMAT_CONFIG_KEY);
    FormatConfig formatConfig = new FormatConfig(formatConfigJson);

    // catalog config and make final IcebergCatalogConfig Object
    final JsonNode catalogConfigJson = config.get(ICEBERG_CATALOG_CONFIG_KEY);
    IcebergCatalogConfig icebergCatalogConfig = genIcebergCatalogConfig(catalogConfigJson);
    icebergCatalogConfig.formatConfig = formatConfig;
    icebergCatalogConfig.storageConfig = storageConfig;
    icebergCatalogConfig.setDefaultOutputDatabase(catalogConfigJson.get(DEFAULT_DATABASE_CONFIG_KEY).asText());

    return icebergCatalogConfig;
  }

  private StorageConfig genStorageConfig(JsonNode storageConfigJson) {
    String storageTypeStr = storageConfigJson.get(ICEBERG_STORAGE_TYPE_CONFIG_KEY).asText();
    if (storageTypeStr == null) {
      throw new IllegalArgumentException(ICEBERG_STORAGE_TYPE_CONFIG_KEY + " cannot be null");
    }
    StorageType storageType = StorageType.valueOf(storageTypeStr.toUpperCase());
    switch (storageType) {
      case S3:
        return S3Config.fromDestinationConfig(storageConfigJson);
      case HDFS:
      default:
        throw new RuntimeException("Unexpected storage config: " + storageTypeStr);
    }
  }

  @NotNull
  private static IcebergCatalogConfig genIcebergCatalogConfig(@NotNull JsonNode catalogConfigJson) {
    String catalogTypeStr = catalogConfigJson.get(ICEBERG_CATALOG_TYPE_CONFIG_KEY).asText();
    if (catalogTypeStr == null) {
      throw new IllegalArgumentException(ICEBERG_CATALOG_TYPE_CONFIG_KEY + " cannot be null");
    }
    CatalogType catalogType = CatalogType.valueOf(catalogTypeStr.toUpperCase());

    return switch (catalogType) {
      case HIVE -> new HiveCatalogConfig(catalogConfigJson);
      case HADOOP -> new HadoopCatalogConfig(catalogConfigJson);
      case JDBC -> new JdbcCatalogConfig(catalogConfigJson);
      default -> throw new RuntimeException("Unexpected catalog config: " + catalogTypeStr);
    };
  }

  public static String getProperty(@Nonnull final JsonNode config, @Nonnull final String key) {
    final JsonNode node = config.get(key);
    if (node == null) {
      return null;
    }
    return node.asText();
  }

}
