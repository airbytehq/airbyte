package io.airbyte.integrations.destination.iceberg;

import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;

/**
 * @author Leibniz on 2022/11/3.
 */
public class IcebergHadoopCatalogS3ParquetIntegrationTest extends AbstractIcebergHadoopCatalogS3IntegrationTest {

    @Override
    DataFileFormat fileFormat() {
        return DataFileFormat.PARQUET;
    }
}
