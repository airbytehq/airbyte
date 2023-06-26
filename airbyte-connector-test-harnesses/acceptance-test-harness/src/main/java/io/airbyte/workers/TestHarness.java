/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.workers.exception.TestHarnessException;
import java.nio.file.Path;

public interface TestHarness<InputType, OutputType> {

  /**
   * Blocking call to run the worker's workflow. Once this is complete, getStatus should return either
   * COMPLETE, FAILED, or CANCELLED.
   */
  OutputType run(InputType inputType, Path jobRoot) throws TestHarnessException;

  /**
   * Cancels in-progress workers. Although all workers support cancel, in reality only the
   * asynchronous {@link DefaultReplicationWorker}'s cancel is used.
   */
  void cancel();

}
