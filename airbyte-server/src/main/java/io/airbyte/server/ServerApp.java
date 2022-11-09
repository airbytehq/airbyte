/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.lang.CloseableShutdownHook;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.temporal.ConnectionManagerUtils;
import io.airbyte.commons.temporal.StreamResetRecordsHelper;
import io.airbyte.commons.temporal.TemporalClient;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.TemporalWorkflowUtils;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.check.DatabaseCheckException;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseCheckFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.persistence.job.DefaultJobPersistence;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.WebUrlHelper;
import io.airbyte.persistence.job.WorkspaceHelper;
import io.airbyte.persistence.job.errorreporter.JobErrorReporter;
import io.airbyte.persistence.job.errorreporter.JobErrorReportingClient;
import io.airbyte.persistence.job.errorreporter.JobErrorReportingClientFactory;
import io.airbyte.persistence.job.factory.OAuthConfigSupplier;
import io.airbyte.persistence.job.tracker.JobTracker;
import io.airbyte.server.errors.InvalidInputExceptionMapper;
import io.airbyte.server.errors.InvalidJsonExceptionMapper;
import io.airbyte.server.errors.InvalidJsonInputExceptionMapper;
import io.airbyte.server.errors.KnownExceptionMapper;
import io.airbyte.server.errors.NotFoundExceptionMapper;
import io.airbyte.server.errors.UncaughtExceptionMapper;
import io.airbyte.server.handlers.AttemptHandler;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.handlers.DbMigrationHandler;
import io.airbyte.server.handlers.DestinationDefinitionsHandler;
import io.airbyte.server.handlers.DestinationHandler;
import io.airbyte.server.handlers.HealthCheckHandler;
import io.airbyte.server.handlers.JobHistoryHandler;
import io.airbyte.server.handlers.LogsHandler;
import io.airbyte.server.handlers.OAuthHandler;
import io.airbyte.server.handlers.OpenApiConfigHandler;
import io.airbyte.server.handlers.OperationsHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import io.airbyte.server.handlers.SourceDefinitionsHandler;
import io.airbyte.server.handlers.SourceHandler;
import io.airbyte.server.handlers.StateHandler;
import io.airbyte.server.handlers.WebBackendConnectionsHandler;
import io.airbyte.server.handlers.WebBackendGeographiesHandler;
import io.airbyte.server.handlers.WorkspacesHandler;
import io.airbyte.server.scheduler.DefaultSynchronousSchedulerClient;
import io.airbyte.server.scheduler.EventRunner;
import io.airbyte.server.scheduler.TemporalEventRunner;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import javax.sql.DataSource;
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

@SuppressWarnings("PMD.AvoidCatchingThrowable")
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
  @SuppressWarnings("PMD.InvalidLogMessageFormat")
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

    Runtime.getRuntime().addShutdownHook(new Thread(() -> {
      try {
        server.stop();
      } catch (final Exception ex) {
        // silently fail at this stage because server is terminating.
        LOGGER.warn("exception: " + ex);
      }
    }));
  }

  private static void assertDatabasesReady(final Configs configs,
                                           final DSLContext configsDslContext,
                                           final Flyway configsFlyway,
                                           final DSLContext jobsDslContext,
                                           final Flyway jobsFlyway)
      throws DatabaseCheckException {
    LOGGER.info("Checking configs database flyway migration version..");
    DatabaseCheckFactory
        .createConfigsDatabaseMigrationCheck(configsDslContext, configsFlyway, configs.getConfigsDatabaseMinimumFlywayMigrationVersion(),
            configs.getConfigsDatabaseInitializationTimeoutMs())
        .check();

    LOGGER.info("Checking jobs database flyway migration version..");
    DatabaseCheckFactory.createJobsDatabaseMigrationCheck(jobsDslContext, jobsFlyway, configs.getJobsDatabaseMinimumFlywayMigrationVersion(),
        configs.getJobsDatabaseInitializationTimeoutMs()).check();
  }

  public static ServerRunnable getServer(final ServerFactory apiFactory,
                                         final Configs configs,
                                         final DSLContext configsDslContext,
                                         final Flyway configsFlyway,
                                         final DSLContext jobsDslContext,
                                         final Flyway jobsFlyway)
      throws Exception {
    LogClientSingleton.getInstance().setWorkspaceMdc(
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        LogClientSingleton.getInstance().getServerLogsRoot(configs.getWorkspaceRoot()));

    LOGGER.info("Checking databases..");
    assertDatabasesReady(configs, configsDslContext, configsFlyway, jobsDslContext, jobsFlyway);

    LOGGER.info("Creating config repository...");
    final Database configsDatabase = new Database(configsDslContext);
    final SecretsHydrator secretsHydrator = SecretPersistence.getSecretsHydrator(configsDslContext, configs);
    final Optional<SecretPersistence> secretPersistence = SecretPersistence.getLongLived(configsDslContext, configs);
    final Optional<SecretPersistence> ephemeralSecretPersistence = SecretPersistence.getEphemeral(configsDslContext, configs);
    final ConfigRepository configRepository = new ConfigRepository(configsDatabase);
    final SecretsRepositoryReader secretsRepositoryReader = new SecretsRepositoryReader(configRepository, secretsHydrator);
    final SecretsRepositoryWriter secretsRepositoryWriter =
        new SecretsRepositoryWriter(configRepository, secretPersistence, ephemeralSecretPersistence);

    LOGGER.info("Creating jobs persistence...");
    final Database jobsDatabase = new Database(jobsDslContext);
    final JobPersistence jobPersistence = new DefaultJobPersistence(jobsDatabase);

    TrackingClientSingleton.initialize(
        configs.getTrackingStrategy(),
        new Deployment(configs.getDeploymentMode(), jobPersistence.getDeployment().orElseThrow(), configs.getWorkerEnvironment()),
        configs.getAirbyteRole(),
        configs.getAirbyteVersion(),
        configRepository);

    final TrackingClient trackingClient = TrackingClientSingleton.get();
    final JobTracker jobTracker = new JobTracker(configRepository, jobPersistence, trackingClient);

    final WebUrlHelper webUrlHelper = new WebUrlHelper(configs.getWebappUrl());
    final JobErrorReportingClient jobErrorReportingClient = JobErrorReportingClientFactory.getClient(configs.getJobErrorReportingStrategy(), configs);
    final JobErrorReporter jobErrorReporter =
        new JobErrorReporter(
            configRepository,
            configs.getDeploymentMode(),
            configs.getAirbyteVersionOrWarning(),
            NormalizationRunnerFactory.BASE_NORMALIZATION_IMAGE_NAME,
            NormalizationRunnerFactory.NORMALIZATION_VERSION,
            webUrlHelper,
            jobErrorReportingClient);

    final TemporalUtils temporalUtils = new TemporalUtils(
        configs.getTemporalCloudClientCert(),
        configs.getTemporalCloudClientKey(),
        configs.temporalCloudEnabled(),
        configs.getTemporalCloudHost(),
        configs.getTemporalCloudNamespace(),
        configs.getTemporalHost(),
        configs.getTemporalRetentionInDays());

    final StreamResetPersistence streamResetPersistence = new StreamResetPersistence(configsDatabase);
    final WorkflowServiceStubs temporalService = temporalUtils.createTemporalService();
    final ConnectionManagerUtils connectionManagerUtils = new ConnectionManagerUtils();
    final StreamResetRecordsHelper streamResetRecordsHelper = new StreamResetRecordsHelper(jobPersistence, streamResetPersistence);

    final TemporalClient temporalClient = new TemporalClient(
        configs.getWorkspaceRoot(),
        TemporalWorkflowUtils.createWorkflowClient(temporalService, temporalUtils.getNamespace()),
        temporalService,
        streamResetPersistence,
        connectionManagerUtils,
        streamResetRecordsHelper);

    final OAuthConfigSupplier oAuthConfigSupplier = new OAuthConfigSupplier(configRepository, trackingClient);
    final DefaultSynchronousSchedulerClient syncSchedulerClient =
        new DefaultSynchronousSchedulerClient(temporalClient, jobTracker, jobErrorReporter, oAuthConfigSupplier);
    final HttpClient httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
    final EventRunner eventRunner = new TemporalEventRunner(temporalClient);

    final WorkspaceHelper workspaceHelper = new WorkspaceHelper(configRepository, jobPersistence);

    final JsonSchemaValidator schemaValidator = new JsonSchemaValidator();

    final AttemptHandler attemptHandler = new AttemptHandler(jobPersistence);

    final ConnectionsHandler connectionsHandler = new ConnectionsHandler(
        configRepository,
        workspaceHelper,
        trackingClient,
        eventRunner);

    final DestinationHandler destinationHandler = new DestinationHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler);

    final OperationsHandler operationsHandler = new OperationsHandler(configRepository);

    final SchedulerHandler schedulerHandler = new SchedulerHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        syncSchedulerClient,
        jobPersistence,
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        eventRunner,
        connectionsHandler);

    final DbMigrationHandler dbMigrationHandler = new DbMigrationHandler(configsDatabase, configsFlyway, jobsDatabase, jobsFlyway);

    final DestinationDefinitionsHandler destinationDefinitionsHandler = new DestinationDefinitionsHandler(configRepository, syncSchedulerClient,
        destinationHandler);

    final HealthCheckHandler healthCheckHandler = new HealthCheckHandler(configRepository);

    final OAuthHandler oAuthHandler = new OAuthHandler(configRepository, httpClient, trackingClient);

    final SourceHandler sourceHandler = new SourceHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler);

    final SourceDefinitionsHandler sourceDefinitionsHandler = new SourceDefinitionsHandler(configRepository, syncSchedulerClient, sourceHandler);

    final JobHistoryHandler jobHistoryHandler = new JobHistoryHandler(
        jobPersistence,
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        connectionsHandler,
        sourceHandler,
        sourceDefinitionsHandler,
        destinationHandler,
        destinationDefinitionsHandler,
        configs.getAirbyteVersion());

    final LogsHandler logsHandler = new LogsHandler(configs);

    final WorkspacesHandler workspacesHandler = new WorkspacesHandler(
        configRepository,
        secretsRepositoryWriter,
        connectionsHandler,
        destinationHandler,
        sourceHandler);

    final OpenApiConfigHandler openApiConfigHandler = new OpenApiConfigHandler();

    final StatePersistence statePersistence = new StatePersistence(configsDatabase);

    final StateHandler stateHandler = new StateHandler(statePersistence);

    final WebBackendConnectionsHandler webBackendConnectionsHandler = new WebBackendConnectionsHandler(
        connectionsHandler,
        stateHandler,
        sourceHandler,
        destinationHandler,
        jobHistoryHandler,
        schedulerHandler,
        operationsHandler,
        eventRunner,
        configRepository);

    final WebBackendGeographiesHandler webBackendGeographiesHandler = new WebBackendGeographiesHandler();

    LOGGER.info("Starting server...");

    return apiFactory.create(
        syncSchedulerClient,
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        jobPersistence,
        configsDatabase,
        jobsDatabase,
        trackingClient,
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        configs.getAirbyteVersion(),
        configs.getWorkspaceRoot(),
        httpClient,
        eventRunner,
        configsFlyway,
        jobsFlyway,
        attemptHandler,
        connectionsHandler,
        dbMigrationHandler,
        destinationDefinitionsHandler,
        destinationHandler,
        healthCheckHandler,
        jobHistoryHandler,
        logsHandler,
        oAuthHandler,
        openApiConfigHandler,
        operationsHandler,
        schedulerHandler,
        sourceHandler,
        sourceDefinitionsHandler,
        stateHandler,
        workspacesHandler,
        webBackendConnectionsHandler,
        webBackendGeographiesHandler);
  }

  public static void main(final String[] args) {
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

        final Flyway configsFlyway = FlywayFactory.create(configsDataSource, DbMigrationHandler.class.getSimpleName(),
            ConfigsDatabaseMigrator.DB_IDENTIFIER, ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
        final Flyway jobsFlyway = FlywayFactory.create(jobsDataSource, DbMigrationHandler.class.getSimpleName(), JobsDatabaseMigrator.DB_IDENTIFIER,
            JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);

        getServer(new ServerFactory.Api(), configs, configsDslContext, configsFlyway, jobsDslContext, jobsFlyway).start();
      }
    } catch (final Throwable e) {
      LOGGER.error("Server failed", e);
      System.exit(1); // so the app doesn't hang on background threads
    }
  }

}
