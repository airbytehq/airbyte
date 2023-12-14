/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination;

import java.util.Optional;

/**
 * @param recordsWritten The number of records written to the stream, or empty if the caller does
 *        not track this information. (this is primarily for backwards-compatibility with the legacy
 *        destinations framework; new implementations should always provide this information). If
 *        this value is empty, consumers should assume that the sync wrote nonzero records for this
 *        stream.
 */
public record StreamSyncSummary(Optional<Long> recordsWritten) {

  public static final StreamSyncSummary DEFAULT = new StreamSyncSummary(Optional.empty());

}
