/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.catalog;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.CATALOG_NAME;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.HIVE_THRIFT_URI_CONFIG_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.HashMap;
import java.util.Map;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.ToString;
import org.apache.iceberg.CatalogProperties;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.hive.HiveCatalog;

/**
 * @author Leibniz on 2022/10/26.
 */
@Data
@AllArgsConstructor
@ToString(callSuper = true)
@EqualsAndHashCode(callSuper = false)
public class HiveCatalogConfig extends IcebergCatalogConfig {

  private final String thriftUri;

  public HiveCatalogConfig(JsonNode catalogConfig) {
    String thriftUri = catalogConfig.get(HIVE_THRIFT_URI_CONFIG_KEY).asText();
    if (!thriftUri.startsWith("thrift://")) {
      throw new IllegalArgumentException(HIVE_THRIFT_URI_CONFIG_KEY + " must start with 'thrift://'");
    }
    this.thriftUri = thriftUri;
  }

  @Override
  public Map<String, String> sparkConfigMap() {
    Map<String, String> configMap = new HashMap<>();
    configMap.put("spark.network.timeout", "300000");
    configMap.put("spark.sql.defaultCatalog", CATALOG_NAME);
    configMap.put("spark.sql.catalog." + CATALOG_NAME, "org.apache.iceberg.spark.SparkCatalog");
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".type", "hive");
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".uri", this.thriftUri);
    configMap.put("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions");
    configMap.put("spark.driver.extraJavaOptions", "-Dpackaging.type=jar -Djava.io.tmpdir=/tmp");

    configMap.putAll(this.storageConfig.sparkConfigMap(CATALOG_NAME));
    return configMap;
  }

  @Override
  public Catalog genCatalog() {
    HiveCatalog catalog = new HiveCatalog();
    Map<String, String> properties = new HashMap<>();
    properties.put(CatalogProperties.URI, thriftUri);
    properties.put(CatalogProperties.WAREHOUSE_LOCATION, this.storageConfig.getWarehouseUri());
    properties.putAll(this.storageConfig.catalogInitializeProperties());
    catalog.initialize("hive", properties);
    return catalog;
  }

}
