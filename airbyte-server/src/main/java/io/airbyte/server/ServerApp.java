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

package io.airbyte.server;

import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.ConfigSeedProvider;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.YamlSeedConfigPersistence;
import io.airbyte.db.Database;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.scheduler.client.DefaultSchedulerJobClient;
import io.airbyte.scheduler.client.DefaultSynchronousSchedulerClient;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.client.SpecCachingSynchronousSchedulerClient;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
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
  private final String airbyteVersion;
  private final Set<Class<?>> customComponentClasses;
  private final Set<Object> customComponents;

  public ServerApp(final String airbyteVersion,
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

    ServletHolder configServlet = new ServletHolder(new ServletContainer(rc));

    handler.addServlet(configServlet, "/api/*");

    server.setHandler(handler);

    server.start();
    final String banner = MoreResources.readResource("banner/banner.txt");
    LOGGER.info(banner + String.format("Version: %s\n", airbyteVersion));
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

  public static ServerRunnable getServer(ServerFactory apiFactory) throws Exception {
    final Configs configs = new EnvConfigs();

    MDC.put(LogClientSingleton.WORKSPACE_MDC_KEY, LogClientSingleton.getServerLogsRoot(configs).toString());

    LOGGER.info("Creating config repository...");
    final Database configDatabase = new ConfigsDatabaseInstance(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl())
            .getAndInitialize();
    final ConfigPersistence configPersistence = new DatabaseConfigPersistence(configDatabase)
        .loadData(ConfigSeedProvider.get(configs))
        .withValidation();
    final ConfigRepository configRepository = new ConfigRepository(configPersistence);

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

    // must happen after the tracking client is initialized.
    // if no workspace exists, we create one so the user starts out with a place to add configuration.
    createWorkspaceIfNoneExists(configRepository);

    final String airbyteVersion = configs.getAirbyteVersion();
    if (jobPersistence.getVersion().isEmpty()) {
      LOGGER.info(String.format("Setting Database version to %s...", airbyteVersion));
      jobPersistence.setVersion(airbyteVersion);
    }

    Optional<String> airbyteDatabaseVersion = jobPersistence.getVersion();
    if (airbyteDatabaseVersion.isPresent() && isDatabaseVersionBehindAppVersion(airbyteVersion, airbyteDatabaseVersion.get())) {
      boolean isKubernetes = configs.getWorkerEnvironment() == WorkerEnvironment.KUBERNETES;
      boolean versionSupportsAutoMigrate =
          new AirbyteVersion(airbyteDatabaseVersion.get()).patchVersionCompareTo(KUBE_SUPPORT_FOR_AUTOMATIC_MIGRATION) >= 0;
      if (!isKubernetes || versionSupportsAutoMigrate) {
        runAutomaticMigration(configRepository, jobPersistence, airbyteVersion, airbyteDatabaseVersion.get());
        // After migration, upgrade the DB version
        airbyteDatabaseVersion = jobPersistence.getVersion();
      } else {
        LOGGER.info("Can not run automatic migration for Airbyte on KUBERNETES before version " + KUBE_SUPPORT_FOR_AUTOMATIC_MIGRATION.getVersion());
      }
    }

    runFlywayMigration(configs, configDatabase, jobDatabase);

    if (airbyteDatabaseVersion.isPresent() && AirbyteVersion.isCompatible(airbyteVersion, airbyteDatabaseVersion.get())) {
      LOGGER.info("Starting server...");

      final JobTracker jobTracker = new JobTracker(configRepository, jobPersistence);
      final WorkflowServiceStubs temporalService = TemporalUtils.createTemporalService(configs.getTemporalHost());
      final TemporalClient temporalClient = TemporalClient.production(configs.getTemporalHost(), configs.getWorkspaceRoot());
      final SchedulerJobClient schedulerJobClient = new DefaultSchedulerJobClient(jobPersistence, new DefaultJobCreator(jobPersistence));
      final DefaultSynchronousSchedulerClient syncSchedulerClient = new DefaultSynchronousSchedulerClient(temporalClient, jobTracker);
      final SpecCachingSynchronousSchedulerClient cachingSchedulerClient = new SpecCachingSynchronousSchedulerClient(syncSchedulerClient);

      return apiFactory.create(
          schedulerJobClient,
          cachingSchedulerClient,
          temporalService,
          configRepository,
          jobPersistence,
          configDatabase,
          jobDatabase,
          configs);
    } else {
      LOGGER.info("Start serving version mismatch errors. Automatic migration either failed or didn't run");
      return new VersionMismatchServer(airbyteVersion, airbyteDatabaseVersion.orElseThrow(), PORT);
    }
  }

  public static void main(String[] args) throws Exception {
    getServer(new ServerFactory.Api()).start();
  }

  /**
   * Ideally when automatic migration runs, we should make sure that we acquire a lock on database and
   * no other operation is allowed
   */
  private static void runAutomaticMigration(ConfigRepository configRepository,
                                            JobPersistence jobPersistence,
                                            String airbyteVersion,
                                            String airbyteDatabaseVersion) {
    LOGGER.info("Running Automatic Migration from version : " + airbyteDatabaseVersion + " to version : " + airbyteVersion);
    try (final RunMigration runMigration = new RunMigration(
        jobPersistence,
        configRepository,
        airbyteVersion,
        YamlSeedConfigPersistence.get())) {
      runMigration.run();
    } catch (Exception e) {
      LOGGER.error("Automatic Migration failed ", e);
    }
  }

  public static boolean isDatabaseVersionBehindAppVersion(String airbyteVersion, String airbyteDatabaseVersion) {
    boolean bothVersionsCompatible = AirbyteVersion.isCompatible(airbyteVersion, airbyteDatabaseVersion);
    if (bothVersionsCompatible) {
      return false;
    }

    AirbyteVersion serverVersion = new AirbyteVersion(airbyteVersion);
    AirbyteVersion databaseVersion = new AirbyteVersion(airbyteDatabaseVersion);

    if (databaseVersion.getMajorVersion().compareTo(serverVersion.getMajorVersion()) < 0) {
      return true;
    }

    return databaseVersion.getMinorVersion().compareTo(serverVersion.getMinorVersion()) < 0;
  }

  private static void runFlywayMigration(Configs configs, Database configDatabase, Database jobDatabase) {
    DatabaseMigrator configDbMigrator = new ConfigsDatabaseMigrator(configDatabase, ServerApp.class.getSimpleName());
    DatabaseMigrator jobDbMigrator = new JobsDatabaseMigrator(jobDatabase, ServerApp.class.getSimpleName());

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
