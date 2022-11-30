/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.logging.LoggingHelper;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.container_orchestrator.orchestrator.JobOrchestrator;
import io.airbyte.workers.process.AsyncKubePodStatus;
import io.micronaut.runtime.Micronaut;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
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
@SuppressWarnings({"PMD.AvoidCatchingThrowable", "PMD.DoNotTerminateVM", "PMD.AvoidFieldNameMatchingTypeName"})
@Singleton
public class Application {

  public static void main(final String[] args) {
    // To mimic previous behavior, assume an exit code of 1 unless Application.run returns otherwise.
    var exitCode = 1;
    try (final var ctx = Micronaut.run(Application.class, args)) {
      exitCode = ctx.getBean(Application.class).run();
    } catch (final Throwable t) {
      log.error("could not run {}", t.getMessage(), t);
    } finally {
      // this mimics the pre-micronaut code, unsure if there is a better way in micronaut to ensure a
      // non-zero exit code
      System.exit(exitCode);
    }
  }

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  private final String application;
  private final JobOrchestrator<?> jobOrchestrator;
  private final AsyncStateManager asyncStateManager;

  public Application(@Named("application") final String application,
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
  @VisibleForTesting
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
