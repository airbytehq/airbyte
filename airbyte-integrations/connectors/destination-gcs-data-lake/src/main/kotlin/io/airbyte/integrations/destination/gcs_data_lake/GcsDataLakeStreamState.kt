/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import org.apache.iceberg.Schema
import org.apache.iceberg.Table

class GcsDataLakeStreamState(
    val table: Table,
    val schema: Schema,
)
