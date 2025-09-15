/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table

import io.airbyte.cdk.load.orchestration.db.TableName

data class DirectLoadTableExecutionConfig(
    val tableName: TableName,
)
