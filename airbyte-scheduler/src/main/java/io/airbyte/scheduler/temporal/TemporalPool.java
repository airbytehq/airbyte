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

package io.airbyte.scheduler.temporal;

import io.airbyte.scheduler.temporal.TemporalUtils.TemporalJobType;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import java.nio.file.Path;

public class TemporalPool implements Runnable {

  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;

  public TemporalPool(Path workspaceRoot, ProcessBuilderFactory pbf) {
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
  }

  @Override
  public void run() {
    final WorkerFactory factory = WorkerFactory.newInstance(TemporalUtils.TEMPORAL_CLIENT);

    final Worker specWorker = factory.newWorker(TemporalJobType.GET_SPEC.name());
    specWorker.registerWorkflowImplementationTypes(SpecWorkflow.WorkflowImpl.class);
    specWorker.registerActivitiesImplementations(new SpecWorkflow.SpecActivityImpl(pbf, workspaceRoot));

    final Worker checkConnectionWorker = factory.newWorker(TemporalJobType.CHECK_CONNECTION.name());
    checkConnectionWorker.registerWorkflowImplementationTypes(CheckConnectionWorkflow.WorkflowImpl.class);
    checkConnectionWorker.registerActivitiesImplementations(new CheckConnectionWorkflow.CheckConnectionActivityImpl(pbf, workspaceRoot));

    final Worker discoverWorker = factory.newWorker(TemporalJobType.DISCOVER_SCHEMA.name());
    discoverWorker.registerWorkflowImplementationTypes(DiscoverCatalogWorkflow.WorkflowImpl.class);
    discoverWorker.registerActivitiesImplementations(new DiscoverCatalogWorkflow.DiscoverCatalogActivityImpl(pbf, workspaceRoot));

    Worker syncWorker = factory.newWorker(TemporalJobType.SYNC.name());
    syncWorker.registerWorkflowImplementationTypes(SyncWorkflow.WorkflowImpl.class);
    syncWorker.registerActivitiesImplementations(new SyncWorkflow.SyncActivityImpl(pbf, workspaceRoot));

    factory.start();
  }

}
