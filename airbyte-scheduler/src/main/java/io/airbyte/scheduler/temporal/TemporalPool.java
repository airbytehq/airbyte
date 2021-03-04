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
    WorkerFactory factory = WorkerFactory.newInstance(TemporalUtils.TEMPORAL_CLIENT);

    final Worker specWorker = factory.newWorker(TemporalJobType.GET_SPEC.name());
    specWorker.registerWorkflowImplementationTypes(SpecWorkflow.WorkflowImpl.class);
    specWorker.registerActivitiesImplementations(new SpecWorkflow.SpecActivityImpl(pbf, workspaceRoot));

    // todo (cgardens) - these will come back once we use temporal for these workers.
    // Worker discoverWorker = factory.newWorker(TemporalUtils.DISCOVER_WORKFLOW_QUEUE);
    // discoverWorker.registerWorkflowImplementationTypes(DiscoverWorkflow.WorkflowImpl.class);
    // discoverWorker.registerActivitiesImplementations(new DiscoverWorkflow.DiscoverActivityImpl(pbf,
    // configs.getWorkspaceRoot()));
    //
    // Worker checkConnectionWorker = factory.newWorker(TemporalUtils.CHECK_CONNECTION_WORKFLOW_QUEUE);
    // checkConnectionWorker.registerWorkflowImplementationTypes(CheckConnectionWorkflow.WorkflowImpl.class);
    // checkConnectionWorker.registerActivitiesImplementations(new
    // CheckConnectionWorkflow.CheckConnectionActivityImpl(pbf, configs.getWorkspaceRoot()));
    //
    // Worker syncWorker = factory.newWorker(TemporalUtils.SYNC_WORKFLOW_QUEUE);
    // syncWorker.registerWorkflowImplementationTypes(SyncWorkflow.WorkflowImpl.class);
    // syncWorker.registerActivitiesImplementations(new SyncWorkflow.SyncActivityImpl(pbf,
    // configs.getWorkspaceRoot()));

    factory.start();
  }

}
