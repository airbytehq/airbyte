package io.airbyte.integrations.destination.bigquery.typing_deduping

import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState

data class BigqueryState(val needsSoftReset: Boolean): MinimumDestinationState {
  override fun needsSoftReset(): Boolean {
    return needsSoftReset
  }

  override fun <T : MinimumDestinationState> withSoftReset(needsSoftReset: Boolean): T {
    return copy(needsSoftReset = needsSoftReset) as T
  }
}
