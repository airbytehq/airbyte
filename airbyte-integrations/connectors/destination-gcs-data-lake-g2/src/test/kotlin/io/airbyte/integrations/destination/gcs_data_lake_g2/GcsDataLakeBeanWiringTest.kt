/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake_g2

import io.airbyte.cdk.load.data.iceberg.parquet.IcebergObjectMode
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergSchemaOptions
import io.micronaut.context.ApplicationContext
import io.micronaut.context.env.Environment
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

internal class GcsDataLakeBeanWiringTest {
    @Test
    fun `Iceberg utility uses typed object mode`() {
        ApplicationContext.run(Environment.TEST).use { context ->
            assertEquals(
                IcebergObjectMode.STRUCT,
                context.getBean(IcebergSchemaOptions::class.java).objectMode,
            )
        }
    }
}
