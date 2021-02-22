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

package io.airbyte.scheduler;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.concurrency.GracefulShutdownHandler;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogHelpers;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DefaultConfigPersistence;
import io.airbyte.db.AirbyteVersion;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.temporal.CheckConnectionWorkflow;
import io.airbyte.scheduler.temporal.DiscoverWorkflow;
import io.airbyte.scheduler.temporal.SpecWorkflow;
import io.airbyte.scheduler.temporal.SyncWorkflow;
import io.airbyte.workers.process.DockerProcessBuilderFactory;
import io.airbyte.workers.process.KubeProcessBuilderFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;

import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/**
 * The SchedulerApp is responsible for finding new scheduled jobs that need to be run and to launch
 * them. The current implementation uses a thread pool on the scheduler's machine to launch the
 * jobs. One thread is reserved for the job submitter, which is responsible for finding and
 * launching new jobs.
 */
public class SchedulerApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerApp.class);



  private static ProcessBuilderFactory getProcessBuilderFactory(Configs configs) {
    if (configs.getWorkerEnvironment() == Configs.WorkerEnvironment.KUBERNETES) {
      return new KubeProcessBuilderFactory(configs.getWorkspaceRoot());
    } else {
      return new DockerProcessBuilderFactory(
          configs.getWorkspaceRoot(),
          configs.getWorkspaceDockerMount(),
          configs.getLocalDockerMount(),
          configs.getDockerNetwork());
    }
  }

  public static void main(String[] args) throws InterruptedException {
    // todo: wait on temporal startup in a cleaner way
    Thread.sleep(45000L);
    System.out.println("starting...");

    final Configs configs = new EnvConfigs();

    final Path configRoot = configs.getConfigRoot();
    LOGGER.info("configRoot = " + configRoot);

    MDC.put(LogHelpers.WORKSPACE_MDC_KEY, LogHelpers.getSchedulerLogsRoot(configs).toString());

    final Path workspaceRoot = configs.getWorkspaceRoot();
    LOGGER.info("workspaceRoot = " + workspaceRoot);

    final ProcessBuilderFactory pbf = getProcessBuilderFactory(configs);
    final ConfigPersistence configPersistence = new DefaultConfigPersistence(configRoot);
    final ConfigRepository configRepository = new ConfigRepository(configPersistence);

    TrackingClientSingleton.initialize(
        configs.getTrackingStrategy(),
        configs.getAirbyteRole(),
        configs.getAirbyteVersion(),
        configRepository);

    LOGGER.info("Launching scheduler...");

    WorkerFactory factory = WorkerFactory.newInstance(TemporalUtils.TEMPORAL_CLIENT);

    Worker specWorker = factory.newWorker(TemporalUtils.SPEC_WORKFLOW_QUEUE);
    specWorker.registerWorkflowImplementationTypes(SpecWorkflow.WorkflowImpl.class);
    specWorker.registerActivitiesImplementations(new SpecWorkflow.SpecActivityImpl(pbf, configs.getWorkspaceRoot()));

    Worker discoverWorker = factory.newWorker(TemporalUtils.DISCOVER_WORKFLOW_QUEUE);
    discoverWorker.registerWorkflowImplementationTypes(DiscoverWorkflow.WorkflowImpl.class);
    discoverWorker.registerActivitiesImplementations(new DiscoverWorkflow.DiscoverActivityImpl(pbf, configs.getWorkspaceRoot()));

    Worker checkConnectionWorker = factory.newWorker(TemporalUtils.CHECK_CONNECTION_WORKFLOW_QUEUE);
    checkConnectionWorker.registerWorkflowImplementationTypes(CheckConnectionWorkflow.WorkflowImpl.class);
    checkConnectionWorker.registerActivitiesImplementations(new CheckConnectionWorkflow.CheckConnectionActivityImpl(pbf, configs.getWorkspaceRoot()));

    Worker syncWorker = factory.newWorker(TemporalUtils.SYNC_WORKFLOW_QUEUE);
    syncWorker.registerWorkflowImplementationTypes(SyncWorkflow.WorkflowImpl.class);
    syncWorker.registerActivitiesImplementations(new SyncWorkflow.SyncActivityImpl(pbf, configs.getWorkspaceRoot()));

    factory.start();
  }

}
