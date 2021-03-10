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

import static java.util.stream.Collectors.toSet;

import io.airbyte.workers.process.ProcessBuilderFactory;
import io.temporal.api.namespace.v1.NamespaceInfo;
import io.temporal.api.workflowservice.v1.DescribeNamespaceResponse;
import io.temporal.api.workflowservice.v1.ListNamespacesRequest;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import java.nio.file.Path;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TemporalPool implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(TemporalPool.class);

  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;

  public TemporalPool(Path workspaceRoot, ProcessBuilderFactory pbf) {
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
  }

  @Override
  public void run() {
    waitForTemporalServerAndLog();

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

  private static void waitForTemporalServerAndLog() {
    LOGGER.info("Waiting for temporal server...");

    while (!getNamespaces().contains("default")) {
      LOGGER.warn("Waiting for default namespace to be initialized in temporal...");
      wait(2);
    }

    // sometimes it takes a few additional seconds for workflow queue listening to be available
    wait(5);

    LOGGER.info("Found temporal default namespace!");
  }

  private static void wait(int seconds) {
    try {
      Thread.sleep(seconds * 1000);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

  private static Set<String> getNamespaces() {
    return TemporalUtils.TEMPORAL_SERVICE.blockingStub()
        .listNamespaces(ListNamespacesRequest.newBuilder().build())
        .getNamespacesList()
        .stream()
        .map(DescribeNamespaceResponse::getNamespaceInfo)
        .map(NamespaceInfo::getName)
        .collect(toSet());
  }

}
