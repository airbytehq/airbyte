/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.test.util.FullTableSchema
import io.airbyte.cdk.load.test.util.SchemaDumper
import io.airbyte.integrations.destination.redshift2.client.RedshiftAirbyteClient
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfigurationFactory
import io.airbyte.integrations.destination.redshift2.config.RedshiftSpecification
import io.airbyte.integrations.destination.redshift2.connect.RedshiftConnect
import io.airbyte.integrations.destination.redshift2.sql.RedshiftSqlGenerator

/**
 * [SchemaDumper] implementation for Redshift regression tests. Creates a [RedshiftAirbyteClient]
 * from the test config and delegates to [RedshiftAirbyteClient.discoverSchema].
 */
class RedshiftSchemaDumper(spec: ConfigurationSpecification) : SchemaDumper {
    private val config =
        RedshiftConfigurationFactory().makeWithoutExceptionHandling(spec as RedshiftSpecification)
    private val dataSource = RedshiftConnect(config).createDataSource()
    private val sqlGenerator = RedshiftSqlGenerator()
    private val airbyteClient =
        RedshiftAirbyteClient(
            dataSource,
            sqlGenerator,
            // S3 client is not needed for schema discovery; pass a no-op stub
            software.amazon.awssdk.services.s3.S3Client.builder()
                .region(software.amazon.awssdk.regions.Region.US_EAST_1)
                .build(),
        )

    override suspend fun discoverSchema(namespace: String?, name: String): FullTableSchema {
        val tableName = TableName(namespace ?: config.schema, name)
        val tableSchema = airbyteClient.discoverSchema(tableName)
        return FullTableSchema(tableSchema)
    }
}
