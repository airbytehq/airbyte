/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.protocol.models.v0.StreamDescriptor

/*
 * This class wants to do three separate things, but not all of them actually happen here right now:
 * * A migration runner, which handles any changes in raw tables (#prepareSchemasAndRawTables) * A
 * raw table creator, which creates any missing raw tables (currently handled in e.g.
 * GeneralStagingFunctions.onStartFunction, BigQueryStagingConsumerFactory.onStartFunction, etc.) *
 * A T+D runner, which manages the final tables (#prepareFinalTables, #typeAndDedupe, etc.)
 *
 * These would be injectable to the relevant locations, so that we can have: * DV2 destinations with
 * T+D enabled (i.e. all three objects instantiated for real) * DV2 destinations with T+D disabled
 * (i.e. noop T+D runner but the other two objects for real) * DV1 destinations (i.e. all three
 * objects as noop)
 *
 * Even more ideally, we'd create an instance per stream, instead of having one instance for the
 * entire sync. This would massively simplify all the state contained in our implementations - see
 * DefaultTyperDeduper's pile of Sets and Maps.
 *
 * Unfortunately, it's just a pain to inject these objects to everywhere they need to be, and we'd
 * need to refactor part of the async framework on top of that. There's an obvious overlap with the
 * async framework's onStart function... which we should deal with eventually.
 */
interface TyperDeduper {
    /**
     * Does two things: Set up the schemas for the sync (both airbyte_internal and final table
     * schemas), and execute any raw table migrations. These migrations might include: Upgrading v1
     * raw tables to v2, adding a column to the raw tables, etc. In general, this method shouldn't
     * actually create the raw tables; the only exception is in the V1 -> V2 migration.
     *
     * This method should be called BEFORE creating raw tables, because the V1V2 migration might
     * create the raw tables.
     *
     * This method may affect the behavior of [.prepareFinalTables]. For example, modifying a raw
     * table may require us to run a soft reset. However, we should defer that soft reset until
     * [.prepareFinalTables].
     */
    @Throws(Exception::class) fun prepareSchemasAndRunMigrations()

    /**
     * Create the tables that T+D will write to during the sync. In OVERWRITE mode, these might not
     * be the true final tables. Specifically, other than an initial sync (i.e. table does not
     * exist, or is empty) we write to a temporary final table, and swap it into the true final
     * table at the end of the sync. This is to prevent user downtime during a sync.
     *
     * This method should be called AFTER creating the raw tables, because it may run a soft reset
     * (which requires the raw tables to exist).
     */
    @Throws(Exception::class) fun prepareFinalTables()

    /**
     * Execute typing and deduping for a single stream (i.e. fetch new raw records into the final
     * table, etc.).
     *
     * @param originalNamespace The stream's namespace, as declared in the configured catalog
     * @param originalName The stream's name, as declared in the configured catalog
     */
    @Throws(Exception::class) fun typeAndDedupe(originalNamespace: String, originalName: String)

    /**
     * Does any "end of sync" work. For most streams, this is a noop.
     *
     * For OVERWRITE streams where we're writing to a temp table, this is where we swap the temp
     * table into the final table.
     *
     * @param streamSyncSummaries Information about what happened during the sync. Implementations
     * SHOULD use this information to skip T+D when possible (this is not a requirement for
     * correctness, but does allow us to save time/money). This parameter MUST NOT be null.
     */
    @Throws(Exception::class)
    fun typeAndDedupe(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>)

    @Throws(Exception::class) fun commitFinalTables()

    fun cleanup()
}
