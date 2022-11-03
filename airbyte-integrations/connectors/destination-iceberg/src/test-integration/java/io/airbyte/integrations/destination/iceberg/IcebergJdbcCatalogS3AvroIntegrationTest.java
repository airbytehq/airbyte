package io.airbyte.integrations.destination.iceberg;

import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;

/**
 * @author Leibniz on 2022/11/3.
 */
public class IcebergJdbcCatalogS3AvroIntegrationTest extends AbstractIcebergJdbcCatalogS3IntegrationTest {

    @Override
    DataFileFormat fileFormat() {
        return DataFileFormat.AVRO;
    }
}
