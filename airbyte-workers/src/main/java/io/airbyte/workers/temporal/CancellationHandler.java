/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import io.airbyte.workers.WorkerException;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import io.temporal.client.ActivityCompletionException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public interface CancellationHandler {

  void checkAndHandleCancellation(Runnable onCancellationCallback);

  class TemporalCancellationHandler implements CancellationHandler {

    private static final Logger LOGGER = LoggerFactory.getLogger(TemporalCancellationHandler.class);

    final ActivityExecutionContext context;

    public TemporalCancellationHandler() {
      context = Activity.getExecutionContext();
    }

    /**
     * Check for a cancellation/timeout status and run any callbacks necessary to shut down underlying
     * processes. This method should generally be run frequently within an activity so a change in
     * cancellation status is respected. This will only be effective if the cancellation type for the
     * workflow is set to
     * {@link io.temporal.activity.ActivityCancellationType#WAIT_CANCELLATION_COMPLETED}; otherwise, the
     * activity will be killed automatically as part of cleanup without removing underlying processes.
     *
     * @param onCancellationCallback a runnable that will only run when Temporal indicates the activity
     *        should be killed (cancellation or timeout).
     * @throws WorkerException
     */
    @Override
    public void checkAndHandleCancellation(Runnable onCancellationCallback) {
      try {
        // Heartbeat is somewhat misleading here. What it does is check the current Temporal activity's
        // context and
        // throw an exception if the sync has been cancelled or timed out. The input to this heartbeat
        // function
        // is available as a field in thrown ActivityCompletionExceptions, which we aren't using for now.
        context.heartbeat(null);
      } catch (ActivityCompletionException e) {
        onCancellationCallback.run();
        LOGGER.warn("Job either timeout-ed or was cancelled.");
      }
    }

  }

}
