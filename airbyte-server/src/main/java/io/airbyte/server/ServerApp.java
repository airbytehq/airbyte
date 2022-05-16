/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.lang.CloseableShutdownHook;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.init.YamlSeedConfigPersistence;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.DatabaseInstance;
import io.airbyte.db.instance.MinimumFlywayMigrationVersionCheck;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.scheduler.client.DefaultSchedulerJobClient;
import io.airbyte.scheduler.client.DefaultSynchronousSchedulerClient;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.client.TemporalEventRunner;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.server.errors.InvalidInputExceptionMapper;
import io.airbyte.server.errors.InvalidJsonExceptionMapper;
import io.airbyte.server.errors.InvalidJsonInputExceptionMapper;
import io.airbyte.server.errors.KnownExceptionMapper;
import io.airbyte.server.errors.NotFoundExceptionMapper;
import io.airbyte.server.errors.UncaughtExceptionMapper;
import io.airbyte.server.handlers.DbMigrationHandler;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.IOException;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import lombok.val;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.flywaydb.core.Flyway;
import org.glassfish.jersey.jackson.internal.jackson.jaxrs.json.JacksonJaxbJsonProvider;
import org.glassfish.jersey.server.ResourceConfig;
import org.glassfish.jersey.servlet.ServletContainer;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class ServerApp implements ServerRunnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(ServerApp.class);
  private static final int PORT = 8001;
  private static final String DRIVER_CLASS_NAME = "org.postgresql.Driver";

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

  private static void assertDatabasesReady(final Configs configs,
                                           final DatabaseInstance configsDatabaseInstance,
                                           final DataSource configsDataSource,
                                           final DatabaseInstance jobsDatabaseInstance,
                                           final DataSource jobsDataSource)
      throws InterruptedException {
    LOGGER.info("Checking configs database flyway migration version..");
    MinimumFlywayMigrationVersionCheck.assertDatabase(configsDatabaseInstance, MinimumFlywayMigrationVersionCheck.DEFAULT_ASSERT_DATABASE_TIMEOUT_MS);
    final Flyway configsFlyway = FlywayFactory.create(configsDataSource, ServerApp.class.getName(), ConfigsDatabaseMigrator.DB_IDENTIFIER,
        ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    val configsMigrator = new ConfigsDatabaseMigrator(configsDatabaseInstance.getInitialized(), configsFlyway);
    MinimumFlywayMigrationVersionCheck.assertMigrations(configsMigrator, configs.getConfigsDatabaseMinimumFlywayMigrationVersion(),
        configs.getConfigsDatabaseInitializationTimeoutMs());

    LOGGER.info("Checking jobs database flyway migration version..");
    MinimumFlywayMigrationVersionCheck.assertDatabase(jobsDatabaseInstance, MinimumFlywayMigrationVersionCheck.DEFAULT_ASSERT_DATABASE_TIMEOUT_MS);
    final Flyway jobsFlyway = FlywayFactory.create(jobsDataSource, ServerApp.class.getName(), JobsDatabaseMigrator.DB_IDENTIFIER,
        JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    val jobsMigrator = new JobsDatabaseMigrator(jobsDatabaseInstance.getInitialized(), jobsFlyway);
    MinimumFlywayMigrationVersionCheck.assertMigrations(jobsMigrator, configs.getJobsDatabaseMinimumFlywayMigrationVersion(),
        configs.getJobsDatabaseInitializationTimeoutMs());

  }

  public static ServerRunnable getServer(final ServerFactory apiFactory,
                                         final ConfigPersistence seed,
                                         final Configs configs,
                                         final DSLContext configsDslContext,
                                         final DataSource configsDataSource,
                                         final DSLContext jobsDslContext,
                                         final DataSource jobsDataSource)
      throws Exception {
    final WorkerConfigs workerConfigs = new WorkerConfigs(configs);

    LogClientSingleton.getInstance().setWorkspaceMdc(
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        LogClientSingleton.getInstance().getServerLogsRoot(configs.getWorkspaceRoot()));

    LOGGER.info("Checking databases..");
    final DatabaseInstance configsDatabaseInstance =
        new ConfigsDatabaseInstance(configsDslContext);
    final DatabaseInstance jobsDatabaseInstance =
        new JobsDatabaseInstance(jobsDslContext);
    assertDatabasesReady(configs, configsDatabaseInstance, configsDataSource, jobsDatabaseInstance, jobsDataSource);

    LOGGER.info("Creating Staged Resource folder...");
    ConfigDumpImporter.initStagedResourceFolder();

    LOGGER.info("Creating config repository...");
    final Database configDatabase = configsDatabaseInstance.getInitialized();
    final FeatureFlags featureFlags = new EnvVariableFeatureFlags();
    final JsonSecretsProcessor jsonSecretsProcessor = JsonSecretsProcessor.builder()
        .maskSecrets(!featureFlags.exposeSecretsInExport())
        .copySecrets(false)
        .build();
    final ConfigPersistence configPersistence = DatabaseConfigPersistence.createWithValidation(configDatabase, jsonSecretsProcessor);
    final SecretsHydrator secretsHydrator = SecretPersistence.getSecretsHydrator(configsDslContext, configs);
    final Optional<SecretPersistence> secretPersistence = SecretPersistence.getLongLived(configsDslContext, configs);
    final Optional<SecretPersistence> ephemeralSecretPersistence = SecretPersistence.getEphemeral(configsDslContext, configs);
    final ConfigRepository configRepository = new ConfigRepository(configPersistence, configDatabase);
    final SecretsRepositoryReader secretsRepositoryReader = new SecretsRepositoryReader(configRepository, secretsHydrator);
    final SecretsRepositoryWriter secretsRepositoryWriter =
        new SecretsRepositoryWriter(configRepository, secretPersistence, ephemeralSecretPersistence);

    LOGGER.info("Creating jobs persistence...");
    final Database jobDatabase = jobsDatabaseInstance.getInitialized();
    final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);

    TrackingClientSingleton.initialize(
        configs.getTrackingStrategy(),
        new Deployment(configs.getDeploymentMode(), jobPersistence.getDeployment().orElseThrow(), configs.getWorkerEnvironment()),
        configs.getAirbyteRole(),
        configs.getAirbyteVersion(),
        configRepository);

    final TrackingClient trackingClient = TrackingClientSingleton.get();
    final JobTracker jobTracker = new JobTracker(configRepository, jobPersistence, trackingClient);

    final WorkflowServiceStubs temporalService = TemporalUtils.createTemporalService(configs.getTemporalHost());
    final TemporalClient temporalClient = TemporalClient.production(configs.getTemporalHost(), configs.getWorkspaceRoot(), configs);
    final OAuthConfigSupplier oAuthConfigSupplier = new OAuthConfigSupplier(configRepository, trackingClient);
    final SchedulerJobClient schedulerJobClient =
        new DefaultSchedulerJobClient(
            configs.connectorSpecificResourceDefaultsEnabled(),
            jobPersistence,
            new DefaultJobCreator(jobPersistence, configRepository, workerConfigs.getResourceRequirements()));
    final DefaultSynchronousSchedulerClient syncSchedulerClient =
        new DefaultSynchronousSchedulerClient(temporalClient, jobTracker, oAuthConfigSupplier);
    final HttpClient httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
    final EventRunner eventRunner = new TemporalEventRunner(
        TemporalClient.production(configs.getTemporalHost(), configs.getWorkspaceRoot(), configs));

    final Flyway configsFlyway = FlywayFactory.create(configsDataSource, DbMigrationHandler.class.getSimpleName(),
        ConfigsDatabaseMigrator.DB_IDENTIFIER, ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    final Flyway jobsFlyway = FlywayFactory.create(jobsDataSource, DbMigrationHandler.class.getSimpleName(), JobsDatabaseMigrator.DB_IDENTIFIER,
        JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);

    LOGGER.info("Starting server...");

    return apiFactory.create(
        schedulerJobClient,
        syncSchedulerClient,
        temporalService,
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        jobPersistence,
        seed,
        configDatabase,
        jobDatabase,
        trackingClient,
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        workerConfigs,
        configs.getWebappUrl(),
        configs.getAirbyteVersion(),
        configs.getWorkspaceRoot(),
        httpClient,
        featureFlags,
        eventRunner,
        configsFlyway,
        jobsFlyway);
  }

  private static void migrateExistingConnection(final ConfigRepository configRepository, final EventRunner eventRunner)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    LOGGER.info("Start migration to the new scheduler...");
    final Set<UUID> connectionIds =
        configRepository.listStandardSyncs().stream()
            .filter(standardSync -> standardSync.getStatus() == Status.ACTIVE || standardSync.getStatus() == Status.INACTIVE)
            .map(standardSync -> standardSync.getConnectionId()).collect(Collectors.toSet());
    eventRunner.migrateSyncIfNeeded(connectionIds);
    LOGGER.info("Done migrating to the new scheduler...");
  }

  public static void main(final String[] args) throws Exception {
    try {
      final Configs configs = new EnvConfigs();

      // Manual configuration that will be replaced by Dependency Injection in the future
      final DataSource configsDataSource =
          DataSourceFactory.create(configs.getConfigDatabaseUser(), configs.getConfigDatabasePassword(), DRIVER_CLASS_NAME,
              configs.getConfigDatabaseUrl());
      final DataSource jobsDataSource =
          DataSourceFactory.create(configs.getDatabaseUser(), configs.getDatabasePassword(), DRIVER_CLASS_NAME, configs.getDatabaseUrl());

      try (final DSLContext configsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES);
          final DSLContext jobsDslContext = DSLContextFactory.create(jobsDataSource, SQLDialect.POSTGRES)) {

        // Ensure that the database resources are closed on application shutdown
        CloseableShutdownHook.registerRuntimeShutdownHook(configsDataSource, jobsDataSource, configsDslContext, jobsDslContext);

        getServer(new ServerFactory.Api(), YamlSeedConfigPersistence.getDefault(),
            configs, configsDslContext, configsDataSource, jobsDslContext, jobsDataSource).start();
      }
    } catch (final Throwable e) {
      LOGGER.error("Server failed", e);
      System.exit(1); // so the app doesn't hang on background threads
    }
  }

}
