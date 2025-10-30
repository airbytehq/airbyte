/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.data.icerberg.parquet.IcebergWriteTest
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeSpecification
import java.nio.file.Files
import org.junit.jupiter.api.Test

class BigLakeWriteTest :
    IcebergWriteTest(
        configContents = Files.readString(GcsDataLakeTestUtil.BIGLAKE_CONFIG_PATH),
        configSpecClass = GcsDataLakeSpecification::class.java,
        getCatalog = { spec ->
            GcsDataLakeTestUtil.getCatalog(GcsDataLakeTestUtil.getConfig(spec))
        },
        destinationCleaner = NoopDestinationCleaner, // TODO: Implement proper cleaner
        tableIdGenerator = SimpleTableIdGenerator("test_database"),
    ) {

    @Test
    override fun testBasicTypes() {
        super.testBasicTypes()
    }

    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}
