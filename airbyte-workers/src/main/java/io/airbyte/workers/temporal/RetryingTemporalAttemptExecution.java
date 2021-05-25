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

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.Worker;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.BiFunction;
import java.util.function.Predicate;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/*
 * This class allows a worker to run multiple times. In addition to the functionality in {@link
 * TemporalAttemptExecution} it takes a predicate to determine if the output of a worker constitutes
 * a complete success or a partial one. It also takes a function that takes in the input of the
 * previous run of the worker and the output of the last worker in order to generate a new input for
 * that worker.
 */
public class RetryingTemporalAttemptExecution<INPUT, OUTPUT> implements Supplier<List<OUTPUT>> {

  private static final Logger LOGGER = LoggerFactory.getLogger(RetryingTemporalAttemptExecution.class);

  private final CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier;
  private final Supplier<INPUT> inputSupplier;
  private final CancellationHandler cancellationHandler;

  private final Predicate<OUTPUT> shouldAttemptAgainPredicate;
  private final BiFunction<INPUT, OUTPUT, INPUT> computeNextAttemptInputFunction;
  private final int maxRetriesCount;
  private final TemporalAttemptExecutionFactory<INPUT, OUTPUT> temporalAttemptExecutionFactory;
  private final Path workspaceRoot;
  private final JobRunConfig jobRunConfig;

  public RetryingTemporalAttemptExecution(Path workspaceRoot,
                                          JobRunConfig jobRunConfig,
                                          CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier,
                                          Supplier<INPUT> initialInputSupplier,
                                          CancellationHandler cancellationHandler,
                                          Predicate<OUTPUT> shouldAttemptAgainPredicate,
                                          BiFunction<INPUT, OUTPUT, INPUT> computeNextAttemptInputFunction,
                                          int maxRetriesCount) {
    this(
        workspaceRoot,
        jobRunConfig,
        workerSupplier,
        initialInputSupplier,
        cancellationHandler,
        shouldAttemptAgainPredicate,
        computeNextAttemptInputFunction,
        maxRetriesCount,
        TemporalAttemptExecution::new);
  }

  @VisibleForTesting
  RetryingTemporalAttemptExecution(Path workspaceRoot,
                                   JobRunConfig jobRunConfig,
                                   CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier,
                                   Supplier<INPUT> initialInputSupplier,
                                   CancellationHandler cancellationHandler,
                                   Predicate<OUTPUT> shouldAttemptAgainPredicate,
                                   BiFunction<INPUT, OUTPUT, INPUT> computeNextAttemptInputFunction,
                                   int maxRetriesCount,
                                   TemporalAttemptExecutionFactory<INPUT, OUTPUT> temporalAttemptExecutionFactory) {
    this.workspaceRoot = workspaceRoot;
    this.jobRunConfig = jobRunConfig;
    this.workerSupplier = workerSupplier;
    this.inputSupplier = initialInputSupplier;
    this.cancellationHandler = cancellationHandler;
    this.shouldAttemptAgainPredicate = shouldAttemptAgainPredicate;
    this.computeNextAttemptInputFunction = computeNextAttemptInputFunction;
    this.maxRetriesCount = maxRetriesCount;
    this.temporalAttemptExecutionFactory = temporalAttemptExecutionFactory;
  }

  @Override
  public List<OUTPUT> get() {
    INPUT input = inputSupplier.get();
    final AtomicReference<OUTPUT> lastOutput = new AtomicReference<>();
    List<OUTPUT> outputCollector = new ArrayList<>();

    for (int i = 0; true; i++) {
      if (i >= maxRetriesCount) {
        LOGGER.info("Max retries reached: {}", i);
        break;
      }

      final boolean hasLastOutput = lastOutput.get() != null;
      final boolean shouldAttemptAgain = !hasLastOutput || shouldAttemptAgainPredicate.test(lastOutput.get());
      LOGGER.info("Last output present: {}. Should attempt again: {}", lastOutput.get() != null, shouldAttemptAgain);
      if (hasLastOutput && !shouldAttemptAgain) {
        break;
      }

      LOGGER.info("Starting attempt: {} of {}", i, maxRetriesCount);

      Supplier<INPUT> resolvedInputSupplier = !hasLastOutput ? inputSupplier : () -> computeNextAttemptInputFunction.apply(input, lastOutput.get());

      final TemporalAttemptExecution<INPUT, OUTPUT> temporalAttemptExecution = temporalAttemptExecutionFactory.create(
          workspaceRoot,
          jobRunConfig,
          workerSupplier,
          resolvedInputSupplier,
          cancellationHandler);
      lastOutput.set(temporalAttemptExecution.get());
      outputCollector.add(lastOutput.get());
    }

    return outputCollector;
  }

  // interface to make testing easier.
  @FunctionalInterface
  interface TemporalAttemptExecutionFactory<INPUT, OUTPUT> {

    TemporalAttemptExecution<INPUT, OUTPUT> create(Path workspaceRoot,
                                                   JobRunConfig jobRunConfig,
                                                   CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier,
                                                   Supplier<INPUT> inputSupplier,
                                                   CancellationHandler cancellationHandler);

  }

}
