/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.migrations

import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState

// Note the nonnullable fields. Even though the underlying storage medium (a JSON blob) supports
// nullability, we don't want to deal with that in our codebase.
data class SnowflakeState(val needsSoftReset: Boolean, val isAirbyteMetaPresentInRaw: Boolean) :
    MinimumDestinationState {
    override fun needsSoftReset(): Boolean {
        return needsSoftReset
    }

    @Suppress("UNCHECKED_CAST")
    override fun <T : MinimumDestinationState> withSoftReset(needsSoftReset: Boolean): T {
        return copy(needsSoftReset = needsSoftReset) as T
    }
}
