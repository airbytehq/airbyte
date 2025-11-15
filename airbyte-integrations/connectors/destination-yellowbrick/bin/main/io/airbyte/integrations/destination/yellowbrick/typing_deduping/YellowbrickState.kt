/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yellowbrick.typing_deduping

import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState

data class YellowbrickState(val needsSoftReset: Boolean) : MinimumDestinationState {
    override fun needsSoftReset(): Boolean {
        return needsSoftReset
    }

    @Suppress("UNCHECKED_CAST")
    override fun <T : MinimumDestinationState> withSoftReset(needsSoftReset: Boolean): T {
        return copy(needsSoftReset = needsSoftReset) as T
    }
}
