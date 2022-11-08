/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import io.temporal.activity.ActivityExecutionContext;
import io.temporal.client.ActivityCompletionException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public interface CancellationHandler {

  void checkAndHandleCancellation(Runnable onCancellationCallback);

  class TemporalCancellationHandler implements CancellationHandler {

    private static final Logger LOGGER = LoggerFactory.getLogger(TemporalCancellationHandler.class);

    private final ActivityExecutionContext activityContext;

    public TemporalCancellationHandler(final ActivityExecutionContext activityContext) {
      this.activityContext = activityContext;
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
     */
    @Override
    public void checkAndHandleCancellation(final Runnable onCancellationCallback) {
      try {
        /**
         * Heartbeat is somewhat misleading here. What it does is check the current Temporal activity's
         * context and throw an exception if the sync has been cancelled or timed out. The input to this
         * heartbeat function is available as a field in thrown ActivityCompletionExceptions, which we
         * aren't using for now.
         *
         * We should use this only as a check for the ActivityCompletionException. See
         * {@link TemporalUtils#withBackgroundHeartbeat} for where we actually send heartbeats to ensure
         * that we don't time out the activity.
         */
        activityContext.heartbeat(null);
      } catch (final ActivityCompletionException e) {
        onCancellationCallback.run();
        LOGGER.warn("Job either timed out or was cancelled.");
      }
    }

  }

}
