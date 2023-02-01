/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.server.RequestLogger;
import io.airbyte.commons.server.errors.*;
import io.airbyte.commons.server.handlers.*;
import io.airbyte.commons.server.scheduler.DefaultSynchronousSchedulerClient;
import io.airbyte.commons.server.scheduler.EventRunner;
import io.airbyte.commons.server.scheduler.TemporalEventRunner;
import io.airbyte.commons.server.services.AirbyteGithubStore;
import io.airbyte.commons.temporal.ConnectionManagerUtils;
import io.airbyte.commons.temporal.StreamResetRecordsHelper;
import io.airbyte.commons.temporal.TemporalClient;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.TemporalWorkflowUtils;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
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
import io.airbyte.db.factory.DatabaseCheckFactory;
import io.airbyte.persistence.job.DefaultJobPersistence;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.WebUrlHelper;
import io.airbyte.persistence.job.WorkspaceHelper;
import io.airbyte.persistence.job.errorreporter.JobErrorReporter;
import io.airbyte.persistence.job.errorreporter.JobErrorReportingClient;
import io.airbyte.persistence.job.errorreporter.JobErrorReportingClientFactory;
import io.airbyte.persistence.job.factory.OAuthConfigSupplier;
import io.airbyte.persistence.job.tracker.JobTracker;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.workers.helper.ConnectionHelper;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.flywaydb.core.Flyway;
import org.glassfish.jersey.jackson.internal.jackson.jaxrs.json.JacksonJaxbJsonProvider;
import org.glassfish.jersey.server.ResourceConfig;
import org.glassfish.jersey.servlet.ServletContainer;
import org.jooq.DSLContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

@SuppressWarnings("PMD.AvoidCatchingThrowable")
public class ServerApp implements ServerRunnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(ServerApp.class);
  private static final int PORT = 8001;

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

  public static void assertDatabasesReady(final Configs configs,
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
    final SecretsRepositoryWriter secretsRepositoryWriter = new SecretsRepositoryWriter(configRepository, secretPersistence,
        ephemeralSecretPersistence);

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

    final FeatureFlags envVariableFeatureFlags = new EnvVariableFeatureFlags();

    final WebUrlHelper webUrlHelper = new WebUrlHelper(configs.getWebappUrl());
    final JobErrorReportingClient jobErrorReportingClient = JobErrorReportingClientFactory.getClient(configs.getJobErrorReportingStrategy(), configs);
    final JobErrorReporter jobErrorReporter =
        new JobErrorReporter(
            configRepository,
            configs.getDeploymentMode(),
            configs.getAirbyteVersionOrWarning(),
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

    final ConnectionHelper connectionHelper = new ConnectionHelper(configRepository, workspaceHelper);

    final ConnectionsHandler connectionsHandler = new ConnectionsHandler(
        configRepository,
        workspaceHelper,
        trackingClient,
        eventRunner,
        connectionHelper);

    final DestinationHandler destinationHandler = new DestinationHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler,
        oAuthConfigSupplier);

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
        connectionsHandler,
        envVariableFeatureFlags);

    final AirbyteProtocolVersionRange airbyteProtocolVersionRange = new AirbyteProtocolVersionRange(configs.getAirbyteProtocolVersionMin(),
        configs.getAirbyteProtocolVersionMax());

    final AirbyteGithubStore airbyteGithubStore = AirbyteGithubStore.production();

    final DestinationDefinitionsHandler destinationDefinitionsHandler = new DestinationDefinitionsHandler(configRepository,
        () -> UUID.randomUUID(),
        syncSchedulerClient,
        airbyteGithubStore,
        destinationHandler,
        airbyteProtocolVersionRange);

    final HealthCheckHandler healthCheckHandler = new HealthCheckHandler(configRepository);

    final OAuthHandler oAuthHandler = new OAuthHandler(configRepository, httpClient, trackingClient, secretsRepositoryReader);

    final SourceHandler sourceHandler = new SourceHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler,
        oAuthConfigSupplier);

    final SourceDefinitionsHandler sourceDefinitionsHandler =
        new SourceDefinitionsHandler(configRepository, () -> UUID.randomUUID(), syncSchedulerClient, airbyteGithubStore, sourceHandler,
            airbyteProtocolVersionRange);

    final JobHistoryHandler jobHistoryHandler = new JobHistoryHandler(
        jobPersistence,
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        connectionsHandler,
        sourceHandler,
        sourceDefinitionsHandler,
        destinationHandler,
        destinationDefinitionsHandler,
        configs.getAirbyteVersion(),
        temporalClient);

    final LogsHandler logsHandler = new LogsHandler(configs);

    final WorkspacesHandler workspacesHandler = new WorkspacesHandler(
        configRepository,
        secretsRepositoryWriter,
        connectionsHandler,
        destinationHandler,
        sourceHandler);

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

    final WebBackendCheckUpdatesHandler webBackendCheckUpdatesHandler =
        new WebBackendCheckUpdatesHandler(configRepository, AirbyteGithubStore.production());

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
        destinationDefinitionsHandler,
        destinationHandler,
        healthCheckHandler,
        jobHistoryHandler,
        logsHandler,
        oAuthHandler,
        new OpenApiConfigHandler(),
        operationsHandler,
        schedulerHandler,
        sourceHandler,
        sourceDefinitionsHandler,
        stateHandler,
        workspacesHandler,
        webBackendConnectionsHandler,
        webBackendGeographiesHandler,
        webBackendCheckUpdatesHandler);
  }

}
