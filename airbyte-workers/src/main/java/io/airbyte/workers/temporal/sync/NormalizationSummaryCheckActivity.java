/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.io.IOException;
import java.util.Optional;

@ActivityInterface
public interface NormalizationSummaryCheckActivity {

  @ActivityMethod
  Boolean shouldRunNormalization(Long jobId, Long attemptId, Optional<Long> numCommittedRecords) throws IOException;

}
