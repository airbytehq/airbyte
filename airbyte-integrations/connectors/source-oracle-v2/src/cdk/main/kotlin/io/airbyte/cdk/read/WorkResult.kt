/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

/** The output of a [Worker]. */
data class WorkResult<K : Key, I : State<K>, O : State<K>>(
    val input: I,
    val output: O,
    val numRecords: Long
)
