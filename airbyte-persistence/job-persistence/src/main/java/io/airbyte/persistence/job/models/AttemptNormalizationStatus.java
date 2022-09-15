/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.models;

import java.util.Optional;

public class AttemptNormalizationStatus {

  private final long attemptNumber;
  private final Optional<Long> recordsCommitted;
  private final Boolean normalizationFailed;

  public AttemptNormalizationStatus(final long attemptNumber, final Optional<Long> recordsCommitted, final Boolean normalizationFailed) {
    this.attemptNumber = attemptNumber;
    this.recordsCommitted = recordsCommitted;
    this.normalizationFailed = normalizationFailed;
  }

  public long getAttemptNumber() {
    return attemptNumber;
  }

  public Optional<Long> getRecordsCommitted() {
    return recordsCommitted;
  }

  public Boolean getNormalizationFailed() {
    return normalizationFailed;
  }

}
