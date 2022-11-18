/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.catalog;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.CATALOG_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.ToString;
import org.apache.hadoop.conf.Configuration;
import org.apache.iceberg.CatalogProperties;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.hadoop.HadoopCatalog;
import org.jetbrains.annotations.NotNull;

/**
 * @author Leibniz on 2022/11/1.
 */
@Data
@ToString(callSuper = true)
@EqualsAndHashCode(callSuper = false)
public class HadoopCatalogConfig extends IcebergCatalogConfig {

  public static final String SPARK_HADOOP_CONFIG_PREFIX = "spark.hadoop.";

  public HadoopCatalogConfig(@NotNull JsonNode catalogConfigJson) {}

  @Override
  public Map<String, String> sparkConfigMap() {
    Map<String, String> configMap = new HashMap<>();
    configMap.put("spark.network.timeout", "300000");
    configMap.put("spark.sql.defaultCatalog", CATALOG_NAME);
    configMap.put("spark.sql.catalog." + CATALOG_NAME, "org.apache.iceberg.spark.SparkCatalog");
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".type", "hadoop");
    configMap.put("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions");
    configMap.put("spark.driver.extraJavaOptions", "-Dpackaging.type=jar -Djava.io.tmpdir=/tmp");

    configMap.putAll(this.storageConfig.sparkConfigMap(CATALOG_NAME));
    return configMap;
  }

  @Override
  public Catalog genCatalog() {
    Configuration conf = new Configuration();
    for (Entry<String, String> entry : this.storageConfig.sparkConfigMap(CATALOG_NAME).entrySet()) {
      String key = entry.getKey();
      if (key.startsWith(SPARK_HADOOP_CONFIG_PREFIX + "fs.")) {
        conf.set(key.substring(SPARK_HADOOP_CONFIG_PREFIX.length()), entry.getValue());
      }
    }

    HadoopCatalog catalog = new HadoopCatalog();
    catalog.setConf(conf);
    Map<String, String> properties = new HashMap<>(this.storageConfig.catalogInitializeProperties());
    properties.put(CatalogProperties.WAREHOUSE_LOCATION, this.storageConfig.getWarehouseUri());
    catalog.initialize(CATALOG_NAME, properties);
    return catalog;
  }

}
