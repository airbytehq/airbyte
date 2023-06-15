package io.airbyte.integrations.destination.iceberg.config.catalog;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.CATALOG_NAME;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.GCS_PROJECT_ID_CONFIG_KEY;

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
import org.apache.iceberg.gcp.biglake.BigLakeCatalog;
import org.jetbrains.annotations.NotNull;

/**
 * @author Leibniz on 2022/11/1.
 */
@Data
@ToString(callSuper = true)
@EqualsAndHashCode(callSuper = false)
public class BigLakeCatalogConfig extends IcebergCatalogConfig {

  private final String biglake_project_id;

  public BigLakeCatalogConfig(@NotNull JsonNode catalogConfigJson) {
    this.biglake_project_id = catalogConfigJson.get(GCS_PROJECT_ID_CONFIG_KEY).asText();
  }

  @Override
  public Map<String, String> sparkConfigMap() {
    Map<String, String> configMap = new HashMap<>();
    configMap.put("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:1.2.0");
    configMap.put("spark.sql.catalog." + CATALOG_NAME, "org.apache.iceberg.spark.SparkCatalog");
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".catalog-impl", "org.apache.iceberg.gcp.biglake.BigLakeCatalog");

    configMap.putAll(this.storageConfig.sparkConfigMap(CATALOG_NAME));
    return configMap;
  }

  @Override
  public Catalog genCatalog() {
    BigLakeCatalog catalog = new BigLakeCatalog();
    Map<String, String> properties = new HashMap<>(this.storageConfig.catalogInitializeProperties());
    properties.put("spark.sql.catalog."+CATALOG_NAME+".gcp_project", this.biglake_project_id);
    catalog.initialize(CATALOG_NAME, properties);
    return catalog;
  }

}
