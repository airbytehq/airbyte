/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.concurrent.locks.Lock;

public interface TyperDeduper {

  /**
   * Create the tables that T+D will write to during the sync. In OVERWRITE mode, these might not be
   * the true final tables. Specifically, other than an initial sync (i.e. table does not exist, or is
   * empty) we write to a temporary final table, and swap it into the true final table at the end of
   * the sync. This is to prevent user downtime during a sync.
   */
  void prepareTables() throws Exception;

  /**
   * Suggest that we execute typing and deduping for a single stream (i.e. fetch new raw records into
   * the final table, etc.).
   * <p>
   * This method is thread-safe; multiple threads can call it concurrently. If T+D is already running
   * for the given stream, this method may choose to do nothing.
   * <p>
   * This method relies on callers to prevent concurrent modification to the underlying raw tables
   * using {@link #getRawTableInsertLock(String, String)}. Raw table writes should be guarded by
   * {@code getRawTableInsertLock().lock()} and {@code getRawTableInsertLock().unlock()}. While
   * {@code typeAndDedupe} is executing, that lock will be unavailable. This is typically implemented
   * using a {@link java.util.concurrent.locks.ReentrantReadWriteLock} with fairness enabled.
   *
   * @param originalNamespace The stream's namespace, as declared in the configured catalog
   * @param originalName The stream's name, as declared in the configured catalog
   */
  void typeAndDedupe(String originalNamespace, String originalName) throws Exception;

  /**
   * Get the lock that should be used to synchronize inserts to the raw table for a given stream.
   * {@link #typeAndDedupe(String, String)} will not run while this lock is held.
   */
  Lock getRawTableInsertLock(final String originalNamespace, final String originalName);

  /**
   * Does any "end of sync" work. For most streams, this is a noop.
   * <p>
   * For OVERWRITE streams where we're writing to a temp table, this is where we swap the temp table
   * into the final table.
   */
  void commitFinalTables() throws Exception;

}
