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

import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.SyncWorkflow.DbtTransformationActivityImpl;
import io.airbyte.workers.temporal.SyncWorkflow.NormalizationActivityImpl;
import io.airbyte.workers.temporal.SyncWorkflow.ReplicationActivityImpl;
import io.temporal.api.namespace.v1.NamespaceInfo;
import io.temporal.api.workflowservice.v1.DescribeNamespaceResponse;
import io.temporal.api.workflowservice.v1.ListNamespacesRequest;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import java.nio.file.Path;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TemporalPool implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(TemporalPool.class);

  private final WorkflowServiceStubs temporalService;
  private final Path workspaceRoot;
  private final ProcessFactory processFactory;

  public TemporalPool(WorkflowServiceStubs temporalService, Path workspaceRoot, ProcessFactory processFactory) {
    this.temporalService = temporalService;
    this.workspaceRoot = workspaceRoot;
    this.processFactory = processFactory;
  }

  @Override
  public void run() {
    waitForTemporalServerAndLog();

    final WorkerFactory factory = WorkerFactory.newInstance(WorkflowClient.newInstance(temporalService));

    final Worker specWorker = factory.newWorker(TemporalJobType.GET_SPEC.name());
    specWorker.registerWorkflowImplementationTypes(SpecWorkflow.WorkflowImpl.class);
    specWorker.registerActivitiesImplementations(new SpecWorkflow.SpecActivityImpl(processFactory, workspaceRoot));

    final Worker checkConnectionWorker = factory.newWorker(TemporalJobType.CHECK_CONNECTION.name());
    checkConnectionWorker.registerWorkflowImplementationTypes(CheckConnectionWorkflow.WorkflowImpl.class);
    checkConnectionWorker.registerActivitiesImplementations(new CheckConnectionWorkflow.CheckConnectionActivityImpl(processFactory, workspaceRoot));

    final Worker discoverWorker = factory.newWorker(TemporalJobType.DISCOVER_SCHEMA.name());
    discoverWorker.registerWorkflowImplementationTypes(DiscoverCatalogWorkflow.WorkflowImpl.class);
    discoverWorker.registerActivitiesImplementations(new DiscoverCatalogWorkflow.DiscoverCatalogActivityImpl(processFactory, workspaceRoot));

    final Worker syncWorker = factory.newWorker(TemporalJobType.SYNC.name());
    syncWorker.registerWorkflowImplementationTypes(SyncWorkflow.WorkflowImpl.class);
    syncWorker.registerActivitiesImplementations(
        new ReplicationActivityImpl(processFactory, workspaceRoot),
        new NormalizationActivityImpl(processFactory, workspaceRoot),
        new DbtTransformationActivityImpl(processFactory, workspaceRoot));

    factory.start();
  }

  protected void waitForTemporalServerAndLog() {
    LOGGER.info("Waiting for temporal server...");

    boolean temporalStatus = false;

    while (!temporalStatus) {
      LOGGER.warn("Waiting for default namespace to be initialized in temporal...");
      wait(2);

      try {
        temporalStatus = getNamespaces(temporalService).contains("default");
      } catch (Exception e) {
        // Ignore the exception because this likely means that the Temporal service is still initializing.
        LOGGER.warn("Ignoring exception while trying to request Temporal namespaces:", e);
      }
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

  protected static Set<String> getNamespaces(WorkflowServiceStubs temporalService) {
    return temporalService.blockingStub()
        .listNamespaces(ListNamespacesRequest.newBuilder().build())
        .getNamespacesList()
        .stream()
        .map(DescribeNamespaceResponse::getNamespaceInfo)
        .map(NamespaceInfo::getName)
        .collect(toSet());
  }

}
