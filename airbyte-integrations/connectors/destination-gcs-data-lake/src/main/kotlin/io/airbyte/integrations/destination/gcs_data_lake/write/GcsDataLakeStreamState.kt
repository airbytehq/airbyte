/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.PositionalDeleteIndex
import org.apache.iceberg.Schema
import org.apache.iceberg.Table

class GcsDataLakeStreamState(
    val table: Table,
    val schema: Schema,
    val stagingBranchName: String,
    val positionalDeleteIndex: PositionalDeleteIndex? = null,
    val baseSnapshotId: Long? = null,
)
