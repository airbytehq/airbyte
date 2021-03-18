/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers.temporal;

import io.airbyte.workers.WorkerException;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import io.temporal.client.ActivityCompletionException;

public interface CancellationHandler {

  void checkAndHandleCancellation(Runnable onCancellationCallback) throws WorkerException;

  class TemporalCancellationHandler implements CancellationHandler {

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
    public void checkAndHandleCancellation(Runnable onCancellationCallback) throws WorkerException {
      try {
        // Heartbeat is somewhat misleading here. What it does is check the current Temporal activity's
        // context and
        // throw an exception if the sync has been cancelled or timed out. The input to this heartbeat
        // function
        // is available as a field in thrown ActivityCompletionExceptions, which we aren't using for now.
        context.heartbeat(null);
      } catch (ActivityCompletionException e) {
        onCancellationCallback.run();
        throw new WorkerException("Worker cleaned up after exception", e);
      }
    }

  }

}
