/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfigurationFactory
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeSpecification
import java.nio.file.Files
import java.nio.file.Path
import org.apache.iceberg.catalog.Catalog

object GcsDataLakeTestUtil {
    val BIGLAKE_CONFIG_PATH: Path = Path.of("secrets/biglake.json")

    fun parseConfig(path: Path) =
        getConfig(
            ValidatedJsonUtils.parseOne(
                GcsDataLakeSpecification::class.java,
                Files.readString(path)
            )
        )

    fun getConfig(spec: ConfigurationSpecification) =
        GcsDataLakeConfigurationFactory()
            .makeWithoutExceptionHandling(spec as GcsDataLakeSpecification)

    fun getCatalog(
        config: GcsDataLakeConfiguration,
        tableIdGenerator: TableIdGenerator = SimpleTableIdGenerator(config.namespace),
    ): Catalog {
        // Create utility instances for test
        val icebergUtil = IcebergUtil(tableIdGenerator)
        val gcsDataLakeCatalogUtil = GcsDataLakeCatalogUtil(icebergUtil)

        val properties = gcsDataLakeCatalogUtil.toCatalogProperties(config)
        return icebergUtil.createCatalog(
            io.airbyte.integrations.destination.gcs_data_lake.spec.DEFAULT_CATALOG_NAME,
            properties
        )
    }
}
