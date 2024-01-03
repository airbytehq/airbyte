/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.nessie;

import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;
import org.junit.jupiter.api.BeforeAll;

public class IcebergNessieCatalogS3ParquetIntegrationTest extends BaseIcebergNessieCatalogS3IntegrationTest {

  @BeforeAll
  public static void startCompose() {
    startCompose(DataFileFormat.PARQUET);
  }

}
