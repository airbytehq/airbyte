package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.read.CdcSharedState
import io.airbyte.cdk.read.DefaultCdcSharedState
import io.airbyte.cdk.read.JdbcSharedState

public fun JdbcSharedState.toCdcSharedState(): CdcSharedState {
    return DefaultCdcSharedState(this.configuration)
}
