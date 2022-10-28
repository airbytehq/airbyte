/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.logging.LoggingHelper;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.process.AsyncKubePodStatus;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.process.KubePodProcess;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.storage.StateClients;
import io.micronaut.context.ApplicationContext;
import io.micronaut.runtime.Micronaut;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
import java.nio.file.Path;
import java.util.Map;
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
      final var successFile = Path.of("/tmp/co", KubePodProcess.CONFIG_DIR,
          KubePodProcess.SUCCESS_FILE_NAME);
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
    final var exitCode = 1;
    try (final var ctx = Micronaut.run(Application.class, args)) {
//      exitCode = ctx.getBean(Application.class).run();
    } catch (final Throwable t) {
      log.error("could not run  {}", t.getMessage());
      t.printStackTrace();
    } finally {
      System.exit(exitCode);
    }
  }

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  static final int MAX_SECONDS_TO_WAIT_FOR_FILE_COPY = 60;

  // TODO Move the following to configuration once converted to a Micronaut service

  // IMPORTANT: Changing the storage location will orphan already existing kube pods when the new
  // version is deployed!
  private static final Path STATE_STORAGE_PREFIX = Path.of("/state");
  private static final Integer KUBE_HEARTBEAT_PORT = 9000;

  private final ApplicationContext context;
  private final String application;
  private final Map<String, String> envMap;
  private final JobRunConfig jobRunConfig;
  private final KubePodInfo kubePodInfo;
  private final Configs configs;
  private final FeatureFlags featureFlags;
  //  private final ProcessFactory processFactory;
  private final JobOrchestrator<?> jobOrchestrator;

  public Application(
      final ApplicationContext context,
      final String application,
      final Map<String, String> envMap,
      final JobRunConfig jobRunConfig,
      final KubePodInfo kubePodInfo,
      final FeatureFlags featureFlags,
      final ProcessFactory processFactory,
      final JobOrchestrator<?> jobOrchestrator) {
    this.context = context;
    this.application = application;
    this.envMap = envMap;
    this.jobRunConfig = jobRunConfig;
    this.kubePodInfo = kubePodInfo;
    this.configs = new EnvConfigs(envMap);
    this.featureFlags = featureFlags;
//    this.processFactory = processFactory;
    this.jobOrchestrator = jobOrchestrator;
  }

  /**
   * Configures logging/mdc scope, and creates all objects necessary to handle state updates.
   * Everything else is delegated to {@link Application#runInternal}.
   */
  int run() {
    configureLogging();

    // set mdc scope for the remaining execution
    try (final var mdcScope = new MdcScope.Builder()
        .setLogPrefix(application)
        .setPrefixColor(LoggingHelper.Color.CYAN_BACKGROUND)
        .build()) {

      // IMPORTANT: Changing the storage location will orphan already existing kube pods when the new
      // version is deployed!
      final var documentStoreClient = StateClients.create(configs.getStateStorageCloudConfigs(),
          STATE_STORAGE_PREFIX);
      final var asyncStateManager = context.createBean(AsyncStateManager.class,
          documentStoreClient);
      // final var asyncStateManager = new AsyncStateManager(documentStoreClient);
      return runInternal(asyncStateManager);
    }
  }

  /**
   * Handles state updates (including writing failures) and running the job orchestrator. As much of
   * the initialization as possible should go in here, so it's logged properly and the state storage
   * is updated appropriately.
   */
  private int runInternal(final AsyncStateManager asyncStateManager) {
    try {
      asyncStateManager.write(kubePodInfo, AsyncKubePodStatus.INITIALIZING);

//      final var workerConfigs = new WorkerConfigs(configs);
//      final var processFactory = getProcessBuilderFactory(configs, workerConfigs);
//      final var jobOrchestrator = getJobOrchestrator(configs, workerConfigs,
//          processFactory, application, featureFlags);

//      if (jobOrchestrator == null) {
//        throw new IllegalStateException(
//            "Could not find job orchestrator for application: " + application);
//      }

      asyncStateManager.write(kubePodInfo, AsyncKubePodStatus.RUNNING);
      asyncStateManager.write(kubePodInfo, AsyncKubePodStatus.SUCCEEDED,
          jobOrchestrator.runJob().orElse(""));

      // required to kill clients with thread pools
      return 0;
    } catch (final Throwable t) {
      log.error("Killing orchestrator because of an Exception", t);
      asyncStateManager.write(kubePodInfo, AsyncKubePodStatus.FAILED);
      return 1;
    }
  }

  private void configureLogging() {
//    OrchestratorConstants.ENV_VARS_TO_TRANSFER.stream()
//        .filter(envMap::containsKey)
//        .forEach(envVar -> System.setProperty(envVar, envMap.get(envVar)));
//
//    // make sure the new configuration is picked up
//    final LoggerContext ctx = (LoggerContext) LogManager.getContext(false);
//    ctx.reconfigure();
//
//    LogClientSingleton.getInstance().setJobMdc(
//        configs.getWorkerEnvironment(),
//        configs.getLogConfigs(),
//        TemporalUtils.getJobRoot(
//            configs.getWorkspaceRoot(), jobRunConfig.getJobId(), jobRunConfig.getAttemptId()));
  }

//  private JobOrchestrator<?> getJobOrchestrator(final Configs configs,
//      final WorkerConfigs workerConfigs,
//      final ProcessFactory processFactory,
//      final String application,
//      final FeatureFlags featureFlags) {
//    return switch (application) {
//      case ReplicationLauncherWorker.REPLICATION ->
//          new ReplicationJobOrchestrator(configs, processFactory, featureFlags);
//      case NormalizationLauncherWorker.NORMALIZATION ->
//          new NormalizationJobOrchestrator(configs, processFactory);
//      case DbtLauncherWorker.DBT -> new DbtJobOrchestrator(configs, workerConfigs, processFactory);
//      case AsyncOrchestratorPodProcess.NO_OP -> new NoOpOrchestrator();
//      default -> null;
//    };
//  }
//
//  /**
//   * Creates a process builder factory that will be used to create connector containers/pods.
//   */
//  private ProcessFactory getProcessBuilderFactory(final Configs configs,
//      final WorkerConfigs workerConfigs)
//      throws IOException {
//    if (configs.getWorkerEnvironment() == Configs.WorkerEnvironment.KUBERNETES) {
//      final var localIp = InetAddress.getLocalHost().getHostAddress();
//      // TODO move port to configuration
//      final var kubeHeartbeatUrl = localIp + ":" + KUBE_HEARTBEAT_PORT;
//      log.info("Using Kubernetes namespace: {}", configs.getJobKubeNamespace());
//
//      // this needs to have two ports for the source and two ports for the destination (all four must be
//      // exposed)
//      KubePortManagerSingleton.init(OrchestratorConstants.PORTS);
//
//      return new KubeProcessFactory(workerConfigs,
//          configs.getJobKubeNamespace(),
//          new DefaultKubernetesClient(),
//          kubeHeartbeatUrl,
//          false);
//    } else {
//      return new DockerProcessFactory(
//          workerConfigs,
//          configs.getWorkspaceRoot(),
//          configs.getWorkspaceDockerMount(),
//          configs.getLocalDockerMount(),
//          configs.getDockerNetwork());
//    }
//  }

}
