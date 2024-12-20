/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.glue;

import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;

public class IcebergGlueCatalogS3AvroIntegrationTest extends BaseIcebergGlueCatalogS3IntegrationTest {

  @Override
  public DataFileFormat getFormat() {
    return DataFileFormat.AVRO;
  }

}
