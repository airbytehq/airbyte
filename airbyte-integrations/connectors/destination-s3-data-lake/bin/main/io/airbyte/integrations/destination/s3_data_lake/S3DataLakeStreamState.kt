/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import org.apache.iceberg.Schema
import org.apache.iceberg.Table

class S3DataLakeStreamState(
    val table: Table,
    val schema: Schema,
)
