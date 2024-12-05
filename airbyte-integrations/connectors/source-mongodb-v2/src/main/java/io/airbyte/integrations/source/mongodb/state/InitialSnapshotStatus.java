/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

/**
 * Enumerates the potential status values for the initial snapshot of streams. This information is
 * used to determine if a stream has successfully completed its initial snapshot when building the
 * list of stream iterators for a sync.
 */
public enum InitialSnapshotStatus {

  IN_PROGRESS,
  COMPLETE,
  // A Full Refresh stream state behaves like In Progress,
  // but its value set to null when collection is fully read
  // Rather than turning into Complete
  FULL_REFRESH
}
