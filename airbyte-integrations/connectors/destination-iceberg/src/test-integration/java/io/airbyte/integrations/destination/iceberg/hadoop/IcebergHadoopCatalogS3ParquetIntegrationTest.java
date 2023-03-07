/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.hadoop;

import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;

/**
 * @author Leibniz on 2022/11/3.
 */
public class IcebergHadoopCatalogS3ParquetIntegrationTest extends BaseIcebergHadoopCatalogS3IntegrationTest {

  @Override
  DataFileFormat fileFormat() {
    return DataFileFormat.PARQUET;
  }

}
