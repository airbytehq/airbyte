/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table.directload

import io.airbyte.cdk.load.schema.model.TableName

data class DirectLoadTableExecutionConfig(
    val tableName: TableName,
)
