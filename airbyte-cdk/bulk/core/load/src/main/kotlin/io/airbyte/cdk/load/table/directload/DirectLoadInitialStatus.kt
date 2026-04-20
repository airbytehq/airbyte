/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table.directload

import io.airbyte.cdk.load.table.DatabaseInitialStatus

data class DirectLoadInitialStatus(
    val realTable: DirectLoadTableStatus?,
    val tempTable: DirectLoadTableStatus?,
) : DatabaseInitialStatus

data class DirectLoadTableStatus(
    val isEmpty: Boolean,
)
