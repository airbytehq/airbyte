/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.aws.AwsToolkitConstants
import io.airbyte.cdk.load.schema.ColumnNameResolver
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.s3_data_lake.schema.S3DataLakeTableSchemaMapper
import io.micronaut.context.ApplicationContext
import io.micronaut.context.env.Environment
import kotlin.test.assertEquals
import kotlin.test.assertIs
import org.junit.jupiter.api.Test

/**
 * Boots the connector's Micronaut context (no network access) and checks that the schema mapping
 * beans resolve. In particular, the CDK ships its own `DefaultTempTableNameGenerator` singleton, so
 * this guards against ambiguous [TempTableNameGenerator] candidates.
 */
internal class S3DataLakeBeanWiringTest {
    private fun <T> withContext(
        lowercaseColumnNames: Boolean,
        block: (ApplicationContext) -> T
    ): T {
        val config =
            """
            {
              "access_key_id": "access-key",
              "secret_access_key": "secret-key",
              "s3_bucket_name": "bucket",
              "s3_bucket_region": "us-east-1",
              "warehouse_location": "s3://bucket/warehouse",
              "main_branch_name": "main",
              "catalog_type": {
                "catalog_type": "GLUE",
                "glue_id": "123456789012",
                "database_name": "Default_DB"
              },
              "lowercase_column_names": $lowercaseColumnNames
            }
            """.trimIndent()
        return ApplicationContext.run(
                mapOf(
                    "airbyte.connector.operation" to "write",
                    "airbyte.connector.config.json" to config,
                ),
                Environment.TEST,
                AwsToolkitConstants.MICRONAUT_ENVIRONMENT,
            )
            .use(block)
    }

    @Test
    fun `schema mapping beans resolve to the connector mapper`() =
        withContext(lowercaseColumnNames = true) { context ->
            val mapper = context.getBean(TableSchemaMapper::class.java)
            assertIs<S3DataLakeTableSchemaMapper>(mapper)
            assertEquals("urls", mapper.toColumnName("URLs"))
            assertEquals(
                TableName("default_db", "my_table"),
                mapper.toFinalTableName(DestinationStream.Descriptor(null, "My-Table")),
            )
            // Beans that consume the mapper (and its TempTableNameGenerator dependency).
            context.getBean(TempTableNameGenerator::class.java)
            context.getBean(TableSchemaFactory::class.java)
            assertEquals(
                mapOf("ID" to "id", "id" to "id_1"),
                context
                    .getBean(ColumnNameResolver::class.java)
                    .getColumnNameMapping(linkedSetOf("ID", "id")),
            )
        }

    @Test
    fun `column names pass through when the option is disabled`() =
        withContext(lowercaseColumnNames = false) { context ->
            assertEquals(
                "URLs",
                context.getBean(TableSchemaMapper::class.java).toColumnName("URLs")
            )
        }
}
