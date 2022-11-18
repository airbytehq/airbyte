/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.storage;

import java.util.Map;

/**
 * @author Leibniz on 2022/10/31.
 */
public interface StorageConfig {

  /**
   * Checks about read, write, privileges
   *
   * @throws Exception maybe IOException
   */
  void check() throws Exception;

  String getWarehouseUri();

  /**
   * append Spark storage configurations for Iceberg, including (but not limited to): 1.
   * spark.sql.catalog.{catalogName}.xxx = yyy 2. spark.hadoop.fs.xxx = yyy
   *
   * @param catalogName name of Iceberg catalog
   * @return a configuration Map to build Spark Session
   */
  Map<String, String> sparkConfigMap(String catalogName);

  /**
   * append storage configurations for Iceberg Catalog For calling
   * org.apache.iceberg.catalog.Catalog#initialize()
   *
   * @return a configuration Map to build Catalog(org.apache.iceberg.catalog.Catalog)
   */
  Map<String, String> catalogInitializeProperties();

}
