/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.jdbc;

import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;

/**
 * @author Leibniz on 2022/11/3.
 */
public class IcebergJdbcCatalogS3ParquetIntegrationTest extends BaseIcebergJdbcCatalogS3IntegrationTest {

  @Override
  DataFileFormat fileFormat() {
    return DataFileFormat.PARQUET;
  }

}
