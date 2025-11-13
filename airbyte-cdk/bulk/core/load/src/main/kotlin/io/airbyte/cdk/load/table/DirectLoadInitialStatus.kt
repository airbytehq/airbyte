/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table

data class DirectLoadInitialStatus(
    val realTable: DirectLoadTableStatus?,
    val tempTable: DirectLoadTableStatus?,
) : DatabaseInitialStatus

data class DirectLoadTableStatus(
    val isEmpty: Boolean,
)
