/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.jdbc;

import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;

/**
 * @author Leibniz on 2022/11/3.
 */
public class IcebergJdbcCatalogS3AvroIntegrationTest extends BaseIcebergJdbcCatalogS3IntegrationTest {

  @Override
  DataFileFormat fileFormat() {
    return DataFileFormat.AVRO;
  }

}
