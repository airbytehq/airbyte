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

package io.airbyte.workers;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.config.WorkerPodToleration;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.protocols.airbyte.HeartbeatMonitor;
import java.nio.file.Path;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.function.BiConsumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO:(Issue-4824): Figure out how to log Docker process information.
public class WorkerUtils {

  public static final List<WorkerPodToleration> DEFAULT_WORKER_POD_TOLERATIONS = initWorkerPodTolerations();
  public static final ResourceRequirements DEFAULT_RESOURCE_REQUIREMENTS = initResourceRequirements();

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerUtils.class);

  public static void gentleClose(final Process process, final long timeout, final TimeUnit timeUnit) {
    if (process == null) {
      return;
    }

    if (new EnvConfigs().getWorkerEnvironment().equals(WorkerEnvironment.KUBERNETES)) {
      LOGGER.debug("Gently closing process {}", process.info().commandLine().get());
    }

    try {
      if (process.isAlive()) {
        process.waitFor(timeout, timeUnit);
      }
    } catch (InterruptedException e) {
      LOGGER.error("Exception while while waiting for process to finish", e);
    }

    if (process.isAlive()) {
      forceShutdown(process, Duration.of(1, ChronoUnit.MINUTES));
    }
  }

  /**
   * As long as the the heartbeatMonitor detects a heartbeat, the process will be allowed to continue.
   * This method checks the heartbeat once every minute. Once there is no heartbeat detected, if the
   * process has ended, then the method returns. If the process is still running it is given a grace
   * period of the timeout arguments passed into the method. Once those expire the process is killed
   * forcibly. If the process cannot be killed, this method will log that this is the case, but then
   * returns.
   *
   * @param process - process to monitor.
   * @param heartbeatMonitor - tracks if the heart is still beating for the given process.
   * @param checkHeartbeatDuration - grace period to give the process to die after its heart stops
   *        beating.
   * @param checkHeartbeatDuration - frequency with which the heartbeat of the process is checked.
   * @param forcedShutdownDuration - amount of time to wait if a process needs to be destroyed
   *        forcibly.
   */
  public static void gentleCloseWithHeartbeat(final Process process,
                                              final HeartbeatMonitor heartbeatMonitor,
                                              Duration gracefulShutdownDuration,
                                              Duration checkHeartbeatDuration,
                                              Duration forcedShutdownDuration) {
    gentleCloseWithHeartbeat(
        process,
        heartbeatMonitor,
        gracefulShutdownDuration,
        checkHeartbeatDuration,
        forcedShutdownDuration,
        WorkerUtils::forceShutdown);
  }

  @VisibleForTesting
  static void gentleCloseWithHeartbeat(final Process process,
                                       final HeartbeatMonitor heartbeatMonitor,
                                       final Duration gracefulShutdownDuration,
                                       final Duration checkHeartbeatDuration,
                                       final Duration forcedShutdownDuration,
                                       final BiConsumer<Process, Duration> forceShutdown) {
    while (process.isAlive() && heartbeatMonitor.isBeating()) {
      try {
        if (new EnvConfigs().getWorkerEnvironment().equals(WorkerEnvironment.KUBERNETES)) {
          LOGGER.debug("Gently closing process {} with heartbeat..", process.info().commandLine().get());
        }

        process.waitFor(checkHeartbeatDuration.toMillis(), TimeUnit.MILLISECONDS);
      } catch (InterruptedException e) {
        LOGGER.error("Exception while waiting for process to finish", e);
      }
    }

    if (process.isAlive()) {
      try {
        if (new EnvConfigs().getWorkerEnvironment().equals(WorkerEnvironment.KUBERNETES)) {
          LOGGER.debug("Gently closing process {} without heartbeat..", process.info().commandLine().get());
        }

        process.waitFor(gracefulShutdownDuration.toMillis(), TimeUnit.MILLISECONDS);
      } catch (InterruptedException e) {
        LOGGER.error("Exception during grace period for process to finish. This can happen when cancelling jobs.");
      }
    }

    // if we were unable to exist gracefully, force shutdown...
    if (process.isAlive()) {
      if (new EnvConfigs().getWorkerEnvironment().equals(WorkerEnvironment.KUBERNETES)) {
        LOGGER.debug("Force shutdown process {}..", process.info().commandLine().get());
      }

      forceShutdown.accept(process, forcedShutdownDuration);
    }
  }

  @VisibleForTesting
  static void forceShutdown(Process process, Duration lastChanceDuration) {
    LOGGER.warn("Process is taking too long to finish. Killing it");
    process.destroy();
    try {
      process.waitFor(lastChanceDuration.toMillis(), TimeUnit.MILLISECONDS);
    } catch (InterruptedException e) {
      LOGGER.error("Exception while while killing the process", e);
    }
    if (process.isAlive()) {
      LOGGER.error("Couldn't kill the process. You might have a zombie process.");
    }
  }

  public static void closeProcess(Process process, int duration, TimeUnit timeUnit) {
    if (process == null) {
      return;
    }
    try {
      process.destroy();
      process.waitFor(duration, timeUnit);
      if (process.isAlive()) {
        process.destroyForcibly();
      }
    } catch (InterruptedException e) {
      LOGGER.error("Exception when closing process.", e);
    }
  }

  public static void wait(Process process) {
    try {
      process.waitFor();
    } catch (InterruptedException e) {
      LOGGER.error("Exception while while waiting for process to finish", e);
    }
  }

  public static void cancelProcess(Process process) {
    closeProcess(process, 10, TimeUnit.SECONDS);
  }

  /**
   * Translates a StandardSyncInput into a WorkerSourceConfig. WorkerSourceConfig is a subset of
   * StandardSyncInput.
   */
  public static WorkerSourceConfig syncToWorkerSourceConfig(StandardSyncInput sync) {
    return new WorkerSourceConfig()
        .withSourceConnectionConfiguration(sync.getSourceConfiguration())
        .withCatalog(sync.getCatalog())
        .withState(sync.getState());
  }

  /**
   * Translates a StandardSyncInput into a WorkerDestinationConfig. WorkerDestinationConfig is a
   * subset of StandardSyncInput.
   */
  public static WorkerDestinationConfig syncToWorkerDestinationConfig(StandardSyncInput sync) {
    return new WorkerDestinationConfig()
        .withDestinationConnectionConfiguration(sync.getDestinationConfiguration())
        .withCatalog(sync.getCatalog())
        .withState(sync.getState());
  }

  // todo (cgardens) - there are 2 sources of truth for job path. we need to reduce this down to one,
  // once we are fully on temporal.
  public static Path getJobRoot(Path workspaceRoot, JobRunConfig jobRunConfig) {
    return getJobRoot(workspaceRoot, jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
  }

  public static Path getLogPath(Path jobRoot) {
    return jobRoot.resolve(LogClientSingleton.LOG_FILENAME);
  }

  public static Path getJobRoot(Path workspaceRoot, String jobId, long attemptId) {
    return getJobRoot(workspaceRoot, jobId, Math.toIntExact(attemptId));
  }

  public static Path getJobRoot(Path workspaceRoot, String jobId, int attemptId) {
    return workspaceRoot
        .resolve(String.valueOf(jobId))
        .resolve(String.valueOf(attemptId));
  }

  private static List<WorkerPodToleration> initWorkerPodTolerations() {
    final EnvConfigs configs = new EnvConfigs();
    return configs.getWorkerPodTolerations();
  }

  private static ResourceRequirements initResourceRequirements() {
    final EnvConfigs configs = new EnvConfigs();
    return new ResourceRequirements()
        .withCpuRequest(configs.getCpuRequest())
        .withCpuLimit(configs.getCpuLimit())
        .withMemoryRequest(configs.getMemoryRequest())
        .withMemoryLimit(configs.getMemoryLimit());
  }

}
