/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.model.LogRead;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.init.YamlSeedConfigPersistence;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.BucketSpecCacheSchedulerClient;
import io.airbyte.scheduler.client.DefaultSchedulerJobClient;
import io.airbyte.scheduler.client.DefaultSynchronousSchedulerClient;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.client.SpecCachingSynchronousSchedulerClient;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.server.converters.JobConverter;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.server.errors.InvalidInputExceptionMapper;
import io.airbyte.server.errors.InvalidJsonExceptionMapper;
import io.airbyte.server.errors.InvalidJsonInputExceptionMapper;
import io.airbyte.server.errors.KnownExceptionMapper;
import io.airbyte.server.errors.NotFoundExceptionMapper;
import io.airbyte.server.errors.UncaughtExceptionMapper;
import io.airbyte.server.version_mismatch.VersionMismatchServer;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.IOException;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.glassfish.jersey.jackson.internal.jackson.jaxrs.json.JacksonJaxbJsonProvider;
import org.glassfish.jersey.server.ResourceConfig;
import org.glassfish.jersey.servlet.ServletContainer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class ServerApp implements ServerRunnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(ServerApp.class);
  private static final int PORT = 8001;
  /**
   * We can't support automatic migration for kube before this version because we had a bug in kube
   * which would cause airbyte db to erase state upon termination, as a result the automatic migration
   * wouldn't run
   */
  private static final AirbyteVersion KUBE_SUPPORT_FOR_AUTOMATIC_MIGRATION = new AirbyteVersion("0.26.5-alpha");
  private final AirbyteVersion airbyteVersion;
  private final Set<Class<?>> customComponentClasses;
  private final Set<Object> customComponents;

  public ServerApp(final AirbyteVersion airbyteVersion,
                   final Set<Class<?>> customComponentClasses,
                   final Set<Object> customComponents) {
    this.airbyteVersion = airbyteVersion;
    this.customComponentClasses = customComponentClasses;
    this.customComponents = customComponents;
  }

  @Override
  public void start() throws Exception {
    final Server server = new Server(PORT);

    final ServletContextHandler handler = new ServletContextHandler();

    final Map<String, String> mdc = MDC.getCopyOfContextMap();

    final ResourceConfig rc =
        new ResourceConfig()
            .register(new RequestLogger(mdc))
            .register(InvalidInputExceptionMapper.class)
            .register(InvalidJsonExceptionMapper.class)
            .register(InvalidJsonInputExceptionMapper.class)
            .register(KnownExceptionMapper.class)
            .register(UncaughtExceptionMapper.class)
            .register(NotFoundExceptionMapper.class)
            // needed so that the custom json exception mappers don't get overridden
            // https://stackoverflow.com/questions/35669774/jersey-custom-exception-mapper-for-invalid-json-string
            .register(JacksonJaxbJsonProvider.class);

    // inject custom server functionality
    customComponentClasses.forEach(rc::register);
    customComponents.forEach(rc::register);

    final ServletHolder configServlet = new ServletHolder(new ServletContainer(rc));

    handler.addServlet(configServlet, "/api/*");

    server.setHandler(handler);

    server.start();
    final String banner = MoreResources.readResource("banner/banner.txt");
    LOGGER.info(banner + String.format("Version: %s\n", airbyteVersion.serialize()));
    server.join();
  }

  private static void createDeploymentIfNoneExists(final JobPersistence jobPersistence) throws IOException {
    final Optional<UUID> deploymentOptional = jobPersistence.getDeployment();
    if (deploymentOptional.isPresent()) {
      LOGGER.info("running deployment: {}", deploymentOptional.get());
    } else {
      final UUID deploymentId = UUID.randomUUID();
      jobPersistence.setDeployment(deploymentId);
      LOGGER.info("created deployment: {}", deploymentId);
    }
  }

  private static void createWorkspaceIfNoneExists(final ConfigRepository configRepository) throws JsonValidationException, IOException {
    if (!configRepository.listStandardWorkspaces(true).isEmpty()) {
      LOGGER.info("workspace already exists for the deployment.");
      return;
    }

    final UUID workspaceId = UUID.randomUUID();
    final StandardWorkspace workspace = new StandardWorkspace()
        .withWorkspaceId(workspaceId)
        .withCustomerId(UUID.randomUUID())
        .withName(workspaceId.toString())
        .withSlug(workspaceId.toString())
        .withInitialSetupComplete(false)
        .withDisplaySetupWizard(true)
        .withTombstone(false);
    configRepository.writeStandardWorkspace(workspace);
    TrackingClientSingleton.get().identify(workspaceId);
  }

  public static ServerRunnable getServer(final ServerFactory apiFactory, final ConfigPersistence seed) throws Exception {
    final Configs configs = new EnvConfigs();

    LogClientSingleton.getInstance().setWorkspaceMdc(configs.getWorkerEnvironment(), configs.getLogConfigs(),
        LogClientSingleton.getInstance().getServerLogsRoot(configs.getWorkspaceRoot()));

    LOGGER.info("Creating Staged Resource folder...");
    ConfigDumpImporter.initStagedResourceFolder();

    LOGGER.info("Creating config repository...");
    final Database configDatabase = new ConfigsDatabaseInstance(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl())
            .getAndInitialize();
    final DatabaseConfigPersistence configPersistence = new DatabaseConfigPersistence(configDatabase).migrateFileConfigs(configs);

    final SecretsHydrator secretsHydrator = SecretPersistence.getSecretsHydrator(configs);
    final Optional<SecretPersistence> secretPersistence = SecretPersistence.getLongLived(configs);
    final Optional<SecretPersistence> ephemeralSecretPersistence = SecretPersistence.getEphemeral(configs);

    final ConfigRepository configRepository =
        new ConfigRepository(configPersistence.withValidation(), secretsHydrator, secretPersistence, ephemeralSecretPersistence);

    LOGGER.info("Creating Scheduler persistence...");
    final Database jobDatabase = new JobsDatabaseInstance(
        configs.getDatabaseUser(),
        configs.getDatabasePassword(),
        configs.getDatabaseUrl())
            .getAndInitialize();
    final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);

    createDeploymentIfNoneExists(jobPersistence);

    // must happen after deployment id is set
    TrackingClientSingleton.initialize(
        configs.getTrackingStrategy(),
        new Deployment(configs.getDeploymentMode(), jobPersistence.getDeployment().orElseThrow(), configs.getWorkerEnvironment()),
        configs.getAirbyteRole(),
        configs.getAirbyteVersion(),
        configRepository);
    final TrackingClient trackingClient = TrackingClientSingleton.get();
    // must happen after the tracking client is initialized.
    // if no workspace exists, we create one so the user starts out with a place to add configuration.
    createWorkspaceIfNoneExists(configRepository);

    final AirbyteVersion airbyteVersion = configs.getAirbyteVersion();
    if (jobPersistence.getVersion().isEmpty()) {
      LOGGER.info(String.format("Setting Database version to %s...", airbyteVersion));
      jobPersistence.setVersion(airbyteVersion.serialize());
    }

    final JobTracker jobTracker = new JobTracker(configRepository, jobPersistence, trackingClient);
    final WorkflowServiceStubs temporalService = TemporalUtils.createTemporalService(configs.getTemporalHost());
    final TemporalClient temporalClient = TemporalClient.production(configs.getTemporalHost(), configs.getWorkspaceRoot());
    final OAuthConfigSupplier oAuthConfigSupplier = new OAuthConfigSupplier(configRepository, false, trackingClient);
    final SchedulerJobClient schedulerJobClient =
        new DefaultSchedulerJobClient(jobPersistence, new DefaultJobCreator(jobPersistence, configRepository));
    final DefaultSynchronousSchedulerClient syncSchedulerClient =
        new DefaultSynchronousSchedulerClient(temporalClient, jobTracker, oAuthConfigSupplier);
    final SynchronousSchedulerClient bucketSpecCacheSchedulerClient =
        new BucketSpecCacheSchedulerClient(syncSchedulerClient, configs.getSpecCacheBucket());
    final SpecCachingSynchronousSchedulerClient cachingSchedulerClient = new SpecCachingSynchronousSchedulerClient(bucketSpecCacheSchedulerClient);
    final SpecFetcher specFetcher = new SpecFetcher(cachingSchedulerClient);

    // todo (cgardens) - this method is deprecated. new migrations are not run using this code path. it
    // is scheduled to be removed.
    final Optional<AirbyteVersion> airbyteDatabaseVersion = runFileMigration(
        airbyteVersion,
        configRepository,
        seed,
        specFetcher,
        jobPersistence,
        configs);

    final HttpClient httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();

    if (airbyteDatabaseVersion.isPresent() && AirbyteVersion.isCompatible(airbyteVersion, airbyteDatabaseVersion.get())) {
      LOGGER.info("Starting server...");

      runFlywayMigration(configs, configDatabase, jobDatabase);
      configPersistence.loadData(seed);

      // todo (lmossman) - this will only exist temporarily to ensure all definitions contain specs. It
      // will be removed after the faux major version bump
      // migrateAllDefinitionsToContainSpec(
      // configRepository,
      // cachingSchedulerClient,
      // trackingClient,
      // configs.getWorkerEnvironment(),
      // configs.getLogConfigs());

      return apiFactory.create(
          schedulerJobClient,
          cachingSchedulerClient,
          temporalService,
          configRepository,
          jobPersistence,
          seed,
          configDatabase,
          jobDatabase,
          trackingClient,
          configs.getWorkerEnvironment(),
          configs.getLogConfigs(),
          configs.getWebappUrl(),
          configs.getAirbyteVersion(),
          configs.getWorkspaceRoot(),
          httpClient);
    } else {
      LOGGER.info("Start serving version mismatch errors. Automatic migration either failed or didn't run");
      return new VersionMismatchServer(airbyteVersion, airbyteDatabaseVersion.orElseThrow(), PORT);
    }
  }

  /**
   * Check that each spec in the database has a spec. If it doesn't, add it. If it can't be added,
   * track the failure in Segment. The goal is to try to end up in a state where all definitions in
   * the db contain specs, and to understand what is stopping us from getting there.
   *
   * @param configRepository - access to the db
   * @param schedulerClient - scheduler client so that specs can be fetched as needed
   * @param trackingClient
   * @param workerEnvironment
   * @param logConfigs
   */
  @VisibleForTesting
  static void migrateAllDefinitionsToContainSpec(final ConfigRepository configRepository,
                                                 final SynchronousSchedulerClient schedulerClient,
                                                 final TrackingClient trackingClient,
                                                 final WorkerEnvironment workerEnvironment,
                                                 final LogConfigs logConfigs)
      throws JsonValidationException, IOException {
    final JobConverter jobConverter = new JobConverter(workerEnvironment, logConfigs);
    for (final StandardSourceDefinition sourceDef : configRepository.listStandardSourceDefinitions()) {
      try {
        if (sourceDef.getSpec() == null) {
          LOGGER.info(
              "migrateAllDefinitionsToContainSpec - Source Definition {} does not have a spec. Attempting to retrieve spec...",
              sourceDef.getName());
          final SynchronousResponse<ConnectorSpecification> getSpecJob = schedulerClient
              .createGetSpecJob(sourceDef.getDockerRepository() + ":" + sourceDef.getDockerImageTag());
          if (getSpecJob.isSuccess()) {
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Spec for Source Definition {} was successfully retrieved. Writing to the db...",
                sourceDef.getName());
            final StandardSourceDefinition updatedDef = Jsons.clone(sourceDef).withSpec(getSpecJob.getOutput());
            configRepository.writeStandardSourceDefinition(updatedDef);
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Spec for Source Definition {} was successfully written to the db record.",
                sourceDef.getName());
          } else {
            final LogRead logRead = jobConverter.getLogRead(getSpecJob.getMetadata().getLogPath());
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Failed to retrieve spec for Source Definition {}. Logs: {}",
                sourceDef.getName(),
                logRead.toString());
            throw new RuntimeException(String.format(
                "Failed to retrieve spec for Source Definition %s. Logs: %s",
                sourceDef.getName(),
                logRead.toString()));
          }
        }
      } catch (final Exception e) {
        trackSpecBackfillFailure(trackingClient, configRepository, sourceDef.getDockerRepository(), sourceDef.getDockerImageTag(), e);
      }
    }

    for (final StandardDestinationDefinition destDef : configRepository.listStandardDestinationDefinitions()) {
      try {
        if (destDef.getSpec() == null) {
          LOGGER.info(
              "migrateAllDefinitionsToContainSpec - Destination Definition {} does not have a spec. Attempting to retrieve spec...",
              destDef.getName());
          final SynchronousResponse<ConnectorSpecification> getSpecJob = schedulerClient
              .createGetSpecJob(destDef.getDockerRepository() + ":" + destDef.getDockerImageTag());
          if (getSpecJob.isSuccess()) {
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Spec for Destination Definition {} was successfully retrieved. Writing to the db...",
                destDef.getName());
            final StandardDestinationDefinition updatedDef = Jsons.clone(destDef).withSpec(getSpecJob.getOutput());
            configRepository.writeStandardDestinationDefinition(updatedDef);
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Spec for Destination Definition {} was successfully written to the db record.",
                destDef.getName());
          } else {
            final LogRead logRead = jobConverter.getLogRead(getSpecJob.getMetadata().getLogPath());
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Failed to retrieve spec for Destination Definition {}. Logs: {}",
                destDef.getName(),
                logRead.toString());
            throw new RuntimeException(String.format(
                "Failed to retrieve spec for Destination Definition %s. Logs: %s",
                destDef.getName(),
                logRead.toString()));
          }
        }
      } catch (final Exception e) {
        trackSpecBackfillFailure(trackingClient, configRepository, destDef.getDockerRepository(), destDef.getDockerImageTag(), e);
      }
    }
  }

  private static void trackSpecBackfillFailure(final TrackingClient trackingClient,
                                               final ConfigRepository configRepository,
                                               final String dockerRepo,
                                               final String dockerImageTag,
                                               final Exception exception)
      throws JsonValidationException, IOException {
    // There is guaranteed to be at least one workspace, because the getServer() function enforces that
    final UUID workspaceId = configRepository.listStandardWorkspaces(true).get(0).getWorkspaceId();

    final ImmutableMap<String, Object> metadata = ImmutableMap.of(
        "docker_image_name", dockerRepo,
        "docker_image_tag", dockerImageTag,
        "exception", exception);
    trackingClient.track(workspaceId, "failed_spec_backfill", metadata);
  }

  @Deprecated
  @SuppressWarnings({"DeprecatedIsStillUsed"})
  private static Optional<AirbyteVersion> runFileMigration(final AirbyteVersion airbyteVersion,
                                                           final ConfigRepository configRepository,
                                                           final ConfigPersistence seed,
                                                           final SpecFetcher specFetcher,
                                                           final JobPersistence jobPersistence,
                                                           final Configs configs)
      throws IOException {
    // required before migration
    // TODO: remove this specFetcherFn logic once file migrations are deprecated
    configRepository.setSpecFetcher(dockerImage -> Exceptions.toRuntime(() -> specFetcher.getSpec(dockerImage)));

    Optional<AirbyteVersion> airbyteDatabaseVersion = jobPersistence.getVersion().map(AirbyteVersion::new);
    if (airbyteDatabaseVersion.isPresent() && isDatabaseVersionBehindAppVersion(airbyteVersion, airbyteDatabaseVersion.get())) {
      final boolean isKubernetes = configs.getWorkerEnvironment() == WorkerEnvironment.KUBERNETES;
      final boolean versionSupportsAutoMigrate = airbyteDatabaseVersion.get().greaterThanOrEqualTo(KUBE_SUPPORT_FOR_AUTOMATIC_MIGRATION);
      if (!isKubernetes || versionSupportsAutoMigrate) {
        runAutomaticMigration(configRepository, jobPersistence, seed, specFetcher, airbyteVersion, airbyteDatabaseVersion.get());
        // After migration, upgrade the DB version
        airbyteDatabaseVersion = jobPersistence.getVersion().map(AirbyteVersion::new);
      } else {
        LOGGER.info("Can not run automatic migration for Airbyte on KUBERNETES before version " + KUBE_SUPPORT_FOR_AUTOMATIC_MIGRATION.serialize());
      }
    }

    return airbyteDatabaseVersion;
  }

  public static void main(final String[] args) throws Exception {
    getServer(new ServerFactory.Api(), YamlSeedConfigPersistence.getDefault()).start();
  }

  /**
   * Ideally when automatic migration runs, we should make sure that we acquire a lock on database and
   * no other operation is allowed
   */
  private static void runAutomaticMigration(final ConfigRepository configRepository,
                                            final JobPersistence jobPersistence,
                                            final ConfigPersistence seed,
                                            final SpecFetcher specFetcher,
                                            final AirbyteVersion airbyteVersion,
                                            final AirbyteVersion airbyteDatabaseVersion) {
    LOGGER.info("Running Automatic Migration from version : " + airbyteDatabaseVersion.serialize() + " to version : " + airbyteVersion.serialize());
    try (final RunMigration runMigration = new RunMigration(
        jobPersistence,
        configRepository,
        airbyteVersion,
        seed,
        specFetcher)) {
      runMigration.run();
    } catch (final Exception e) {
      LOGGER.error("Automatic Migration failed ", e);
    }
  }

  public static boolean isDatabaseVersionBehindAppVersion(final AirbyteVersion serverVersion, final AirbyteVersion databaseVersion) {
    final boolean bothVersionsCompatible = AirbyteVersion.isCompatible(serverVersion, databaseVersion);
    if (bothVersionsCompatible) {
      return false;
    }

    if (databaseVersion.getMajorVersion().compareTo(serverVersion.getMajorVersion()) < 0) {
      return true;
    }

    return databaseVersion.getMinorVersion().compareTo(serverVersion.getMinorVersion()) < 0;
  }

  private static void runFlywayMigration(final Configs configs, final Database configDatabase, final Database jobDatabase) {
    final DatabaseMigrator configDbMigrator = new ConfigsDatabaseMigrator(configDatabase, ServerApp.class.getSimpleName());
    final DatabaseMigrator jobDbMigrator = new JobsDatabaseMigrator(jobDatabase, ServerApp.class.getSimpleName());

    configDbMigrator.createBaseline();
    jobDbMigrator.createBaseline();

    if (configs.runDatabaseMigrationOnStartup()) {
      LOGGER.info("Migrating configs database");
      configDbMigrator.migrate();
      LOGGER.info("Migrating jobs database");
      jobDbMigrator.migrate();
    } else {
      LOGGER.info("Auto database migration is skipped");
    }
  }

}
