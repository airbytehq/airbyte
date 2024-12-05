/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.hadoop;

import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;
import org.junit.jupiter.api.BeforeAll;

/**
 * @author Leibniz on 2022/11/3.
 */
public class IcebergHadoopCatalogS3AvroIntegrationTest extends BaseIcebergHadoopCatalogS3IntegrationTest {

  @Override
  DataFileFormat fileFormat() {
    return DataFileFormat.AVRO;
  }

  @BeforeAll
  public static void start() {
    start(DataFileFormat.AVRO);
  }

}
