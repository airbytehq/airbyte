/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.storage;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.MANAGED_WAREHOUSE_NAME;
import static io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfigFactory.getProperty;
import static org.apache.commons.lang3.StringUtils.isBlank;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import java.util.HashMap;
import java.util.Map;
import javax.annotation.Nonnull;

public class ServerManagedStorageConfig implements StorageConfig {

  private final String warehouseName;

  public ServerManagedStorageConfig(String warehouseName) {
    this.warehouseName = warehouseName;
  }

  @Override
  public void check() throws Exception {}

  @Override
  public String getWarehouseUri() {
    return warehouseName;
  }

  public static ServerManagedStorageConfig fromDestinationConfig(@Nonnull final JsonNode config) {
    String warehouseName = getProperty(config, MANAGED_WAREHOUSE_NAME);
    if (isBlank(warehouseName)) {
      throw new IllegalArgumentException(MANAGED_WAREHOUSE_NAME + " cannot be null");
    }

    return new ServerManagedStorageConfig(warehouseName);
  }

  @Override
  public Map<String, String> sparkConfigMap(String catalogName) {
    Map<String, String> sparkConfig = new HashMap<>();
    sparkConfig.put("spark.sql.catalog." + catalogName + ".warehouse", warehouseName);
    return sparkConfig;
  }

  @Override
  public Map<String, String> catalogInitializeProperties() {
    return ImmutableMap.of();
  }

}
