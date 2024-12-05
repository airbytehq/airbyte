/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping.migrators

import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig

/**
 * Migrations may do two things:
 * 1. Modify the raw table
 * 2. Trigger a soft reset
 *
 * The raw table modification should happen in {@link #migrateIfNecessary(Object, StreamConfig)}.
 * However, if multiple migrations want to trigger a soft reset, we should only trigger a single
 * soft reset, because soft resets are idempotent. There's no reason to trigger multiple soft resets
 * in sequence, and it would be a waste of warehouse compute to do so. Migrations MUST NOT directly
 * run a soft reset within {@link #migrateIfNecessary(Object, StreamConfig)}. <p> Migrations are
 * encouraged to store something into the destination State blob. This allows us to make fewer
 * queries into customer data. However, migrations MUST NOT rely solely on the state blob to trigger
 * migrations. It's possible for a state to not be committed after a migration runs (e.g. a
 * well-timed OOMKill). Therefore, if the state blob indicates that a migration is necessary,
 * migrations must still confirm against the database that the migration is necessary.
 */
interface Migration<DestinationState : MinimumDestinationState> {

    /**
     * Perform the migration if it's necessary. Implementations of this method MUST check against
     * the database to confirm the the migration is still necessary, in case a previous migration
     * ran, but failed to update the state.
     *
     * Migrations MUST NOT set the `needsSoftReset` flag to false, but they MAY set it to true.
     */
    fun migrateIfNecessary(
        destinationHandler: DestinationHandler<DestinationState>,
        stream: StreamConfig,
        state: DestinationInitialStatus<DestinationState>
    ): MigrationResult<DestinationState>

    /**
     * @param invalidateInitialState If true, the migration modified the raw tables in a way that
     * requires us to re-gather initial state.
     */
    data class MigrationResult<DestinationState>(
        val updatedDestinationState: DestinationState,
        val invalidateInitialState: Boolean
    )
}
