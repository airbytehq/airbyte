/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.catalog;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.CATALOG_NAME;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.REST_CATALOG_CREDENTIAL_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.REST_CATALOG_TOKEN_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.REST_CATALOG_URI_CONFIG_KEY;
import static org.apache.commons.lang3.StringUtils.isNotBlank;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.HashMap;
import java.util.Map;

import com.google.common.base.Preconditions;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.ToString;
import org.apache.iceberg.CatalogProperties;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.rest.RESTCatalog;
import org.apache.iceberg.rest.auth.OAuth2Properties;
import org.jetbrains.annotations.NotNull;

@Data
@ToString(callSuper = true)
@EqualsAndHashCode(callSuper = false)
public class RESTCatalogConfig
        extends IcebergCatalogConfig {

  private final String uri;
  private final String credential;
  private final String token;

  public RESTCatalogConfig(@NotNull JsonNode catalogConfig) {
    Preconditions.checkArgument(null != catalogConfig.get(REST_CATALOG_URI_CONFIG_KEY), "%s is required", REST_CATALOG_URI_CONFIG_KEY);
    this.uri = catalogConfig.get(REST_CATALOG_URI_CONFIG_KEY).asText();
    JsonNode credentialNode = catalogConfig.get(REST_CATALOG_CREDENTIAL_CONFIG_KEY);
    JsonNode tokenNode = catalogConfig.get(REST_CATALOG_TOKEN_CONFIG_KEY);
    this.credential = null != credentialNode ? credentialNode.asText() : null;
    this.token = null != tokenNode ? tokenNode.asText() : null;
  }

  @Override
  public Map<String, String> sparkConfigMap() {
    Map<String, String> configMap = new HashMap<>();
    configMap.put("spark.network.timeout", "300000");
    configMap.put("spark.sql.defaultCatalog", CATALOG_NAME);
    configMap.put("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions");
    configMap.put("spark.sql.catalog." + CATALOG_NAME, "org.apache.iceberg.spark.SparkCatalog");
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".catalog-impl", "org.apache.iceberg.rest.RESTCatalog");
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".uri", this.uri);
    configMap.put("spark.driver.extraJavaOptions", "-Dpackaging.type=jar -Djava.io.tmpdir=/tmp");

    if (isNotBlank(this.credential)) {
      configMap.put("spark.sql.catalog." + CATALOG_NAME + ".credential", this.credential);
    }
    if (isNotBlank(this.token)) {
      configMap.put("spark.sql.catalog." + CATALOG_NAME + ".token", this.token);
    }

    configMap.putAll(this.storageConfig.sparkConfigMap(CATALOG_NAME));
    return configMap;
  }

  @Override
  public Catalog genCatalog() {
    RESTCatalog catalog = new RESTCatalog();
    Map<String, String> properties = new HashMap<>(this.storageConfig.catalogInitializeProperties());
    properties.put(CatalogProperties.URI, this.uri);
    if (isNotBlank(this.credential)) {
      properties.put(OAuth2Properties.CREDENTIAL, this.credential);
    }
    if (isNotBlank(this.token)) {
      properties.put(OAuth2Properties.TOKEN, this.token);
    }
    catalog.initialize(CATALOG_NAME, properties);
    return catalog;
  }
}
