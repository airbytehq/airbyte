/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.catalog;

/**
 * @author Leibniz on 2022/10/31.
 */
public enum CatalogType {
  HIVE,
  HADOOP,
  JDBC
}
