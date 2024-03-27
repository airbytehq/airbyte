/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.cdk.integrations.destination.StreamSyncSummary;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Map;
import java.util.concurrent.locks.Lock;

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
public interface TyperDeduper {

  /**
   * Does two things: Set up the schemas for the sync (both airbyte_internal and final table schemas),
   * and execute any raw table migrations. These migrations might include: Upgrading v1 raw tables to
   * v2, adding a column to the raw tables, etc. In general, this method shouldn't actually create the
   * raw tables; the only exception is in the V1 -> V2 migration.
   * <p>
   * This method should be called BEFORE creating raw tables, because the V1V2 migration might create
   * the raw tables.
   * <p>
   * This method may affect the behavior of {@link #prepareFinalTables()}. For example, modifying a
   * raw table may require us to run a soft reset. However, we should defer that soft reset until
   * {@link #prepareFinalTables()}.
   */
  void prepareSchemasAndRunMigrations() throws Exception;

  /**
   * Create the tables that T+D will write to during the sync. In OVERWRITE mode, these might not be
   * the true final tables. Specifically, other than an initial sync (i.e. table does not exist, or is
   * empty) we write to a temporary final table, and swap it into the true final table at the end of
   * the sync. This is to prevent user downtime during a sync.
   * <p>
   * This method should be called AFTER creating the raw tables, because it may run a soft reset
   * (which requires the raw tables to exist).
   */
  void prepareFinalTables() throws Exception;

  /**
   * Suggest that we execute typing and deduping for a single stream (i.e. fetch new raw records into
   * the final table, etc.).
   * <p>
   * This method is thread-safe; multiple threads can call it concurrently. If T+D is already running
   * for the given stream, this method may choose to do nothing. If a caller wishes to force T+D to
   * run (for example, at the end of a sync), they may set {@code mustRun} to true.
   * <p>
   * This method relies on callers to prevent concurrent modification to the underlying raw tables.
   * This is most easily accomplished using {@link #getRawTableInsertLock(String, String)}, if the
   * caller guards all raw table writes using {@code getRawTableInsertLock().lock()} and
   * {@code getRawTableInsertLock().unlock()}. While {@code typeAndDedupe} is executing, that lock
   * will be unavailable. However, callers are free to enforce this in other ways (for example,
   * single- threaded callers do not need to use the lock).
   *
   * @param originalNamespace The stream's namespace, as declared in the configured catalog
   * @param originalName The stream's name, as declared in the configured catalog
   */
  void typeAndDedupe(String originalNamespace, String originalName, boolean mustRun) throws Exception;

  /**
   * Get the lock that should be used to synchronize inserts to the raw table for a given stream. This
   * lock permits any number of threads to hold the lock, but
   * {@link #typeAndDedupe(String, String, boolean)} will not proceed while this lock is held.
   * <p>
   * This lock provides fairness guarantees, i.e. typeAndDedupe will not starve while waiting for the
   * lock (and similarly, raw table writers will not starve if many typeAndDedupe calls are queued).
   */
  Lock getRawTableInsertLock(final String originalNamespace, final String originalName);

  /**
   * Does any "end of sync" work. For most streams, this is a noop.
   * <p>
   * For OVERWRITE streams where we're writing to a temp table, this is where we swap the temp table
   * into the final table.
   *
   * @param streamSyncSummaries Information about what happened during the sync. Implementations
   *        SHOULD use this information to skip T+D when possible (this is not a requirement for
   *        correctness, but does allow us to save time/money). This parameter MUST NOT be null.
   *        Streams MAY be omitted, which will be treated as though they were mapped to
   *        {@link StreamSyncSummary#DEFAULT}.
   */
  void typeAndDedupe(Map<StreamDescriptor, StreamSyncSummary> streamSyncSummaries) throws Exception;

  void commitFinalTables() throws Exception;

  void cleanup();

}
