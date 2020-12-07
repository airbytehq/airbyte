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

import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.airbyte.workers.DefaultDiscoverCatalogWorker;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.DefaultSyncWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageTracker;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import io.airbyte.workers.protocols.airbyte.EmptyAirbyteSource;
import io.airbyte.workers.wrappers.JobOutputCheckConnectionWorker;
import io.airbyte.workers.wrappers.JobOutputDiscoverSchemaWorker;
import io.airbyte.workers.wrappers.JobOutputGetSpecWorker;
import io.airbyte.workers.wrappers.JobOutputSyncWorker;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is a runnable that give a job id and db connection figures out how to run the
 * appropriate worker for a given job.
 */
public class WorkerRunFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerRunFactory.class);

  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;
  private final Creator creator;

  public WorkerRunFactory(final Path workspaceRoot,
                          final ProcessBuilderFactory pbf) {
    this(workspaceRoot, pbf, WorkerRun::new);
  }

  WorkerRunFactory(final Path workspaceRoot,
                   final ProcessBuilderFactory pbf,
                   final Creator creator) {
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
    this.creator = creator;
  }

  public WorkerRun create(final Job job) {
    final int currentAttempt = job.getAttemptsCount();
    LOGGER.info("job id: {} attempt: {} scope: {} type: {}", job.getId(), currentAttempt, job.getScope(), job.getConfig().getConfigType());

    final Path jobRoot = workspaceRoot.resolve(String.valueOf(job.getId())).resolve(String.valueOf(currentAttempt));
    LOGGER.info("job root: {}", jobRoot);

    return switch (job.getConfig().getConfigType()) {
      case GET_SPEC -> createGetSpecWorker(job.getConfig().getGetSpec(), jobRoot);
      case CHECK_CONNECTION_SOURCE, CHECK_CONNECTION_DESTINATION -> createConnectionCheckWorker(job.getConfig().getCheckConnection(), jobRoot);
      case DISCOVER_SCHEMA -> createDiscoverCatalogWorker(job.getConfig().getDiscoverCatalog(), jobRoot);
      case SYNC -> createSyncWorker(job.getConfig().getSync(), jobRoot);
    };
  }

  private WorkerRun createGetSpecWorker(JobGetSpecConfig config, Path jobRoot) {
    final IntegrationLauncher launcher = createLauncher(config.getDockerImage());

    return creator.create(
        jobRoot,
        config,
        new JobOutputGetSpecWorker(new DefaultGetSpecWorker(launcher)));
  }

  private WorkerRun createConnectionCheckWorker(JobCheckConnectionConfig config, Path jobRoot) {
    final StandardCheckConnectionInput checkConnectionInput = getCheckConnectionInput(config);

    final IntegrationLauncher launcher = createLauncher(config.getDockerImage());
    return creator.create(
        jobRoot,
        checkConnectionInput,
        new JobOutputCheckConnectionWorker(new DefaultCheckConnectionWorker(launcher)));
  }

  private WorkerRun createDiscoverCatalogWorker(JobDiscoverCatalogConfig config, Path jobRoot) {
    final StandardDiscoverCatalogInput discoverSchemaInput = getDiscoverCatalogInput(config);

    final IntegrationLauncher launcher = createLauncher(config.getDockerImage());

    return creator.create(
        jobRoot,
        discoverSchemaInput,
        new JobOutputDiscoverSchemaWorker(new DefaultDiscoverCatalogWorker(launcher)));
  }

  private WorkerRun createSyncWorker(JobSyncConfig config, Path jobRoot) {
    final StandardSyncInput syncInput = getSyncInput(config);

    final IntegrationLauncher sourceLauncher = createLauncher(config.getSourceDockerImage());
    final IntegrationLauncher destinationLauncher = createLauncher(config.getDestinationDockerImage());

    // Switch to using the empty source when the placeholder is found. This is used for resetting the
    // data in the destination.
    final AirbyteSource airbyteSource =
        config.getSourceDockerImage().equals(SchedulerConstants.RESET_SOURCE_IMAGE_PLACEHOLDER) ? new EmptyAirbyteSource()
            : new DefaultAirbyteSource(sourceLauncher);

    return creator.create(
        jobRoot,
        syncInput,
        new JobOutputSyncWorker(
            new DefaultSyncWorker(
                airbyteSource,
                new DefaultAirbyteDestination(destinationLauncher),
                new AirbyteMessageTracker(),
                NormalizationRunnerFactory.create(
                    config.getDestinationDockerImage(),
                    pbf,
                    syncInput.getDestinationConfiguration()))));
  }

  private IntegrationLauncher createLauncher(final String image) {
    return new AirbyteIntegrationLauncher(image, pbf);
  }

  private static StandardCheckConnectionInput getCheckConnectionInput(JobCheckConnectionConfig config) {
    return new StandardCheckConnectionInput().withConnectionConfiguration(config.getConnectionConfiguration());
  }

  private static StandardDiscoverCatalogInput getDiscoverCatalogInput(JobDiscoverCatalogConfig config) {
    return new StandardDiscoverCatalogInput().withConnectionConfiguration(config.getConnectionConfiguration());
  }

  private static StandardSyncInput getSyncInput(JobSyncConfig config) {
    return new StandardSyncInput()
        .withSourceConfiguration(config.getSourceConfiguration())
        .withDestinationConfiguration(config.getDestinationConfiguration())
        .withCatalog(config.getConfiguredAirbyteCatalog())
        .withState(config.getState());
  }

  /*
   * This class is here to help with the testing
   */
  @FunctionalInterface
  interface Creator {

    <T> WorkerRun create(Path jobRoot, T input, Worker<T, JobOutput> worker);

  }

}
