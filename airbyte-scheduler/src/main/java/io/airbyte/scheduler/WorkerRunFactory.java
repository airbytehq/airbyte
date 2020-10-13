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

import com.google.common.base.Preconditions;
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
import io.airbyte.workers.DiscoverCatalogWorker;
import io.airbyte.workers.GetSpecWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.process.SingerIntegrationLauncher;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageTracker;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import io.airbyte.workers.protocols.singer.DefaultSingerDestination;
import io.airbyte.workers.protocols.singer.DefaultSingerSource;
import io.airbyte.workers.protocols.singer.SingerDiscoverCatalogWorker;
import io.airbyte.workers.protocols.singer.SingerMessageTracker;
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
    final int currentAttempt = job.getAttempts();
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
    final GetSpecWorker worker = new DefaultGetSpecWorker(createLauncher(config.getDockerImage()));

    return creator.create(
        jobRoot,
        config,
        new JobOutputGetSpecWorker(worker));
  }

  private WorkerRun createConnectionCheckWorker(JobCheckConnectionConfig config, Path jobRoot) {
    final StandardCheckConnectionInput checkConnectionInput = getCheckConnectionInput(config);

    IntegrationLauncher launcher = createLauncher(config.getDockerImage());
    DiscoverCatalogWorker discoverCatalogWorker =
        isAirbyteProtocol(config.getDockerImage()) ? new DefaultDiscoverCatalogWorker(launcher) : new SingerDiscoverCatalogWorker(launcher);

    return creator.create(
        jobRoot,
        checkConnectionInput,
        new JobOutputCheckConnectionWorker(
            new DefaultCheckConnectionWorker(discoverCatalogWorker)));
  }

  private WorkerRun createDiscoverCatalogWorker(JobDiscoverCatalogConfig config, Path jobRoot) {
    final StandardDiscoverCatalogInput discoverSchemaInput = getDiscoverCatalogInput(config);

    IntegrationLauncher launcher = createLauncher(config.getDockerImage());
    DiscoverCatalogWorker discoverCatalogWorker =
        isAirbyteProtocol(config.getDockerImage()) ? new DefaultDiscoverCatalogWorker(launcher) : new SingerDiscoverCatalogWorker(launcher);

    return creator.create(
        jobRoot,
        discoverSchemaInput,
        new JobOutputDiscoverSchemaWorker(discoverCatalogWorker));
  }

  private WorkerRun createSyncWorker(JobSyncConfig config, Path jobRoot) {
    final StandardSyncInput syncInput = getSyncInput(config);

    IntegrationLauncher sourceLauncher = createLauncher(config.getSourceDockerImage());
    IntegrationLauncher destinationLauncher = createLauncher(config.getDestinationDockerImage());

    Preconditions.checkArgument(sourceLauncher.getClass().equals(destinationLauncher.getClass()),
        "Source and Destination must be using the same protocol");

    if (!isAirbyteProtocol(config.getDestinationDockerImage())) {
      final SingerDiscoverCatalogWorker discoverSchemaWorker = new SingerDiscoverCatalogWorker(sourceLauncher);

      return creator.create(
          jobRoot,
          syncInput,
          new JobOutputSyncWorker(
              new DefaultSyncWorker<>(
                  new DefaultSingerSource(sourceLauncher, discoverSchemaWorker),
                  new DefaultSingerDestination(destinationLauncher),
                  new SingerMessageTracker())));

    } else {
      final DefaultDiscoverCatalogWorker discoverSchemaWorker = new DefaultDiscoverCatalogWorker(createLauncher(config.getSourceDockerImage()));

      return creator.create(
          jobRoot,
          syncInput,
          new JobOutputSyncWorker(
              new DefaultSyncWorker<>(
                  new DefaultAirbyteSource(sourceLauncher, discoverSchemaWorker),
                  new DefaultAirbyteDestination(destinationLauncher),
                  new AirbyteMessageTracker())));
    }
  }

  private IntegrationLauncher createLauncher(final String image) {
    return isAirbyteProtocol(image) ? new AirbyteIntegrationLauncher(image, pbf) : new SingerIntegrationLauncher(image, pbf);
  }

  private boolean isAirbyteProtocol(final String image) {
    return image != null && image.contains("abprotocol");
  }

  private static StandardCheckConnectionInput getCheckConnectionInput(JobCheckConnectionConfig config) {
    return new StandardCheckConnectionInput().withConnectionConfiguration(config.getConnectionConfiguration());
  }

  private static StandardDiscoverCatalogInput getDiscoverCatalogInput(JobDiscoverCatalogConfig config) {
    return new StandardDiscoverCatalogInput().withConnectionConfiguration(config.getConnectionConfiguration());
  }

  private static StandardSyncInput getSyncInput(JobSyncConfig config) {
    return new StandardSyncInput()
        .withSourceConnectionImplementation(config.getSourceConnectionImplementation())
        .withDestinationConnectionImplementation(config.getDestinationConnectionImplementation())
        .withStandardSync(config.getStandardSync());
  }

  /*
   * This class is here to help with the testing
   */
  @FunctionalInterface
  interface Creator {

    <T> WorkerRun create(Path jobRoot, T input, Worker<T, JobOutput> worker);

  }

}
