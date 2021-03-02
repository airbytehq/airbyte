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

package io.airbyte.scheduler.worker_run;

import io.airbyte.config.JobOutput;
import io.airbyte.workers.Worker;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.nio.file.Path;

/**
 * This classes exists to make testing WorkerRunFactories easier. For testing the extending class
 * can use the protected constructor to pass in mocks. In production, the public constructor should
 * be preferred.
 *
 * @param <T> Input config type
 */
public abstract class BaseWorkerRunFactory<T> implements WorkerRunFactory<T> {

  final IntegrationLauncherFactory integrationLauncherFactory;
  final WorkerRunCreator workerRunCreator;

  public BaseWorkerRunFactory() {
    this(WorkerRunFactoryUtils::createLauncher, WorkerRun::new);
  }

  BaseWorkerRunFactory(IntegrationLauncherFactory integrationLauncherFactory, WorkerRunCreator workerRunCreator) {
    this.integrationLauncherFactory = integrationLauncherFactory;
    this.workerRunCreator = workerRunCreator;
  }

  // exists to make testing easier.
  @FunctionalInterface
  interface IntegrationLauncherFactory {

    IntegrationLauncher create(long jobId, int attempt, final String image, ProcessBuilderFactory pbf);

  }

  // exists to make testing easier.
  @FunctionalInterface
  interface WorkerRunCreator {

    <T> WorkerRun create(Path jobRoot, T input, Worker<T, JobOutput> worker);

  }

}
