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
import io.airbyte.api.client.model.generated.ConnectionScheduleData;
import io.airbyte.api.client.model.generated.ConnectionScheduleType;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.ConnectionStatus;
import io.airbyte.api.client.model.generated.ConnectionUpdate;
import io.airbyte.api.client.model.generated.CustomDestinationDefinitionCreate;
import io.airbyte.api.client.model.generated.CustomSourceDefinitionCreate;
import io.airbyte.api.client.model.generated.DestinationCreate;
import io.airbyte.api.client.model.generated.DestinationDefinitionCreate;
import io.airbyte.api.client.model.generated.DestinationDefinitionRead;
import io.airbyte.api.client.model.generated.DestinationDefinitionUpdate;
import io.airbyte.api.client.model.generated.DestinationIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationRead;
import io.airbyte.api.client.model.generated.DestinationSyncMode;
import io.airbyte.api.client.model.generated.Geography;
import io.airbyte.api.client.model.generated.JobConfigType;
import io.airbyte.api.client.model.generated.JobDebugInfoRead;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.api.client.model.generated.JobListRequestBody;
import io.airbyte.api.client.model.generated.JobRead;
import io.airbyte.api.client.model.generated.JobStatus;
import io.airbyte.api.client.model.generated.JobWithAttemptsRead;
import io.airbyte.api.client.model.generated.NamespaceDefinitionType;
import io.airbyte.api.client.model.generated.OperationCreate;
import io.airbyte.api.client.model.generated.OperationIdRequestBody;
import io.airbyte.api.client.model.generated.OperationRead;
import io.airbyte.api.client.model.generated.OperatorConfiguration;
import io.airbyte.api.client.model.generated.OperatorNormalization;
import io.airbyte.api.client.model.generated.OperatorType;
import io.airbyte.api.client.model.generated.SourceCreate;
import io.airbyte.api.client.model.generated.SourceDefinitionCreate;
import io.airbyte.api.client.model.generated.SourceDefinitionRead;
import io.airbyte.api.client.model.generated.SourceDefinitionUpdate;
import io.airbyte.api.client.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.client.model.generated.SourceIdRequestBody;
import io.airbyte.api.client.model.generated.SourceRead;
import io.airbyte.api.client.model.generated.SyncMode;
import io.airbyte.api.client.model.generated.WebBackendConnectionUpdate;
import io.airbyte.api.client.model.generated.WebBackendOperationCreateOrUpdate;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.TemporalWorkflowUtils;
import io.airbyte.commons.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.commons.temporal.scheduling.state.WorkflowState;
import io.airbyte.commons.util.MoreProperties;
import io.airbyte.db.Database;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.test.airbyte_test_container.AirbyteTestContainer;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.File;
import java.io.IOException;
import java.net.Inet4Address;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
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
import org.junit.jupiter.api.Assertions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

/**
 * This class contains containers used for acceptance tests. Some of those containers/states are
 * only used when the test are run without GKE. Specific environmental variables govern what types
 * of containers are run.
 * <p>
 * This class is put in a separate module to be easily pulled in as a dependency for Airbyte Cloud
 * Acceptance Tests.
 * <p>
 * Containers and states include:
 * <li>source postgres SQL</li>
 * <li>destination postgres SQL</li>
 * <li>{@link AirbyteTestContainer}</li>
 * <li>kubernetes client</li>
 * <li>lists of UUIDS representing IDs of sources, destinations, connections, and operations</li>
 */
public class AirbyteAcceptanceTestHarness {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteAcceptanceTestHarness.class);

  private static final String DOCKER_COMPOSE_FILE_NAME = "docker-compose.yaml";
  // assume env file is one directory level up from airbyte-tests.
  private final static File ENV_FILE = Path.of(System.getProperty("user.dir")).getParent().resolve(".env").toFile();

  private static final DockerImageName DESTINATION_POSTGRES_IMAGE_NAME = DockerImageName.parse("postgres:13-alpine");

  private static final DockerImageName SOURCE_POSTGRES_IMAGE_NAME = DockerImageName.parse("debezium/postgres:13-alpine")
      .asCompatibleSubstituteFor("postgres");

  private static final String SOURCE_E2E_TEST_CONNECTOR_VERSION = "0.1.2";
  private static final String DESTINATION_E2E_TEST_CONNECTOR_VERSION = "0.1.1";

  public static final String POSTGRES_SOURCE_LEGACY_CONNECTOR_VERSION = "0.4.26";

  private static final String OUTPUT_NAMESPACE_PREFIX = "output_namespace_";
  private static final String OUTPUT_NAMESPACE = OUTPUT_NAMESPACE_PREFIX + "${SOURCE_NAMESPACE}";
  private static final String OUTPUT_STREAM_PREFIX = "output_table_";
  private static final String TABLE_NAME = "id_and_name";
  public static final String STREAM_NAME = TABLE_NAME;
  public static final String COLUMN_ID = "id";
  public static final String COLUMN_NAME = "name";
  private static final String COLUMN_NAME_DATA = "_airbyte_data";
  private static final String SOURCE_USERNAME = "sourceusername";
  public static final String SOURCE_PASSWORD = "hunter2";
  public static final String PUBLIC_SCHEMA_NAME = "public";
  public static final String STAGING_SCHEMA_NAME = "staging";
  public static final String COOL_EMPLOYEES_TABLE_NAME = "cool_employees";
  public static final String AWESOME_PEOPLE_TABLE_NAME = "awesome_people";

  private static final String DEFAULT_POSTGRES_INIT_SQL_FILE = "postgres_init.sql";

  // Used for bypassing SSL modification for db configs
  private static final String IS_TEST = "is_test";

  private static boolean isKube;
  private static boolean isMinikube;
  private static boolean isGke;
  private static boolean isMac;
  private static boolean useExternalDeployment;

  /**
   * When the acceptance tests are run against a local instance of docker-compose or KUBE then these
   * test containers are used. When we run these tests in GKE, we spawn a source and destination
   * postgres database ane use them for testing.
   */
  private PostgreSQLContainer sourcePsql;
  private PostgreSQLContainer destinationPsql;
  private AirbyteTestContainer airbyteTestContainer;
  private AirbyteApiClient apiClient;
  private final UUID defaultWorkspaceId;
  private final String postgresSqlInitFile;

  private KubernetesClient kubernetesClient;

  private List<UUID> sourceIds;
  private List<UUID> connectionIds;
  private List<UUID> destinationIds;
  private List<UUID> operationIds;

  public PostgreSQLContainer getSourcePsql() {
    return sourcePsql;
  }

  public KubernetesClient getKubernetesClient() {
    return kubernetesClient;
  }

  public void removeConnection(final UUID connection) {
    connectionIds.remove(connection);
  }

  public void setApiClient(final AirbyteApiClient apiClient) {
    this.apiClient = apiClient;
  }

  public AirbyteAcceptanceTestHarness(final AirbyteApiClient apiClient, final UUID defaultWorkspaceId, final String postgresSqlInitFile)
      throws URISyntaxException, IOException, InterruptedException {
    // reads env vars to assign static variables
    assignEnvVars();
    this.apiClient = apiClient;
    this.defaultWorkspaceId = defaultWorkspaceId;
    this.postgresSqlInitFile = postgresSqlInitFile;

    if (isGke && !isKube) {
      throw new RuntimeException("KUBE Flag should also be enabled if GKE flag is enabled");
    }
    if (!isGke) {
      sourcePsql = new PostgreSQLContainer(SOURCE_POSTGRES_IMAGE_NAME)
          .withUsername(SOURCE_USERNAME)
          .withPassword(SOURCE_PASSWORD);
      sourcePsql.start();

      destinationPsql = new PostgreSQLContainer(DESTINATION_POSTGRES_IMAGE_NAME);
      destinationPsql.start();
    }

    if (isKube) {
      kubernetesClient = new DefaultKubernetesClient();
    }

    // by default use airbyte deployment governed by a test container.
    if (!useExternalDeployment) {
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
  }

  public AirbyteAcceptanceTestHarness(final AirbyteApiClient apiClient, final UUID defaultWorkspaceId)
      throws URISyntaxException, IOException, InterruptedException {
    this(apiClient, defaultWorkspaceId, DEFAULT_POSTGRES_INIT_SQL_FILE);
  }

  public void stopDbAndContainers() {
    if (!isGke) {
      sourcePsql.stop();
      destinationPsql.stop();
    }

    if (airbyteTestContainer != null) {
      airbyteTestContainer.stop();
    }
  }

  public void setup() throws SQLException, URISyntaxException, IOException {
    sourceIds = Lists.newArrayList();
    connectionIds = Lists.newArrayList();
    destinationIds = Lists.newArrayList();
    operationIds = Lists.newArrayList();

    if (isGke) {
      // seed database.
      final Database database = getSourceDatabase();
      final Path path = Path.of(MoreResources.readResourceAsFile(postgresSqlInitFile).toURI());
      final StringBuilder query = new StringBuilder();
      for (final String line : java.nio.file.Files.readAllLines(path, StandardCharsets.UTF_8)) {
        if (line != null && !line.isEmpty()) {
          query.append(line);
        }
      }
      database.query(context -> context.execute(query.toString()));
    } else {
      PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource(postgresSqlInitFile), sourcePsql);

      destinationPsql = new PostgreSQLContainer("postgres:13-alpine");
      destinationPsql.start();
    }
  }

  public void cleanup() {
    try {
      clearSourceDbData();
      clearDestinationDbData();

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
      if (!isGke) {
        destinationPsql.stop();
      }
    } catch (final Exception e) {
      LOGGER.error("Error tearing down test fixtures:", e);
    }
  }

  private void assignEnvVars() {
    isKube = System.getenv().containsKey("KUBE");
    isMinikube = System.getenv().containsKey("IS_MINIKUBE");
    isGke = System.getenv().containsKey("IS_GKE");
    isMac = System.getProperty("os.name").startsWith("Mac");
    useExternalDeployment =
        System.getenv("USE_EXTERNAL_DEPLOYMENT") != null &&
            System.getenv("USE_EXTERNAL_DEPLOYMENT").equalsIgnoreCase("true");
  }

  private WorkflowClient getWorkflowClient() {
    final TemporalUtils temporalUtils = new TemporalUtils(null, null, null, null, null, null, null);
    final WorkflowServiceStubs temporalService = temporalUtils.createTemporalService(
        TemporalWorkflowUtils.getAirbyteTemporalOptions("localhost:7233"),
        TemporalUtils.DEFAULT_NAMESPACE);
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

  public AirbyteCatalog discoverSourceSchemaWithoutCache(final UUID sourceId) throws ApiException {
    return apiClient.getSourceApi().discoverSchemaForSource(
        new SourceDiscoverSchemaRequestBody().sourceId(sourceId).disableCache(true)).getCatalog();
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
    if (isKube && isGke) {
      return GKEPostgresConfig.getSourceDatabase();
    }
    return getDatabase(sourcePsql);
  }

  public Database getDestinationDatabase() {
    if (isKube && isGke) {
      return GKEPostgresConfig.getDestinationDatabase();
    }
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

  private Set<SchemaTableNamePair> addAirbyteGeneratedTables(final boolean withScdTable, final Set<SchemaTableNamePair> sourceTables) {
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

  /**
   * Assert that the normalized destination matches the input records, only expecting a single id
   * column.
   *
   * @param sourceRecords
   * @throws Exception
   */
  public void assertNormalizedDestinationContainsIdColumn(final List<JsonNode> sourceRecords) throws Exception {
    final Database destination = getDestinationDatabase();
    final String finalDestinationTable = String.format("%spublic.%s%s", OUTPUT_NAMESPACE_PREFIX, OUTPUT_STREAM_PREFIX, STREAM_NAME.replace(".", "_"));
    final List<JsonNode> destinationRecords = retrieveSourceRecords(destination, finalDestinationTable);

    assertEquals(sourceRecords.size(), destinationRecords.size(),
        String.format("destination contains: %s record. source contains: %s", sourceRecords.size(), destinationRecords.size()));

    for (final JsonNode sourceStreamRecord : sourceRecords) {
      assertTrue(
          destinationRecords.stream()
              .anyMatch(r -> r.get(COLUMN_ID).asInt() == sourceStreamRecord.get(COLUMN_ID).asInt()),
          String.format("destination does not contain record:\n %s \n destination contains:\n %s\n", sourceStreamRecord, destinationRecords));
    }
  }

  public ConnectionRead createConnection(final String name,
                                         final UUID sourceId,
                                         final UUID destinationId,
                                         final List<UUID> operationIds,
                                         final AirbyteCatalog catalog,
                                         final ConnectionScheduleType scheduleType,
                                         final ConnectionScheduleData scheduleData)
      throws ApiException {
    return createConnectionWithGeography(name, sourceId, destinationId, operationIds, catalog, scheduleType, scheduleData, Geography.AUTO);
  }

  public ConnectionRead createConnectionWithGeography(final String name,
                                                      final UUID sourceId,
                                                      final UUID destinationId,
                                                      final List<UUID> operationIds,
                                                      final AirbyteCatalog catalog,
                                                      final ConnectionScheduleType scheduleType,
                                                      final ConnectionScheduleData scheduleData,
                                                      final Geography geography)
      throws ApiException {
    final ConnectionRead connection = apiClient.getConnectionApi().createConnection(
        new ConnectionCreate()
            .status(ConnectionStatus.ACTIVE)
            .sourceId(sourceId)
            .destinationId(destinationId)
            .syncCatalog(catalog)
            .scheduleType(scheduleType)
            .scheduleData(scheduleData)
            .operationIds(operationIds)
            .name(name)
            .namespaceDefinition(NamespaceDefinitionType.CUSTOMFORMAT)
            .namespaceFormat(OUTPUT_NAMESPACE)
            .prefix(OUTPUT_STREAM_PREFIX)
            .geography(geography));
    connectionIds.add(connection.getConnectionId());
    return connection;
  }

  public void updateConnectionSchedule(
                                       final UUID connectionId,
                                       final ConnectionScheduleType newScheduleType,
                                       final ConnectionScheduleData newScheduleData)
      throws ApiException {
    apiClient.getConnectionApi().updateConnection(
        new ConnectionUpdate()
            .connectionId(connectionId)
            .scheduleType(newScheduleType)
            .scheduleData(newScheduleData));
  }

  public void updateConnectionCatalog(final UUID connectionId, final AirbyteCatalog catalog) throws ApiException {
    apiClient.getConnectionApi().updateConnection(
        new ConnectionUpdate()
            .connectionId(connectionId)
            .syncCatalog(catalog));
  }

  public DestinationRead createPostgresDestination(final boolean isLegacy) throws ApiException {
    return createDestination(
        "AccTestDestination-" + UUID.randomUUID(),
        defaultWorkspaceId,
        getPostgresDestinationDefinitionId(),
        getDestinationDbConfig(isLegacy));
  }

  public DestinationRead createPostgresDestination() throws ApiException {
    return createPostgresDestination(false);
  }

  public DestinationRead createDestination(final String name,
                                           final UUID workspaceId,
                                           final UUID destinationDefId,
                                           final JsonNode destinationConfig)
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
        .workspaceId(defaultWorkspaceId)
        .name("AccTestDestination-" + UUID.randomUUID()).operatorConfiguration(normalizationConfig);

    final OperationRead operation = apiClient.getOperationApi().createOperation(operationCreate);
    operationIds.add(operation.getOperationId());
    return operation;
  }

  public List<JsonNode> retrieveSourceRecords(final Database database, final String table) throws SQLException {
    return database.query(context -> context.fetch(String.format("SELECT * FROM %s;", table)))
        .stream()
        .map(Record::intoMap)
        .map(rec -> {
          // The protocol requires converting numbers to strings. source-postgres does that internally,
          // but we're querying the DB directly, so we have to do it manually.
          final Map<String, Object> stringifiedNumbers = new HashMap<>();
          for (final String key : rec.keySet()) {
            Object o = rec.get(key);
            if (o instanceof Number) {
              o = o.toString();
            }
            stringifiedNumbers.put(key, o);
          }
          return stringifiedNumbers;
        })
        .map(Jsons::jsonNode)
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveDestinationRecords(final Database database, final String table) throws SQLException {
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

  public JsonNode getSourceDbConfig(final boolean isLegacy) {
    return getDbConfig(sourcePsql, false, false, isLegacy, Type.SOURCE);
  }

  public JsonNode getSourceDbConfig() {
    return getSourceDbConfig(false);
  }

  public JsonNode getDestinationDbConfig(final boolean isLegacy) {
    return getDbConfig(destinationPsql, false, true, isLegacy, Type.DESTINATION);
  }

  public JsonNode getDestinationDbConfig() {
    return getDestinationDbConfig(false);
  }

  public JsonNode getDestinationDbConfigWithHiddenPassword() {
    return getDbConfig(destinationPsql, true, true, false, Type.DESTINATION);
  }

  public JsonNode getDbConfig(final PostgreSQLContainer psql,
                              final boolean hiddenPassword,
                              final boolean withSchema,
                              final boolean isLegacy,
                              final Type connectorType) {
    try {
      final Map<Object, Object> dbConfig = (isKube && isGke) ? GKEPostgresConfig.dbConfig(connectorType, hiddenPassword, withSchema)
          : localConfig(psql, hiddenPassword, withSchema, isLegacy);
      return Jsons.jsonNode(dbConfig);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  private Map<Object, Object> localConfig(final PostgreSQLContainer psql,
                                          final boolean hiddenPassword,
                                          final boolean withSchema,
                                          final boolean isLegacy)
      throws UnknownHostException {
    final Map<Object, Object> dbConfig = new HashMap<>();
    // don't use psql.getHost() directly since the ip we need differs depending on environment
    if (isKube) {
      if (isMinikube) {
        // used with minikube driver=none instance
        dbConfig.put(JdbcUtils.HOST_KEY, Inet4Address.getLocalHost().getHostAddress());
      } else {
        // used on a single node with docker driver
        dbConfig.put(JdbcUtils.HOST_KEY, "host.docker.internal");
      }
    } else if (isMac) {
      dbConfig.put(JdbcUtils.HOST_KEY, "host.docker.internal");
    } else {
      dbConfig.put(JdbcUtils.HOST_KEY, "localhost");
    }

    if (hiddenPassword) {
      dbConfig.put(JdbcUtils.PASSWORD_KEY, "**********");
    } else {
      dbConfig.put(JdbcUtils.PASSWORD_KEY, psql.getPassword());
    }

    dbConfig.put(JdbcUtils.PORT_KEY, psql.getFirstMappedPort());
    dbConfig.put(JdbcUtils.DATABASE_KEY, psql.getDatabaseName());
    dbConfig.put(JdbcUtils.USERNAME_KEY, psql.getUsername());

    // bypasses the SSL modification for cloud acceptance tests. This use useful in cloud since it
    // enforces most databases to have SSL on, but the postgres containers we use for testing does not
    // allow SSL.
    if (!isLegacy) {
      dbConfig.put(IS_TEST, true);
    }
    dbConfig.put(JdbcUtils.SSL_KEY, false);

    if (withSchema) {
      dbConfig.put(JdbcUtils.SCHEMA_KEY, "public");
    }
    return dbConfig;
  }

  public SourceDefinitionRead createE2eSourceDefinition(final UUID workspaceId) throws ApiException {
    return apiClient.getSourceDefinitionApi().createCustomSourceDefinition(new CustomSourceDefinitionCreate()
        .workspaceId(workspaceId)
        .sourceDefinition(new SourceDefinitionCreate()
            .name("E2E Test Source")
            .dockerRepository("airbyte/source-e2e-test")
            .dockerImageTag(SOURCE_E2E_TEST_CONNECTOR_VERSION)
            .documentationUrl(URI.create("https://example.com"))));
  }

  public DestinationDefinitionRead createE2eDestinationDefinition(final UUID workspaceId) throws ApiException {
    return apiClient.getDestinationDefinitionApi().createCustomDestinationDefinition(new CustomDestinationDefinitionCreate()
        .workspaceId(workspaceId)
        .destinationDefinition(new DestinationDefinitionCreate()
            .name("E2E Test Destination")
            .dockerRepository("airbyte/destination-e2e-test")
            .dockerImageTag(DESTINATION_E2E_TEST_CONNECTOR_VERSION)
            .documentationUrl(URI.create("https://example.com"))));
  }

  public SourceRead createPostgresSource(final boolean isLegacy) throws ApiException {
    return createSource(
        "acceptanceTestDb-" + UUID.randomUUID(),
        defaultWorkspaceId,
        getPostgresSourceDefinitionId(),
        getSourceDbConfig(isLegacy));
  }

  public SourceRead createPostgresSource() throws ApiException {
    return createPostgresSource(false);
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
        .filter(sourceRead -> "postgres".equalsIgnoreCase(sourceRead.getName()))
        .findFirst()
        .orElseThrow()
        .getSourceDefinitionId();
  }

  public UUID getPostgresDestinationDefinitionId() throws ApiException {
    return apiClient.getDestinationDefinitionApi().listDestinationDefinitions().getDestinationDefinitions()
        .stream()
        .filter(destRead -> "postgres".equalsIgnoreCase(destRead.getName()))
        .findFirst()
        .orElseThrow()
        .getDestinationDefinitionId();
  }

  public void updateSourceDefinitionVersion(final UUID sourceDefinitionId, final String dockerImageTag) throws ApiException {
    apiClient.getSourceDefinitionApi().updateSourceDefinition(new SourceDefinitionUpdate()
        .sourceDefinitionId(sourceDefinitionId).dockerImageTag(dockerImageTag));
  }

  public void updateDestinationDefinitionVersion(final UUID destDefinitionId, final String dockerImageTag) throws ApiException {
    apiClient.getDestinationDefinitionApi().updateDestinationDefinition(new DestinationDefinitionUpdate()
        .destinationDefinitionId(destDefinitionId).dockerImageTag(dockerImageTag));
  }

  private void clearSourceDbData() throws SQLException {
    final Database database = getSourceDatabase();
    final Set<SchemaTableNamePair> pairs = listAllTables(database);
    for (final SchemaTableNamePair pair : pairs) {
      database.query(context -> context.execute(String.format("DROP TABLE %s.%s", pair.schemaName, pair.tableName)));
    }
  }

  private void clearDestinationDbData() throws SQLException {
    final Database database = getDestinationDatabase();
    final Set<SchemaTableNamePair> pairs = listAllTables(database);
    for (final SchemaTableNamePair pair : pairs) {
      database.query(context -> context.execute(String.format("DROP TABLE %s.%s CASCADE", pair.schemaName, pair.tableName)));
    }
  }

  private void disableConnection(final UUID connectionId) throws ApiException {
    final ConnectionUpdate connectionUpdate =
        new ConnectionUpdate().connectionId(connectionId).status(ConnectionStatus.DEPRECATED);
    apiClient.getConnectionApi().updateConnection(connectionUpdate);
  }

  private void deleteSource(final UUID sourceId) throws ApiException {
    apiClient.getSourceApi().deleteSource(new SourceIdRequestBody().sourceId(sourceId));
  }

  private void deleteDestination(final UUID destinationId) throws ApiException {
    apiClient.getDestinationApi().deleteDestination(new DestinationIdRequestBody().destinationId(destinationId));
  }

  private void deleteOperation(final UUID destinationId) throws ApiException {
    apiClient.getOperationApi().deleteOperation(new OperationIdRequestBody().operationId(destinationId));
  }

  public JobRead getMostRecentSyncJobId(final UUID connectionId) throws Exception {
    return apiClient.getJobsApi()
        .listJobsFor(new JobListRequestBody().configId(connectionId.toString()).configTypes(List.of(JobConfigType.SYNC)))
        .getJobs()
        .stream().findFirst().map(JobWithAttemptsRead::getJob).orElseThrow();
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
    Thread.sleep(200);
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

  @SuppressWarnings("BusyWait")
  public static void waitWhileJobIsRunning(final JobsApi jobsApi, final JobRead job, final Duration maxWaitTime)
      throws ApiException, InterruptedException {
    final Instant waitStart = Instant.now();
    JobDebugInfoRead jobDebugInfoRead = jobsApi.getJobDebugInfo(new JobIdRequestBody().id(job.getId()));
    LOGGER.info("workflow state: {}", jobDebugInfoRead.getWorkflowState());
    while (jobDebugInfoRead.getWorkflowState() != null && jobDebugInfoRead.getWorkflowState().getRunning()) {
      if (Duration.between(waitStart, Instant.now()).compareTo(maxWaitTime) > 0) {
        LOGGER.info("Max wait time of {} has been reached. Stopping wait.", maxWaitTime);
        break;
      }
      LOGGER.info("waiting: job id: {}, workflowState.isRunning is still true", job.getId());
      sleep(1000);
      jobDebugInfoRead = jobsApi.getJobDebugInfo(new JobIdRequestBody().id(job.getId()));
    }
  }

  @SuppressWarnings("BusyWait")
  public static ConnectionState waitForConnectionState(final AirbyteApiClient apiClient, final UUID connectionId)
      throws ApiException, InterruptedException {
    ConnectionState connectionState = apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId));
    int count = 0;
    while (count < 60 && (connectionState.getState() == null || connectionState.getState().isNull())) {
      LOGGER.info("fetching connection state. attempt: {}", count++);
      connectionState = apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId));
      sleep(1000);
    }
    return connectionState;
  }

  public JobRead waitUntilTheNextJobIsStarted(final UUID connectionId) throws Exception {
    final JobRead lastJob = getMostRecentSyncJobId(connectionId);
    if (lastJob.getStatus() != JobStatus.SUCCEEDED) {
      return lastJob;
    }

    JobRead mostRecentSyncJob = getMostRecentSyncJobId(connectionId);
    int count = 0;
    while (count < 60 && mostRecentSyncJob.getId().equals(lastJob.getId())) {
      Thread.sleep(Duration.ofSeconds(1).toMillis());
      mostRecentSyncJob = getMostRecentSyncJobId(connectionId);
      ++count;
    }
    final boolean exceeded60seconds = count >= 60;
    if (exceeded60seconds) {
      // Fail because taking more than 60seconds to start a job is not expected
      // Returning the current mostRecencSyncJob here could end up hiding some issues
      Assertions.fail("unable to find the next job within 60seconds");
    }

    return mostRecentSyncJob;
  }

  public enum Type {
    SOURCE,
    DESTINATION
  }

  public void assertDestinationDbEmpty(final boolean withScdTable) throws Exception {
    final Database source = getSourceDatabase();
    final Set<SchemaTableNamePair> sourceTables = listAllTables(source);
    final Set<SchemaTableNamePair> sourceTablesWithRawTablesAdded = addAirbyteGeneratedTables(withScdTable, sourceTables);
    final Database destination = getDestinationDatabase();
    final Set<SchemaTableNamePair> destinationTables = listAllTables(destination);
    assertEquals(sourceTablesWithRawTablesAdded, destinationTables,
        String.format("streams did not match.\n source stream names: %s\n destination stream names: %s\n", sourceTables, destinationTables));

    for (final SchemaTableNamePair pair : sourceTables) {
      final List<JsonNode> sourceRecords = retrieveRawDestinationRecords(pair);
      assertTrue(sourceRecords.isEmpty());
    }
  }

  public void setIncrementalAppendSyncMode(final AirbyteCatalog airbyteCatalog, final List<String> cursorField) {
    airbyteCatalog.getStreams().forEach(stream -> {
      stream.getConfig().syncMode(SyncMode.INCREMENTAL)
          .destinationSyncMode(DestinationSyncMode.APPEND)
          .cursorField(cursorField);
    });
  }

  public WebBackendConnectionUpdate getUpdateInput(final ConnectionRead connection, final AirbyteCatalog catalog, final OperationRead operation) {
    setIncrementalAppendSyncMode(catalog, List.of(COLUMN_ID));

    return new WebBackendConnectionUpdate()
        .connectionId(connection.getConnectionId())
        .name(connection.getName())
        .operations(List.of(new WebBackendOperationCreateOrUpdate()
            .name(operation.getName())
            .operationId(operation.getOperationId())
            .workspaceId(operation.getWorkspaceId())
            .operatorConfiguration(operation.getOperatorConfiguration())))
        .namespaceDefinition(connection.getNamespaceDefinition())
        .namespaceFormat(connection.getNamespaceFormat())
        .syncCatalog(catalog)
        .schedule(connection.getSchedule())
        .sourceCatalogId(connection.getSourceCatalogId())
        .status(connection.getStatus())
        .prefix(connection.getPrefix())
        .skipReset(false);
  }

}
