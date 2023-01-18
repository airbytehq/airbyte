/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.catalog;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.CATALOG_NAME;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.JDBC_CATALOG_SCHEMA_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.JDBC_PASSWORD_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.JDBC_SSL_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.JDBC_URL_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.JDBC_USERNAME_CONFIG_KEY;
import static org.apache.commons.lang3.StringUtils.isNotBlank;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.HashMap;
import java.util.Map;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.ToString;
import org.apache.iceberg.CatalogProperties;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.jdbc.JdbcCatalog;
import org.jetbrains.annotations.NotNull;

/**
 * @author Leibniz on 2022/11/1.
 */
@Data
@ToString(callSuper = true)
@EqualsAndHashCode(callSuper = false)
public class JdbcCatalogConfig extends IcebergCatalogConfig {

  private final String jdbcUrl;
  private final String user;
  private final String password;
  private final boolean verifyServerCertificate;
  private final boolean useSSL;
  private final String catalogSchema;

  public JdbcCatalogConfig(@NotNull JsonNode catalogConfig) {
    this.jdbcUrl = catalogConfig.get(JDBC_URL_CONFIG_KEY).asText();
    this.user = catalogConfig.get(JDBC_USERNAME_CONFIG_KEY).asText();
    this.password = catalogConfig.get(JDBC_PASSWORD_CONFIG_KEY).asText();
    // TODO
    this.verifyServerCertificate = false;
    this.useSSL = catalogConfig.get(JDBC_SSL_CONFIG_KEY).asBoolean();
    this.catalogSchema = catalogConfig.get(JDBC_CATALOG_SCHEMA_CONFIG_KEY).asText();
  }

  @Override
  public Map<String, String> sparkConfigMap() {
    Map<String, String> configMap = new HashMap<>();
    configMap.put("spark.network.timeout", "300000");
    configMap.put("spark.sql.defaultCatalog", CATALOG_NAME);
    configMap.put("spark.sql.catalog." + CATALOG_NAME, "org.apache.iceberg.spark.SparkCatalog");
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".catalog-impl", "org.apache.iceberg.jdbc.JdbcCatalog");
    configMap.put("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions");
    configMap.put("spark.driver.extraJavaOptions", "-Dpackaging.type=jar -Djava.io.tmpdir=/tmp");

    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".uri", this.jdbcUrl);
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".jdbc.verifyServerCertificate",
        String.valueOf(this.verifyServerCertificate));
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".jdbc.useSSL", String.valueOf(this.useSSL));
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".jdbc.user", this.user);
    configMap.put("spark.sql.catalog." + CATALOG_NAME + ".jdbc.password", this.password);
    if (isNotBlank(this.catalogSchema)) {
      configMap.put("spark.sql.catalog." + CATALOG_NAME + ".jdbc.currentSchema", this.catalogSchema);
    }

    configMap.putAll(this.storageConfig.sparkConfigMap(CATALOG_NAME));
    return configMap;
  }

  @Override
  public Catalog genCatalog() {
    JdbcCatalog catalog = new JdbcCatalog();
    Map<String, String> properties = new HashMap<>(this.storageConfig.catalogInitializeProperties());
    properties.put(CatalogProperties.URI, this.jdbcUrl);
    properties.put(JdbcCatalog.PROPERTY_PREFIX + "user", this.user);
    properties.put(JdbcCatalog.PROPERTY_PREFIX + "password", this.password);
    properties.put(JdbcCatalog.PROPERTY_PREFIX + "useSSL", String.valueOf(this.useSSL));
    properties.put(JdbcCatalog.PROPERTY_PREFIX + "verifyServerCertificate",
        String.valueOf(this.verifyServerCertificate));
    if (isNotBlank(this.catalogSchema)) {
      properties.put(JdbcCatalog.PROPERTY_PREFIX + "currentSchema", this.catalogSchema);
    }
    properties.put(CatalogProperties.WAREHOUSE_LOCATION, this.storageConfig.getWarehouseUri());
    catalog.initialize(CATALOG_NAME, properties);
    return catalog;
  }

}
