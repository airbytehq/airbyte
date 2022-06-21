/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.utils;

import static java.lang.Thread.sleep;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import com.google.common.io.Resources;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.JobsApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.AirbyteCatalog;
import io.airbyte.api.client.model.generated.AttemptInfoRead;
import io.airbyte.api.client.model.generated.ConnectionCreate;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionRead;
import io.airbyte.api.client.model.generated.ConnectionSchedule;
import io.airbyte.api.client.model.generated.ConnectionStatus;
import io.airbyte.api.client.model.generated.ConnectionUpdate;
import io.airbyte.api.client.model.generated.DestinationCreate;
import io.airbyte.api.client.model.generated.DestinationDefinitionCreate;
import io.airbyte.api.client.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationDefinitionRead;
import io.airbyte.api.client.model.generated.DestinationIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationRead;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.api.client.model.generated.JobRead;
import io.airbyte.api.client.model.generated.JobStatus;
import io.airbyte.api.client.model.generated.NamespaceDefinitionType;
import io.airbyte.api.client.model.generated.OperationCreate;
import io.airbyte.api.client.model.generated.OperationIdRequestBody;
import io.airbyte.api.client.model.generated.OperationRead;
import io.airbyte.api.client.model.generated.OperatorConfiguration;
import io.airbyte.api.client.model.generated.OperatorNormalization;
import io.airbyte.api.client.model.generated.OperatorType;
import io.airbyte.api.client.model.generated.SourceCreate;
import io.airbyte.api.client.model.generated.SourceDefinitionCreate;
import io.airbyte.api.client.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.SourceDefinitionRead;
import io.airbyte.api.client.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.client.model.generated.SourceIdRequestBody;
import io.airbyte.api.client.model.generated.SourceRead;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreProperties;
import io.airbyte.db.Database;
import io.airbyte.test.airbyte_test_container.AirbyteTestContainer;
import io.airbyte.workers.temporal.TemporalUtils;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class AirbyteAcceptanceTestHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteAcceptanceTestHelper.class);

  private static final String DOCKER_COMPOSE_FILE_NAME = "docker-compose.yaml";
  // assume env file is one directory level up from airbyte-tests.
  private final static File ENV_FILE = Path.of(System.getProperty("user.dir")).getParent().resolve(".env").toFile();

  private static final String SOURCE_E2E_TEST_CONNECTOR_VERSION = "0.1.1";
  private static final String DESTINATION_E2E_TEST_CONNECTOR_VERSION = "0.1.1";

  private static final boolean IS_MAC = System.getProperty("os.name").startsWith("Mac");
  private static final boolean USE_EXTERNAL_DEPLOYMENT =
      System.getenv("USE_EXTERNAL_DEPLOYMENT") != null && System.getenv("USE_EXTERNAL_DEPLOYMENT").equalsIgnoreCase("true");

  private static final String OUTPUT_NAMESPACE_PREFIX = "output_namespace_";
  private static final String OUTPUT_NAMESPACE = OUTPUT_NAMESPACE_PREFIX + "${SOURCE_NAMESPACE}";
  private static final String OUTPUT_STREAM_PREFIX = "output_table_";
  private static final String TABLE_NAME = "id_and_name";
  public static final String STREAM_NAME = TABLE_NAME;
  public static final String COLUMN_ID = "id";
  public static final String COLUMN_NAME = "name";
  private static final String COLUMN_NAME_DATA = "_airbyte_data";
  private static final String SOURCE_USERNAME = "sourceusername";
  private static final String SOURCE_PASSWORD = "hunter2";

  /**
   * When the acceptance tests are run against a local instance of docker-compose these test
   * containers are used.
   */
  private PostgreSQLContainer sourcePsql;
  private PostgreSQLContainer destinationPsql;
  private AirbyteTestContainer airbyteTestContainer;
  private AirbyteApiClient apiClient; // todo let users pass this in
  private UUID workspaceId;

  private List<UUID> sourceIds;
  private List<UUID> connectionIds;
  private List<UUID> destinationIds;
  private List<UUID> operationIds;

  public PostgreSQLContainer getSourcePsql() {
    return sourcePsql;
  }

  public PostgreSQLContainer getDestinationPsql() {
    return destinationPsql;
  }

  public void removeConnection(final UUID connection) {
    connectionIds.remove(connection);
  }

  @SuppressWarnings("UnstableApiUsage")
  public void init(final AirbyteApiClient apiClient) throws URISyntaxException, IOException, InterruptedException, ApiException {
    sourcePsql = new PostgreSQLContainer("postgres:13-alpine")
        .withUsername(SOURCE_USERNAME)
        .withPassword(SOURCE_PASSWORD);
    sourcePsql.start();

    // by default use airbyte deployment governed by a test container.
    if (!USE_EXTERNAL_DEPLOYMENT) {
      LOGGER.info("Using deployment of airbyte managed by test containers.");
      airbyteTestContainer = new AirbyteTestContainer.Builder(new File(Resources.getResource(DOCKER_COMPOSE_FILE_NAME).toURI()))
          .setEnv(MoreProperties.envFileToProperties(ENV_FILE))
          // override env VERSION to use dev to test current build of airbyte.
          .setEnvVariable("VERSION", "dev")
          // override to use test mounts.
          .setEnvVariable("DATA_DOCKER_MOUNT", "airbyte_data_migration_test")
          .setEnvVariable("DB_DOCKER_MOUNT", "airbyte_db_migration_test")
          .setEnvVariable("WORKSPACE_DOCKER_MOUNT", "airbyte_workspace_migration_test")
          .setEnvVariable("LOCAL_ROOT", "/tmp/airbyte_local_migration_test")
          .setEnvVariable("LOCAL_DOCKER_MOUNT", "/tmp/airbyte_local_migration_test")
          .build();
      airbyteTestContainer.startBlocking();
    } else {
      LOGGER.info("Using external deployment of airbyte.");
    }

    this.apiClient = apiClient;
    // new AirbyteApiClient(
    // new ApiClient().setScheme("http")
    // .setHost("localhost")
    // .setPort(8001)
    // .setBasePath("/api"));

    // work in whatever default workspace is present.
    workspaceId = apiClient.getWorkspaceApi().listWorkspaces().getWorkspaces().get(0).getWorkspaceId();
    LOGGER.info("workspaceId = " + workspaceId);

    // log which connectors are being used.
    final SourceDefinitionRead sourceDef = apiClient.getSourceDefinitionApi()
        .getSourceDefinition(new SourceDefinitionIdRequestBody()
            .sourceDefinitionId(UUID.fromString("decd338e-5647-4c0b-adf4-da0e75f5a750")));
    final DestinationDefinitionRead destinationDef = apiClient.getDestinationDefinitionApi()
        .getDestinationDefinition(new DestinationDefinitionIdRequestBody()
            .destinationDefinitionId(UUID.fromString("25c5221d-dce2-4163-ade9-739ef790f503")));
    LOGGER.info("pg source definition: {}", sourceDef.getDockerImageTag());
    LOGGER.info("pg destination definition: {}", destinationDef.getDockerImageTag());

    destinationPsql = new PostgreSQLContainer("postgres:13-alpine");
    destinationPsql.start();
  }

  public void stopDbAndContainers() {
    sourcePsql.stop();
    destinationPsql.stop();

    if (airbyteTestContainer != null) {
      airbyteTestContainer.stop();
    }
  }

  public void setup() {
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("postgres_init.sql"), sourcePsql);

    destinationPsql = new PostgreSQLContainer("postgres:13-alpine");
    destinationPsql.start();

    sourceIds = Lists.newArrayList();
    connectionIds = Lists.newArrayList();
    destinationIds = Lists.newArrayList();
    operationIds = Lists.newArrayList();
  }

  public void cleanup() {
    try {
      clearSourceDbData();

      for (final UUID operationId : operationIds) {
        deleteOperation(operationId);
      }

      for (final UUID connectionId : connectionIds) {
        disableConnection(connectionId);
      }

      for (final UUID sourceId : sourceIds) {
        deleteSource(sourceId);
      }

      for (final UUID destinationId : destinationIds) {
        deleteDestination(destinationId);
      }
    } catch (final Exception e) {
      LOGGER.error("Error tearing down test fixtures:", e);
    }
  }

  public WorkflowClient getWorkflowClient() {
    final WorkflowServiceStubs temporalService = TemporalUtils.createTemporalService("localhost:7233");
    return WorkflowClient.newInstance(temporalService);
  }

  public WorkflowState getWorkflowState(final UUID connectionId) {
    final WorkflowClient workflowCLient = getWorkflowClient();

    // check if temporal workflow is reachable
    final ConnectionManagerWorkflow connectionManagerWorkflow =
        workflowCLient.newWorkflowStub(ConnectionManagerWorkflow.class, "connection_manager_" + connectionId);

    return connectionManagerWorkflow.getState();
  }

  public void terminateTemporalWorkflow(final UUID connectionId) {
    final WorkflowClient workflowCLient = getWorkflowClient();

    // check if temporal workflow is reachable
    getWorkflowState(connectionId);

    // Terminate workflow
    LOGGER.info("Terminating temporal workflow...");
    workflowCLient.newUntypedWorkflowStub("connection_manager_" + connectionId).terminate("");

    // remove connection to avoid exception during tear down
    connectionIds.remove(connectionId);
  }

  public AirbyteCatalog discoverSourceSchema(final UUID sourceId) throws ApiException {
    return apiClient.getSourceApi().discoverSchemaForSource(new SourceDiscoverSchemaRequestBody().sourceId(sourceId)).getCatalog();
  }

  public void assertSourceAndDestinationDbInSync(final boolean withScdTable) throws Exception {
    final Database source = getSourceDatabase();

    final Set<SchemaTableNamePair> sourceTables = listAllTables(source);
    final Set<SchemaTableNamePair> sourceTablesWithRawTablesAdded = addAirbyteGeneratedTables(withScdTable, sourceTables);
    final Database destination = getDestinationDatabase();
    final Set<SchemaTableNamePair> destinationTables = listAllTables(destination);
    assertEquals(sourceTablesWithRawTablesAdded, destinationTables,
        String.format("streams did not match.\n source stream names: %s\n destination stream names: %s\n", sourceTables, destinationTables));

    for (final SchemaTableNamePair pair : sourceTables) {
      final List<JsonNode> sourceRecords = retrieveSourceRecords(source, pair.getFullyQualifiedTableName());
      assertRawDestinationContains(sourceRecords, pair);
    }
  }

  public Database getSourceDatabase() {
    return getDatabase(sourcePsql);
  }

  public Database getDestinationDatabase() {
    return getDatabase(destinationPsql);
  }

  public Database getDatabase(final PostgreSQLContainer db) {
    return new Database(DatabaseConnectionHelper.createDslContext(db, SQLDialect.POSTGRES));
  }

  public Set<SchemaTableNamePair> listAllTables(final Database database) throws SQLException {
    return database.query(
        context -> {
          final Result<Record> fetch =
              context.fetch(
                  "SELECT tablename, schemaname FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'");
          return fetch.stream()
              .map(record -> {
                final var schemaName = (String) record.get("schemaname");
                final var tableName = (String) record.get("tablename");
                return new SchemaTableNamePair(schemaName, tableName);
              })
              .collect(Collectors.toSet());
        });
  }

  public Set<SchemaTableNamePair> addAirbyteGeneratedTables(final boolean withScdTable, final Set<SchemaTableNamePair> sourceTables) {
    return sourceTables.stream().flatMap(x -> {
      final String cleanedNameStream = x.tableName.replace(".", "_");
      final List<SchemaTableNamePair> explodedStreamNames = new ArrayList<>(List.of(
          new SchemaTableNamePair(OUTPUT_NAMESPACE_PREFIX + x.schemaName,
              String.format("_airbyte_raw_%s%s", OUTPUT_STREAM_PREFIX, cleanedNameStream)),
          new SchemaTableNamePair(OUTPUT_NAMESPACE_PREFIX + x.schemaName, String.format("%s%s", OUTPUT_STREAM_PREFIX, cleanedNameStream))));
      if (withScdTable) {
        explodedStreamNames
            .add(new SchemaTableNamePair("_airbyte_" + OUTPUT_NAMESPACE_PREFIX + x.schemaName,
                String.format("%s%s_stg", OUTPUT_STREAM_PREFIX, cleanedNameStream)));
        explodedStreamNames
            .add(new SchemaTableNamePair(OUTPUT_NAMESPACE_PREFIX + x.schemaName, String.format("%s%s_scd", OUTPUT_STREAM_PREFIX, cleanedNameStream)));
      }
      return explodedStreamNames.stream();
    }).collect(Collectors.toSet());
  }

  public void assertRawDestinationContains(final List<JsonNode> sourceRecords, final SchemaTableNamePair pair) throws Exception {
    final Set<JsonNode> destinationRecords = new HashSet<>(retrieveRawDestinationRecords(pair));

    assertEquals(sourceRecords.size(), destinationRecords.size(),
        String.format("destination contains: %s record. source contains: %s, \nsource records %s \ndestination records: %s",
            destinationRecords.size(), sourceRecords.size(), sourceRecords, destinationRecords));

    for (final JsonNode sourceStreamRecord : sourceRecords) {
      assertTrue(destinationRecords.contains(sourceStreamRecord),
          String.format("destination does not contain record:\n %s \n destination contains:\n %s\n",
              sourceStreamRecord, destinationRecords));
    }
  }

  public void assertNormalizedDestinationContains(final List<JsonNode> sourceRecords) throws Exception {
    final Database destination = getDestinationDatabase();
    final String finalDestinationTable = String.format("%spublic.%s%s", OUTPUT_NAMESPACE_PREFIX, OUTPUT_STREAM_PREFIX, STREAM_NAME.replace(".", "_"));
    final List<JsonNode> destinationRecords = retrieveSourceRecords(destination, finalDestinationTable);

    assertEquals(sourceRecords.size(), destinationRecords.size(),
        String.format("destination contains: %s record. source contains: %s", sourceRecords.size(), destinationRecords.size()));

    for (final JsonNode sourceStreamRecord : sourceRecords) {
      assertTrue(
          destinationRecords.stream()
              .anyMatch(r -> r.get(COLUMN_NAME).asText().equals(sourceStreamRecord.get(COLUMN_NAME).asText())
                  && r.get(COLUMN_ID).asInt() == sourceStreamRecord.get(COLUMN_ID).asInt()),
          String.format("destination does not contain record:\n %s \n destination contains:\n %s\n", sourceStreamRecord, destinationRecords));
    }
  }

  public ConnectionRead createConnection(final String name,
                                         final UUID sourceId,
                                         final UUID destinationId,
                                         final List<UUID> operationIds,
                                         final AirbyteCatalog catalog,
                                         final ConnectionSchedule schedule)
      throws ApiException {
    final ConnectionRead connection = apiClient.getConnectionApi().createConnection(
        new ConnectionCreate()
            .status(ConnectionStatus.ACTIVE)
            .sourceId(sourceId)
            .destinationId(destinationId)
            .syncCatalog(catalog)
            .schedule(schedule)
            .operationIds(operationIds)
            .name(name)
            .namespaceDefinition(NamespaceDefinitionType.CUSTOMFORMAT)
            .namespaceFormat(OUTPUT_NAMESPACE)
            .prefix(OUTPUT_STREAM_PREFIX));
    connectionIds.add(connection.getConnectionId());
    return connection;
  }

  public ConnectionRead updateConnectionSchedule(final UUID connectionId, final ConnectionSchedule newSchedule) throws ApiException {
    final ConnectionRead connectionRead = apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    return apiClient.getConnectionApi().updateConnection(
        new ConnectionUpdate()
            .namespaceDefinition(connectionRead.getNamespaceDefinition())
            .namespaceFormat(connectionRead.getNamespaceFormat())
            .prefix(connectionRead.getPrefix())
            .connectionId(connectionId)
            .operationIds(connectionRead.getOperationIds())
            .status(connectionRead.getStatus())
            .syncCatalog(connectionRead.getSyncCatalog())
            .name(connectionRead.getName())
            .resourceRequirements(connectionRead.getResourceRequirements())
            .schedule(newSchedule) // only field being updated
    );
  }

  public DestinationRead createDestination() throws ApiException {
    return createDestination(
        "AccTestDestination-" + UUID.randomUUID(),
        workspaceId,
        getDestinationDefId(),
        getDestinationDbConfig());
  }

  public DestinationRead createDestination(final String name, final UUID workspaceId, final UUID destinationDefId, final JsonNode destinationConfig)
      throws ApiException {
    final DestinationRead destination =
        apiClient.getDestinationApi().createDestination(new DestinationCreate()
            .name(name)
            .connectionConfiguration(Jsons.jsonNode(destinationConfig))
            .workspaceId(workspaceId)
            .destinationDefinitionId(destinationDefId));
    destinationIds.add(destination.getDestinationId());
    return destination;
  }

  public OperationRead createOperation() throws ApiException {
    final OperatorConfiguration normalizationConfig = new OperatorConfiguration()
        .operatorType(OperatorType.NORMALIZATION).normalization(new OperatorNormalization().option(
            OperatorNormalization.OptionEnum.BASIC));

    final OperationCreate operationCreate = new OperationCreate()
        .workspaceId(workspaceId)
        .name("AccTestDestination-" + UUID.randomUUID()).operatorConfiguration(normalizationConfig);

    final OperationRead operation = apiClient.getOperationApi().createOperation(operationCreate);
    operationIds.add(operation.getOperationId());
    return operation;
  }

  public UUID getDestinationDefId() throws ApiException {
    return apiClient.getDestinationDefinitionApi().listDestinationDefinitions().getDestinationDefinitions()
        .stream()
        .filter(dr -> dr.getName().toLowerCase().contains("postgres"))
        .findFirst()
        .orElseThrow()
        .getDestinationDefinitionId();
  }

  public List<JsonNode> retrieveSourceRecords(final Database database, final String table) throws SQLException {
    return database.query(context -> context.fetch(String.format("SELECT * FROM %s;", table)))
        .stream()
        .map(Record::intoMap)
        .map(Jsons::jsonNode)
        .collect(Collectors.toList());
  }

  public List<JsonNode> retrieveDestinationRecords(final Database database, final String table) throws SQLException {
    return database.query(context -> context.fetch(String.format("SELECT * FROM %s;", table)))
        .stream()
        .map(Record::intoMap)
        .map(r -> r.get(COLUMN_NAME_DATA))
        .map(f -> (JSONB) f)
        .map(JSONB::data)
        .map(Jsons::deserialize)
        .map(Jsons::jsonNode)
        .collect(Collectors.toList());
  }

  public List<JsonNode> retrieveRawDestinationRecords(final SchemaTableNamePair pair) throws Exception {
    final Database destination = getDestinationDatabase();
    final Set<SchemaTableNamePair> namePairs = listAllTables(destination);

    final String rawStreamName = String.format("_airbyte_raw_%s%s", OUTPUT_STREAM_PREFIX, pair.tableName.replace(".", "_"));
    final SchemaTableNamePair rawTablePair = new SchemaTableNamePair(OUTPUT_NAMESPACE_PREFIX + pair.schemaName, rawStreamName);
    assertTrue(namePairs.contains(rawTablePair), "can't find a non-normalized version (raw) of " + rawTablePair.getFullyQualifiedTableName());

    return retrieveDestinationRecords(destination, rawTablePair.getFullyQualifiedTableName());
  }

  public JsonNode getSourceDbConfig() {
    return getDbConfig(sourcePsql, false, false);
  }

  public JsonNode getDestinationDbConfig() {
    return getDbConfig(destinationPsql, false, true);
  }

  public JsonNode getDestinationDbConfigWithHiddenPassword() {
    return getDbConfig(destinationPsql, true, true);
  }

  public JsonNode getDbConfig(final PostgreSQLContainer psql, final boolean hiddenPassword, final boolean withSchema) {
    try {
      final Map<Object, Object> dbConfig = localConfig(psql, hiddenPassword, withSchema);
      return Jsons.jsonNode(dbConfig);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public Map<Object, Object> localConfig(final PostgreSQLContainer psql, final boolean hiddenPassword, final boolean withSchema) {
    final Map<Object, Object> dbConfig = new HashMap<>();
    // don't use psql.getHost() directly since the ip we need differs depending on environment
    if (IS_MAC) {
      dbConfig.put("host", "host.docker.internal");
    } else {
      dbConfig.put("host", "localhost");
    }

    if (hiddenPassword) {
      dbConfig.put("password", "**********");
    } else {
      dbConfig.put("password", psql.getPassword());
    }

    dbConfig.put("port", psql.getFirstMappedPort());
    dbConfig.put("database", psql.getDatabaseName());
    dbConfig.put("username", psql.getUsername());
    dbConfig.put("ssl", false);

    if (withSchema) {
      dbConfig.put("schema", "public");
    }
    return dbConfig;
  }

  public SourceDefinitionRead createE2eSourceDefinition() throws ApiException {
    return apiClient.getSourceDefinitionApi().createSourceDefinition(new SourceDefinitionCreate()
        .name("E2E Test Source")
        .dockerRepository("airbyte/source-e2e-test")
        .dockerImageTag(SOURCE_E2E_TEST_CONNECTOR_VERSION)
        .documentationUrl(URI.create("https://example.com")));
  }

  public DestinationDefinitionRead createE2eDestinationDefinition() throws ApiException {
    return apiClient.getDestinationDefinitionApi().createDestinationDefinition(new DestinationDefinitionCreate()
        .name("E2E Test Destination")
        .dockerRepository("airbyte/destination-e2e-test")
        .dockerImageTag(DESTINATION_E2E_TEST_CONNECTOR_VERSION)
        .documentationUrl(URI.create("https://example.com")));
  }

  public SourceRead createPostgresSource() throws ApiException {
    return createSource(
        "acceptanceTestDb-" + UUID.randomUUID(),
        workspaceId,
        getPostgresSourceDefinitionId(),
        getSourceDbConfig());
  }

  public SourceRead createSource(final String name, final UUID workspaceId, final UUID sourceDefId, final JsonNode sourceConfig)
      throws ApiException {
    final SourceRead source = apiClient.getSourceApi().createSource(new SourceCreate()
        .name(name)
        .sourceDefinitionId(sourceDefId)
        .workspaceId(workspaceId)
        .connectionConfiguration(sourceConfig));
    sourceIds.add(source.getSourceId());
    return source;
  }

  public UUID getPostgresSourceDefinitionId() throws ApiException {
    return apiClient.getSourceDefinitionApi().listSourceDefinitions().getSourceDefinitions()
        .stream()
        .filter(sourceRead -> sourceRead.getName().equalsIgnoreCase("postgres"))
        .findFirst()
        .orElseThrow()
        .getSourceDefinitionId();
  }

  public void clearSourceDbData() throws SQLException {
    final Database database = getSourceDatabase();
    final Set<SchemaTableNamePair> pairs = listAllTables(database);
    for (final SchemaTableNamePair pair : pairs) {
      database.query(context -> context.execute(String.format("DROP TABLE %s.%s", pair.schemaName, pair.tableName)));
    }
  }

  public void deleteSource(final UUID sourceId) throws ApiException {
    apiClient.getSourceApi().deleteSource(new SourceIdRequestBody().sourceId(sourceId));
  }

  public void disableConnection(final UUID connectionId) throws ApiException {
    final ConnectionRead connection = apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    final ConnectionUpdate connectionUpdate =
        new ConnectionUpdate()
            .prefix(connection.getPrefix())
            .connectionId(connectionId)
            .operationIds(connection.getOperationIds())
            .status(ConnectionStatus.DEPRECATED)
            .schedule(connection.getSchedule())
            .syncCatalog(connection.getSyncCatalog());
    apiClient.getConnectionApi().updateConnection(connectionUpdate);
  }

  public void deleteDestination(final UUID destinationId) throws ApiException {
    apiClient.getDestinationApi().deleteDestination(new DestinationIdRequestBody().destinationId(destinationId));
  }

  public void deleteOperation(final UUID destinationId) throws ApiException {
    apiClient.getOperationApi().deleteOperation(new OperationIdRequestBody().operationId(destinationId));
  }

  public static void waitForSuccessfulJob(final JobsApi jobsApi, final JobRead originalJob) throws InterruptedException, ApiException {
    final JobRead job = waitWhileJobHasStatus(jobsApi, originalJob, Sets.newHashSet(JobStatus.PENDING, JobStatus.RUNNING));

    if (!JobStatus.SUCCEEDED.equals(job.getStatus())) {
      // If a job failed during testing, show us why.
      final JobIdRequestBody id = new JobIdRequestBody();
      id.setId(originalJob.getId());
      for (final AttemptInfoRead attemptInfo : jobsApi.getJobInfo(id).getAttempts()) {
        LOGGER.warn("Unsuccessful job attempt " + attemptInfo.getAttempt().getId()
            + " with status " + job.getStatus() + " produced log output as follows: " + attemptInfo.getLogs().getLogLines());
      }
    }
    assertEquals(JobStatus.SUCCEEDED, job.getStatus());
  }

  public static JobRead waitWhileJobHasStatus(final JobsApi jobsApi, final JobRead originalJob, final Set<JobStatus> jobStatuses)
      throws InterruptedException, ApiException {
    return waitWhileJobHasStatus(jobsApi, originalJob, jobStatuses, Duration.ofMinutes(6));
  }

  @SuppressWarnings("BusyWait")
  public static JobRead waitWhileJobHasStatus(final JobsApi jobsApi,
                                              final JobRead originalJob,
                                              final Set<JobStatus> jobStatuses,
                                              final Duration maxWaitTime)
      throws InterruptedException, ApiException {
    JobRead job = originalJob;

    final Instant waitStart = Instant.now();
    while (jobStatuses.contains(job.getStatus())) {
      if (Duration.between(waitStart, Instant.now()).compareTo(maxWaitTime) > 0) {
        LOGGER.info("Max wait time of {} has been reached. Stopping wait.", maxWaitTime);
        break;
      }
      sleep(1000);

      job = jobsApi.getJobInfo(new JobIdRequestBody().id(job.getId())).getJob();
      LOGGER.info("waiting: job id: {} config type: {} status: {}", job.getId(), job.getConfigType(), job.getStatus());
    }
    return job;
  }

  public enum Type {
    SOURCE,
    DESTINATION
  }

}
