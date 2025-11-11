/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.NessieCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.PolarisCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.RestCatalogConfiguration
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableCleaner
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import jakarta.inject.Singleton
import java.util.UUID
import org.apache.iceberg.Schema
import org.apache.iceberg.types.Types

/**
 * Validates S3 Data Lake destination connectivity by creating and cleaning up a test Iceberg table.
 *
 * This checker validates:
 * - Catalog connectivity (Glue, Nessie, or REST)
 * - S3 bucket access and permissions
 * - Ability to create namespaces and tables
 * - Proper cleanup of test resources
 *
 * Uses UUID-based unique table names to prevent conflicts with:
 * - Concurrent check operations
 * - Stale metadata from previous test runs
 * - User tables with similar names
 */
@Singleton
class S3DataLakeChecker(
    private val icebergTableCleaner: IcebergTableCleaner,
    private val s3DataLakeUtil: S3DataLakeUtil,
    private val icebergUtil: IcebergUtil,
    private val tableIdGenerator: TableIdGenerator,
) : DestinationChecker<S3DataLakeConfiguration> {

    override fun check(config: S3DataLakeConfiguration) {
        catalogValidation(config)
    }

    /**
     * Validates catalog connectivity by creating a temporary test table and cleaning it up.
     *
     * Creates a uniquely-named test table in the configured namespace, then immediately cleans it
     * up. The cleanup is guaranteed via try-finally to prevent orphaned resources.
     *
     * @param config The S3 Data Lake destination configuration
     * @throws Exception if catalog validation fails (e.g., invalid credentials, missing
     * permissions)
     */
    private fun catalogValidation(config: S3DataLakeConfiguration) {
        val catalogProperties = s3DataLakeUtil.toCatalogProperties(config)
        val catalog = icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, catalogProperties)

        val defaultNamespace =
            config.icebergCatalogConfiguration.catalogConfiguration.let {
                when (it) {
                    is GlueCatalogConfiguration -> it.databaseName
                    is NessieCatalogConfiguration -> it.namespace
                    is RestCatalogConfiguration, -> it.namespace
                    is PolarisCatalogConfiguration -> it.namespace
                }
            }

        // Use a unique table name to avoid conflicts with existing tables or stale metadata
        val uniqueTestTableName = "${TEST_TABLE}_${UUID.randomUUID().toString().replace("-", "_")}"
        val testTableIdentifier =
            DestinationStream.Descriptor(defaultNamespace, uniqueTestTableName)

        val testTableSchema =
            Schema(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.optional(2, "data", Types.StringType.get()),
            )
        s3DataLakeUtil.createNamespaceWithGlueHandling(testTableIdentifier, catalog)

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
