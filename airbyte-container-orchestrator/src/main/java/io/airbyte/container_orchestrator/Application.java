/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.commons.logging.LoggingHelper;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.container_orchestrator.orchestrator.JobOrchestrator;
import io.airbyte.workers.process.AsyncKubePodStatus;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.process.KubePodProcess;
import io.micronaut.runtime.Micronaut;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Entrypoint for the application responsible for launching containers and handling all message
 * passing for replication, normalization, and dbt. Also, the current version relies on a heartbeat
 * from a Temporal worker. This will also be removed in the future so this can run fully async.
 * <p>
 * This application retrieves most of its configuration from copied files from the calling Temporal
 * worker.
 * <p>
 * This app uses default logging which is directly captured by the calling Temporal worker. In the
 * future this will need to independently interact with cloud storage.
 */
@SuppressWarnings({"PMD.AvoidCatchingThrowable", "PMD.DoNotTerminateVM"})
@Singleton
public class Application {

  public static void main(final String[] args) {
    try {
      // wait for config files to be copied
      // todo: fix this to use the correct path
      final var successFile = Path.of("/tmp/conorc", KubePodProcess.SUCCESS_FILE_NAME);
      log.info("Looking for config file at {}", successFile);

      int secondsWaited = 0;

      while (!successFile.toFile().exists() && secondsWaited < MAX_SECONDS_TO_WAIT_FOR_FILE_COPY) {
        log.info("Waiting for config file transfers to complete...");
        Thread.sleep(1000);
        secondsWaited++;
      }

      if (!successFile.toFile().exists()) {
        log.error("Config files did not transfer within the maximum amount of time ({} seconds)!",
            MAX_SECONDS_TO_WAIT_FOR_FILE_COPY);
        System.exit(1);
      }
    } catch (final Throwable t) {
      log.error("Orchestrator failed...", t);
      // otherwise the pod hangs on closing
      System.exit(1);
    }

    // To mimic previous behavior, assume an exit code of 1 unless Application.run returns otherwise.
    var exitCode = 1;
    try (final var ctx = Micronaut.run(Application.class, args)) {
      exitCode = ctx.getBean(Application.class).run();
    } catch (final Throwable t) {
      log.error("could not run  {}", t.getMessage());
      t.printStackTrace();
    } finally {
      // this mimics the pre-micronaut code, unsure if there is a better way in micronaut to ensure a
      // non-zero exit code
      System.exit(exitCode);
    }
  }

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  static final int MAX_SECONDS_TO_WAIT_FOR_FILE_COPY = 60;

  private final String application;
  private final JobOrchestrator<?> jobOrchestrator;
  private final AsyncStateManager asyncStateManager;

  public Application(
                     final String application,
                     final KubePodInfo kubePodInfo,
                     final JobOrchestrator<?> jobOrchestrator,
                     final AsyncStateManager asyncStateManager) {
    this.application = application;
    this.jobOrchestrator = jobOrchestrator;
    this.asyncStateManager = asyncStateManager;
  }

  /**
   * Configures logging/mdc scope, and creates all objects necessary to handle state updates.
   * <p>
   * Handles state updates (including writing failures) and running the job orchestrator. As much of
   * the initialization as possible should go in here, so it's logged properly and the state storage
   * is updated appropriately.
   */
  int run() {
    // set mdc scope for the remaining execution
    try (final var mdcScope = new MdcScope.Builder()
        .setLogPrefix(application)
        .setPrefixColor(LoggingHelper.Color.CYAN_BACKGROUND)
        .build()) {

      asyncStateManager.write(AsyncKubePodStatus.INITIALIZING);
      asyncStateManager.write(AsyncKubePodStatus.RUNNING);
      asyncStateManager.write(AsyncKubePodStatus.SUCCEEDED, jobOrchestrator.runJob().orElse(""));
    } catch (final Throwable t) {
      log.error("Killing orchestrator because of an Exception", t);
      asyncStateManager.write(AsyncKubePodStatus.FAILED);
      return 1;
    }

    return 0;
  }

}
