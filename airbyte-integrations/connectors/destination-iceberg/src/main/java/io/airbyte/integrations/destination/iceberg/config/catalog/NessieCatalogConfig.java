/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.catalog;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.CATALOG_NAME;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.NESSIE_CATALOG_REFERENCE_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.NESSIE_CATALOG_TOKEN_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.NESSIE_CATALOG_URI_CONFIG_KEY;
import static org.apache.commons.lang3.StringUtils.isNotBlank;
import static org.projectnessie.client.NessieConfigConstants.CONF_NESSIE_AUTH_TOKEN;
import static org.projectnessie.client.NessieConfigConstants.CONF_NESSIE_AUTH_TYPE;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import java.util.HashMap;
import java.util.Map;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.ToString;
import org.apache.iceberg.CatalogProperties;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.nessie.NessieCatalog;
import org.jetbrains.annotations.NotNull;

@Data
@ToString(callSuper = true)
@EqualsAndHashCode(callSuper = false)
public class NessieCatalogConfig
    extends IcebergCatalogConfig {

  private final String uri;
  private final String ref;
  private final String token;

  public NessieCatalogConfig(@NotNull JsonNode catalogConfig) {
    Preconditions.checkArgument(null != catalogConfig.get(NESSIE_CATALOG_URI_CONFIG_KEY), "%s is required", NESSIE_CATALOG_URI_CONFIG_KEY);
    JsonNode refNode = catalogConfig.get(NESSIE_CATALOG_REFERENCE_KEY);
    JsonNode tokenNode = catalogConfig.get(NESSIE_CATALOG_TOKEN_CONFIG_KEY);
    this.uri = catalogConfig.get(NESSIE_CATALOG_URI_CONFIG_KEY).asText();
    this.ref = null != refNode ? refNode.asText() : null;
    this.token = null != tokenNode ? tokenNode.asText() : null;
  }

  @Override
  public Map<String, String> sparkConfigMap() {
    Map<String, String> configMap = new HashMap<>();
    configMap.put("spark.network.timeout", "300000");
    configMap.put("spark.sql.defaultCatalog", CATALOG_NAME);
    configMap.put("spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions");
    configMap.put("spark.sql.catalog." + CATALOG_NAME, "org.apache.iceberg.spark.SparkCatalog");
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".catalog-impl", "org.apache.iceberg.nessie.NessieCatalog");
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".uri", this.uri);
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".ref", this.ref);
    configMap.put("spark.driver.extraJavaOptions", "-Dpackaging.type=jar -Djava.io.tmpdir=/tmp");

    if (isNotBlank(this.token)) {
      configMap.put("spark.sql.catalog." + CATALOG_NAME + ".authentication.type", "BEARER");
      configMap.put("spark.sql.catalog." + CATALOG_NAME + ".authentication.token", this.token);
    }

    configMap.putAll(this.storageConfig.sparkConfigMap(CATALOG_NAME));
    return configMap;
  }

  @Override
  public Catalog genCatalog() {
    NessieCatalog catalog = new NessieCatalog();
    Map<String, String> properties = new HashMap<>(this.storageConfig.catalogInitializeProperties());
    properties.put(CatalogProperties.URI, this.uri);
    properties.put(CatalogProperties.WAREHOUSE_LOCATION, this.storageConfig.getWarehouseUri());
    if (isNotBlank(this.ref)) {
      properties.put("ref", this.ref);
    }

    if (isNotBlank(this.token)) {
      properties.put(CONF_NESSIE_AUTH_TYPE, "BEARER");
      properties.put(CONF_NESSIE_AUTH_TOKEN, this.token);
    }

    catalog.initialize(CATALOG_NAME, properties);
    return catalog;
  }

}
