/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table

import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatus

data class DirectLoadInitialStatus(
    val realTable: DirectLoadTableStatus?,
    val tempTable: DirectLoadTableStatus?,
) : DatabaseInitialStatus

data class DirectLoadTableStatus(
    val isEmpty: Boolean,
)
