/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.gcs_data_lake.io.GcsDataLakeUtil
import java.nio.file.Files
import java.nio.file.Path
import org.apache.iceberg.catalog.Catalog

object GcsDataLakeTestUtil {
    val GLUE_CONFIG_PATH: Path = Path.of("secrets/glue.json")

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

    fun getCatalog(config: GcsDataLakeConfiguration): Catalog {
        val icebergUtil = IcebergUtil(SimpleTableIdGenerator())
        val s3DataLakeUtil = GcsDataLakeUtil(icebergUtil)
        val props = s3DataLakeUtil.toCatalogProperties(config)
        return icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, props)
    }
}
