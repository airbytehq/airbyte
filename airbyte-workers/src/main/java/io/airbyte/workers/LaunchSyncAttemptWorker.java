/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LaunchSyncAttemptWorker implements Worker<StandardSyncInput, StandardSyncOutput> {

  private static final Logger LOGGER = LoggerFactory.getLogger(LaunchSyncAttemptWorker.class);

  private final IntegrationLauncherConfig sourceLauncherConfig;
  private final IntegrationLauncherConfig destinationLauncherConfig;
  private final JobRunConfig jobRunConfig;
  private final StandardSyncInput syncInput;
  private final ProcessFactory processFactory;
  private final Path workspaceRoot;
  private final String airbyteVersion;
  private final UUID connectionId;

  private Process process = null;

  public LaunchSyncAttemptWorker(
                                 final IntegrationLauncherConfig sourceLauncherConfig,
                                 final IntegrationLauncherConfig destinationLauncherConfig,
                                 final JobRunConfig jobRunConfig,
                                 final StandardSyncInput syncInput,
                                 final ProcessFactory processFactory,
                                 final Path workspaceRoot,
                                 final String airbyteVersion,
                                 final UUID connectionId) {
    this.sourceLauncherConfig = sourceLauncherConfig;
    this.destinationLauncherConfig = destinationLauncherConfig;
    this.jobRunConfig = jobRunConfig;
    this.syncInput = syncInput;
    this.processFactory = processFactory;
    this.workspaceRoot = workspaceRoot;
    this.airbyteVersion = airbyteVersion;
    this.connectionId = connectionId;
  }

  @Override
  public StandardSyncOutput run(StandardSyncInput standardSyncInput, Path jobRoot) throws WorkerException {
    try {
      // todo: do we need to wrapp all of this in a worker with anew TemporalAttemptExecution<>()

      final Path jobPath = WorkerUtils.getJobRoot(workspaceRoot, jobRunConfig.getJobId(), jobRunConfig.getAttemptId());

      // todo: don't use magic strings
      final Map<String, String> fileMap = Map.of(
          "jobRunConfig.json", Jsons.serialize(jobRunConfig),
          "sourceLauncherConfig.json", Jsons.serialize(sourceLauncherConfig),
          "destinationLauncherConfig.json", Jsons.serialize(destinationLauncherConfig),
          "syncInput.json", Jsons.serialize(syncInput),
          "connectionId.json", Jsons.serialize(connectionId),
          "envMap.json", Jsons.serialize(System.getenv())); // todo: inject this differently

      // for now keep same failure behavior where this is heartbeating and depends on the parent worker to
      // exist
      process = processFactory.create(
          "sync-attempt-" + UUID.randomUUID().toString().substring(0, 10),
          0,
          jobPath,
          "airbyte/sync-attempt:" + airbyteVersion,
          false,
          fileMap,
          null,
          null, // todo: allow resource requirements for this pod to be configurable
          Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SYNC_ATTEMPT));

      final AtomicReference<StandardSyncOutput> output = new AtomicReference<>();

      LineGobbler.gobble(process.getInputStream(), line -> {
        final var maybeOutput = Jsons.tryDeserialize(line, StandardSyncOutput.class);
        maybeOutput.ifPresent(output::set);
      });

      process.waitFor();

      if (output.get() != null) {
        return output.get();
      } else {
        throw new WorkerException("Running the sync attempt resulted in no readable output!");
      }
    } catch (Exception e) {
      throw new WorkerException("Running the sync attempt failed", e);
    }
  }

  @Override
  public void cancel() {
    if (process == null) {
      return;
    }

    LOGGER.info("Cancelling sync attempt launcher...");
    WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);
    if (process.isAlive() || process.exitValue() != 0) {
      LOGGER.error("Wasn't able to cancel sync attempt launcher..."); // todo: output problem here
    }
  }

}
