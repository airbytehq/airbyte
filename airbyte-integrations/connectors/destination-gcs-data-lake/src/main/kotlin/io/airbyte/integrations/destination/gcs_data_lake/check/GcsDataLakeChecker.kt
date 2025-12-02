/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.check

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableCleaner
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.TEST_TABLE
import jakarta.inject.Singleton
import java.util.UUID
import org.apache.iceberg.Schema
import org.apache.iceberg.types.Types

/**
 * Validates GCS Data Lake destination connectivity by creating and cleaning up a test Iceberg
 * table.
 *
 * This checker validates:
 * - Catalog connectivity (BigLake or Polaris)
 * - GCS bucket access and permissions
 * - Ability to create namespaces and tables
 * - Proper cleanup of test resources
 *
 * Uses UUID-based unique table names to prevent conflicts with:
 * - Concurrent check operations
 * - Stale metadata from previous test runs
 * - User tables with similar names
 */
@Singleton
class GcsDataLakeChecker(
    private val icebergTableCleaner: IcebergTableCleaner,
    private val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil,
    private val icebergUtil: IcebergUtil,
    private val tableIdGenerator: TableIdGenerator,
) : DestinationChecker<GcsDataLakeConfiguration> {

    override fun check(config: GcsDataLakeConfiguration) {
        catalogValidation(config)
    }

    /**
     * Validates catalog connectivity by creating a temporary test table and cleaning it up.
     *
     * Creates a uniquely-named test table in the configured namespace, then immediately cleans it
     * up. The cleanup is guaranteed via try-finally to prevent orphaned resources.
     *
     * @param config The GCS Data Lake destination configuration
     * @throws Exception if catalog validation fails (e.g., invalid credentials, missing
     * permissions)
     */
    private fun catalogValidation(config: GcsDataLakeConfiguration) {
        val catalogProperties = gcsDataLakeCatalogUtil.toCatalogProperties(config)
        val catalog =
            icebergUtil.createCatalog(
                io.airbyte.integrations.destination.gcs_data_lake.spec.DEFAULT_CATALOG_NAME,
                catalogProperties
            )

        // Get the default namespace from the configuration
        val defaultNamespace = config.namespace

        // Use a unique table name to avoid conflicts with existing tables or stale metadata
        val uniqueTestTableName = "${TEST_TABLE}_${UUID.randomUUID().toString().replace("-", "_")}"
        val testTableIdentifier =
            DestinationStream.Descriptor(defaultNamespace, uniqueTestTableName)

        val testTableSchema =
            Schema(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.optional(2, "data", Types.StringType.get()),
            )
        gcsDataLakeCatalogUtil.createNamespace(testTableIdentifier, catalog)

        var table: org.apache.iceberg.Table? = null
        try {
            table =
                icebergUtil.createTable(
                    testTableIdentifier,
                    catalog,
                    testTableSchema,
                )
        } finally {
            // Always cleanup test table, even if creation or validation fails
            table?.let {
                icebergTableCleaner.clearTable(
                    catalog,
                    tableIdGenerator.toTableIdentifier(testTableIdentifier),
                    it.io(),
                    it.location()
                )
            }
        }
    }
}
