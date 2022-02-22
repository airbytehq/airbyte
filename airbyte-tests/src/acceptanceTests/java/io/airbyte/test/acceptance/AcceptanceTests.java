/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import static java.lang.Thread.sleep;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import com.google.common.io.Resources;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.JobsApi;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.model.AirbyteCatalog;
import io.airbyte.api.client.model.AttemptInfoRead;
import io.airbyte.api.client.model.ConnectionCreate;
import io.airbyte.api.client.model.ConnectionIdRequestBody;
import io.airbyte.api.client.model.ConnectionRead;
import io.airbyte.api.client.model.ConnectionSchedule;
import io.airbyte.api.client.model.ConnectionState;
import io.airbyte.api.client.model.ConnectionStatus;
import io.airbyte.api.client.model.ConnectionUpdate;
import io.airbyte.api.client.model.DestinationCreate;
import io.airbyte.api.client.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.client.model.DestinationDefinitionRead;
import io.airbyte.api.client.model.DestinationIdRequestBody;
import io.airbyte.api.client.model.DestinationRead;
import io.airbyte.api.client.model.DestinationSyncMode;
import io.airbyte.api.client.model.JobIdRequestBody;
import io.airbyte.api.client.model.JobInfoRead;
import io.airbyte.api.client.model.JobRead;
import io.airbyte.api.client.model.JobStatus;
import io.airbyte.api.client.model.NamespaceDefinitionType;
import io.airbyte.api.client.model.OperationCreate;
import io.airbyte.api.client.model.OperationIdRequestBody;
import io.airbyte.api.client.model.OperationRead;
import io.airbyte.api.client.model.OperatorConfiguration;
import io.airbyte.api.client.model.OperatorNormalization;
import io.airbyte.api.client.model.OperatorNormalization.OptionEnum;
import io.airbyte.api.client.model.OperatorType;
import io.airbyte.api.client.model.SourceCreate;
import io.airbyte.api.client.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.client.model.SourceDefinitionRead;
import io.airbyte.api.client.model.SourceIdRequestBody;
import io.airbyte.api.client.model.SourceRead;
import io.airbyte.api.client.model.SyncMode;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreProperties;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.test.airbyte_test_container.AirbyteTestContainer;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.File;
import java.io.IOException;
import java.net.Inet4Address;
import java.net.URISyntaxException;
import java.net.UnknownHostException;
import java.nio.charset.Charset;
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
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

@SuppressWarnings({"rawtypes", "ConstantConditions"})
// We order tests such that earlier tests test more basic behavior that is relied upon in later
// tests.
// e.g. We test that we can create a destination before we test whether we can sync data to it.
//
// Many of the tests here are disabled for Kubernetes. This is because they are already run
// as part of the Docker acceptance tests and there is little value re-running on Kubernetes,
// especially operations take much longer due to Kubernetes pod spin up times.
// We run a subset to sanity check basic Airbyte Kubernetes Sync features.
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class AcceptanceTests {

  private static final Logger LOGGER = LoggerFactory.getLogger(AcceptanceTests.class);

  private static final String DOCKER_COMPOSE_FILE_NAME = "docker-compose.yaml";
  // assume env file is one directory level up from airbyte-tests.
  private final static File ENV_FILE = Path.of(System.getProperty("user.dir")).getParent().resolve(".env").toFile();

  private static final String SOURCE_E2E_TEST_CONNECTOR_VERSION = "0.1.1";
  private static final String DESTINATION_E2E_TEST_CONNECTOR_VERSION = "0.1.1";

  private static final Charset UTF8 = StandardCharsets.UTF_8;
  private static final boolean IS_KUBE = System.getenv().containsKey("KUBE");
  private static final boolean IS_CONTAINER_ORCHESTRATOR = System.getenv().containsKey("CONTAINER_ORCHESTRATOR");
  private static final boolean IS_MINIKUBE = System.getenv().containsKey("IS_MINIKUBE");
  private static final boolean IS_GKE = System.getenv().containsKey("IS_GKE");
  private static final boolean USE_EXTERNAL_DEPLOYMENT =
      System.getenv("USE_EXTERNAL_DEPLOYMENT") != null && System.getenv("USE_EXTERNAL_DEPLOYMENT").equalsIgnoreCase("true");

  private static final String OUTPUT_NAMESPACE_PREFIX = "output_namespace_";
  private static final String OUTPUT_NAMESPACE = OUTPUT_NAMESPACE_PREFIX + "${SOURCE_NAMESPACE}";
  private static final String OUTPUT_STREAM_PREFIX = "output_table_";
  private static final String TABLE_NAME = "id_and_name";
  private static final String STREAM_NAME = TABLE_NAME;
  private static final String COLUMN_ID = "id";
  private static final String COLUMN_NAME = "name";
  private static final String COLUMN_NAME_DATA = "_airbyte_data";
  private static final String SOURCE_USERNAME = "sourceusername";
  private static final String SOURCE_PASSWORD = "hunter2";

  /**
   * When the acceptance tests are run against a local instance of docker-compose or KUBE then these
   * test containers are used. When we run these tests in GKE, we spawn a source and destination
   * postgres database ane use them for testing.
   */
  private static PostgreSQLContainer sourcePsql;
  private static PostgreSQLContainer destinationPsql;
  private static AirbyteTestContainer airbyteTestContainer;

  private AirbyteApiClient apiClient;

  private UUID workspaceId;
  private List<UUID> sourceIds;
  private List<UUID> connectionIds;
  private List<UUID> destinationIds;
  private List<UUID> operationIds;

  private static FeatureFlags featureFlags;

  private static KubernetesClient kubernetesClient = null;

  @SuppressWarnings("UnstableApiUsage")
  @BeforeAll
  public static void init() throws URISyntaxException, IOException, InterruptedException {
    System.out.println("in init");
    if (IS_GKE && !IS_KUBE) {
      throw new RuntimeException("KUBE Flag should also be enabled if GKE flag is enabled");
    }
    if (!IS_GKE) {
      sourcePsql = new PostgreSQLContainer("postgres:13-alpine")
          .withUsername(SOURCE_USERNAME)
          .withPassword(SOURCE_PASSWORD);
      sourcePsql.start();
    }

    if (IS_KUBE) {
      kubernetesClient = new DefaultKubernetesClient();
    }

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

    featureFlags = new EnvVariableFeatureFlags();
  }

  @AfterAll
  public static void end() {
    if (!IS_GKE) {
      sourcePsql.stop();
    }
    if (airbyteTestContainer != null) {
      airbyteTestContainer.stop();
    }
  }

  @BeforeEach
  public void setup() throws ApiException, URISyntaxException, SQLException, IOException {
    apiClient = new AirbyteApiClient(
        new ApiClient().setScheme("http")
            .setHost("localhost")
            .setPort(8001)
            .setBasePath("/api"));

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
    if (!IS_GKE) {
      destinationPsql = new PostgreSQLContainer("postgres:13-alpine");
      destinationPsql.start();
    }

    sourceIds = Lists.newArrayList();
    connectionIds = Lists.newArrayList();
    destinationIds = Lists.newArrayList();
    operationIds = Lists.newArrayList();

    // seed database.
    if (IS_GKE) {
      final Database database = getSourceDatabase();
      final Path path = Path.of(MoreResources.readResourceAsFile("postgres_init.sql").toURI());
      final StringBuilder query = new StringBuilder();
      for (final String line : java.nio.file.Files.readAllLines(path, UTF8)) {
        if (line != null && !line.isEmpty()) {
          query.append(line);
        }
      }
      database.query(context -> context.execute(query.toString()));
    } else {
      PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("postgres_init.sql"), sourcePsql);
    }
  }

  @AfterEach
  public void tearDown() throws ApiException, SQLException {
    clearSourceDbData();
    clearDestinationDbData();
    if (!IS_GKE) {
      destinationPsql.stop();
    }

    for (final UUID sourceId : sourceIds) {
      deleteSource(sourceId);
    }

    for (final UUID connectionId : connectionIds) {
      disableConnection(connectionId);
    }

    for (final UUID destinationId : destinationIds) {
      deleteDestination(destinationId);
    }
    for (final UUID operationId : operationIds) {
      deleteOperation(operationId);
    }
  }

  // todo: test with both types of workers getting scaled down, just one of each
  @ParameterizedTest
  @Order(-1800000)
  @EnabledIfEnvironmentVariable(named = "CONTAINER_ORCHESTRATOR",
                                matches = "true")
  @ValueSource(strings = {"KILL_BOTH_SAME_TIME", "KILL_SYNC_FIRST", "KILL_NON_SYNC_FIRST", "KILL_ONLY_SYNC", "KILL_ONLY_NON_SYNC"})
  public void testDowntimeDuringSync(String input) throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = createPostgresSource().getSourceId();
    final UUID destinationId = createDestination().getDestinationId();
    final UUID operationId = createOperation().getOperationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

    // Avoid race condition with the new scheduler
    if (featureFlags.usesNewScheduler()) {
      waitForTemporalWorkflow(connectionId);
    }

    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // todo: ideally this waits a couple seconds after the orchestrator pod starts
    Thread.sleep(10000);

    switch (input) {
      case "KILL_BOTH_SAME_TIME" -> {
        LOGGER.info("Scaling down both workers at roughly the same time...");
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(0);
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(0, true);

        LOGGER.info("Scaling up both workers...");
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(1);
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(1);
      }
      case "KILL_SYNC_FIRST" -> {
        LOGGER.info("Scaling down sync worker first...");
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(0, true);
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(0, true);

        LOGGER.info("Scaling up both workers...");
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(1);
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(1);
      }
      case "KILL_NON_SYNC_FIRST" -> {
        LOGGER.info("Scaling down non-sync worker first...");
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(0, true);
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(0, true);

        LOGGER.info("Scaling up both workers...");
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(1);
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(1);
      }
      case "KILL_ONLY_SYNC" -> {
        LOGGER.info("Scaling down only sync worker...");
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(0, true);

        LOGGER.info("Scaling up sync worker...");
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(1);
      }
      case "KILL_ONLY_NON_SYNC" -> {
        LOGGER.info("Scaling down only non-sync worker...");
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(0, true);

        LOGGER.info("Scaling up non-sync worker...");
        kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(1);
      }
    }

    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead.getJob());
    assertSourceAndDestinationDbInSync(false);

    final long numAttempts = apiClient.getJobsApi()
        .getJobInfo(new JobIdRequestBody().id(connectionSyncRead.getJob().getId()))
        .getAttempts()
        .size();

    // it should be able to accomplish the resume without an additional attempt!
    assertEquals(1, numAttempts);
  }

  private AirbyteCatalog discoverSourceSchema(final UUID sourceId) throws ApiException {
    return apiClient.getSourceApi().discoverSchemaForSource(new SourceIdRequestBody().sourceId(sourceId)).getCatalog();
  }

  private void assertSourceAndDestinationDbInSync(final boolean withScdTable) throws Exception {
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

  private Database getSourceDatabase() {
    if (IS_KUBE && IS_GKE) {
      return GKEPostgresConfig.getSourceDatabase();
    }
    return getDatabase(sourcePsql);
  }

  private Database getDestinationDatabase() {
    if (IS_KUBE && IS_GKE) {
      return GKEPostgresConfig.getDestinationDatabase();
    }
    return getDatabase(destinationPsql);
  }

  private Database getDatabase(final PostgreSQLContainer db) {
    return Databases.createPostgresDatabase(db.getUsername(), db.getPassword(), db.getJdbcUrl());
  }

  private Set<SchemaTableNamePair> listAllTables(final Database database) throws SQLException {
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

  private void assertRawDestinationContains(final List<JsonNode> sourceRecords, final SchemaTableNamePair pair) throws Exception {
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

  private void assertNormalizedDestinationContains(final List<JsonNode> sourceRecords) throws Exception {
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

  private ConnectionRead createConnection(final String name,
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

  private DestinationRead createDestination() throws ApiException {
    return createDestination(
        "AccTestDestination-" + UUID.randomUUID(),
        workspaceId,
        getDestinationDefId(),
        getDestinationDbConfig());
  }

  private DestinationRead createDestination(final String name, final UUID workspaceId, final UUID destinationDefId, final JsonNode destinationConfig)
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

  private OperationRead createOperation() throws ApiException {
    final OperatorConfiguration normalizationConfig = new OperatorConfiguration()
        .operatorType(OperatorType.NORMALIZATION).normalization(new OperatorNormalization().option(
            OptionEnum.BASIC));

    final OperationCreate operationCreate = new OperationCreate()
        .workspaceId(workspaceId)
        .name("AccTestDestination-" + UUID.randomUUID()).operatorConfiguration(normalizationConfig);

    final OperationRead operation = apiClient.getOperationApi().createOperation(operationCreate);
    operationIds.add(operation.getOperationId());
    return operation;
  }

  private UUID getDestinationDefId() throws ApiException {
    return apiClient.getDestinationDefinitionApi().listDestinationDefinitions().getDestinationDefinitions()
        .stream()
        .filter(dr -> dr.getName().toLowerCase().contains("postgres"))
        .findFirst()
        .orElseThrow()
        .getDestinationDefinitionId();
  }

  private List<JsonNode> retrieveSourceRecords(final Database database, final String table) throws SQLException {
    return database.query(context -> context.fetch(String.format("SELECT * FROM %s;", table)))
        .stream()
        .map(Record::intoMap)
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

  private List<JsonNode> retrieveRawDestinationRecords(final SchemaTableNamePair pair) throws Exception {
    final Database destination = getDestinationDatabase();
    final Set<SchemaTableNamePair> namePairs = listAllTables(destination);

    final String rawStreamName = String.format("_airbyte_raw_%s%s", OUTPUT_STREAM_PREFIX, pair.tableName.replace(".", "_"));
    final SchemaTableNamePair rawTablePair = new SchemaTableNamePair(OUTPUT_NAMESPACE_PREFIX + pair.schemaName, rawStreamName);
    assertTrue(namePairs.contains(rawTablePair), "can't find a non-normalized version (raw) of " + rawTablePair.getFullyQualifiedTableName());

    return retrieveDestinationRecords(destination, rawTablePair.getFullyQualifiedTableName());
  }

  private JsonNode getSourceDbConfig() {
    return getDbConfig(sourcePsql, false, false, Type.SOURCE);
  }

  private JsonNode getDestinationDbConfig() {
    return getDbConfig(destinationPsql, false, true, Type.DESTINATION);
  }

  private JsonNode getDestinationDbConfigWithHiddenPassword() {
    return getDbConfig(destinationPsql, true, true, Type.DESTINATION);
  }

  private JsonNode getDbConfig(final PostgreSQLContainer psql, final boolean hiddenPassword, final boolean withSchema, final Type connectorType) {
    try {
      final Map<Object, Object> dbConfig = (IS_KUBE && IS_GKE) ? GKEPostgresConfig.dbConfig(connectorType, hiddenPassword, withSchema)
          : localConfig(psql, hiddenPassword, withSchema);
      return Jsons.jsonNode(dbConfig);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  private Map<Object, Object> localConfig(final PostgreSQLContainer psql, final boolean hiddenPassword, final boolean withSchema)
      throws UnknownHostException {
    final Map<Object, Object> dbConfig = new HashMap<>();
    // don't use psql.getHost() directly since the ip we need differs depending on environment
    if (IS_KUBE) {
      if (IS_MINIKUBE) {
        // used with minikube driver=none instance
        dbConfig.put("host", Inet4Address.getLocalHost().getHostAddress());
      } else {
        // used on a single node with docker driver
        dbConfig.put("host", "host.docker.internal");
      }
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

  private SourceRead createPostgresSource() throws ApiException {
    return createSource(
        "acceptanceTestDb-" + UUID.randomUUID(),
        workspaceId,
        getPostgresSourceDefinitionId(),
        getSourceDbConfig());
  }

  private SourceRead createSource(final String name, final UUID workspaceId, final UUID sourceDefId, final JsonNode sourceConfig)
      throws ApiException {
    final SourceRead source = apiClient.getSourceApi().createSource(new SourceCreate()
        .name(name)
        .sourceDefinitionId(sourceDefId)
        .workspaceId(workspaceId)
        .connectionConfiguration(sourceConfig));
    sourceIds.add(source.getSourceId());
    return source;
  }

  private UUID getPostgresSourceDefinitionId() throws ApiException {
    return apiClient.getSourceDefinitionApi().listSourceDefinitions().getSourceDefinitions()
        .stream()
        .filter(sourceRead -> sourceRead.getName().equalsIgnoreCase("postgres"))
        .findFirst()
        .orElseThrow()
        .getSourceDefinitionId();
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

  private void deleteSource(final UUID sourceId) throws ApiException {
    apiClient.getSourceApi().deleteSource(new SourceIdRequestBody().sourceId(sourceId));
  }

  private void disableConnection(final UUID connectionId) throws ApiException {
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

  private void deleteDestination(final UUID destinationId) throws ApiException {
    apiClient.getDestinationApi().deleteDestination(new DestinationIdRequestBody().destinationId(destinationId));
  }

  private void deleteOperation(final UUID destinationId) throws ApiException {
    apiClient.getOperationApi().deleteOperation(new OperationIdRequestBody().operationId(destinationId));
  }

  private static void waitForSuccessfulJob(final JobsApi jobsApi, final JobRead originalJob) throws InterruptedException, ApiException {
    final JobRead job = waitForJob(jobsApi, originalJob, Sets.newHashSet(JobStatus.PENDING, JobStatus.RUNNING));

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

  private static JobRead waitForJob(final JobsApi jobsApi, final JobRead originalJob, final Set<JobStatus> jobStatuses)
      throws InterruptedException, ApiException {
    return waitForJob(jobsApi, originalJob, jobStatuses, Duration.ofMinutes(6));
  }

  @SuppressWarnings("BusyWait")
  private static JobRead waitForJob(final JobsApi jobsApi, final JobRead originalJob, final Set<JobStatus> jobStatuses, final Duration maxWaitTime)
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
  private static ConnectionState waitForConnectionState(final AirbyteApiClient apiClient, final UUID connectionId)
      throws ApiException, InterruptedException {
    ConnectionState connectionState = apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId));
    int count = 0;
    while (count < 60 && (connectionState.getState() == null || connectionState.getState().isNull())) {
      LOGGER.info("fetching connection state. attempt: {}", count++);
      connectionState = apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId));
      sleep(1000);
    }
    return connectionState;
  }

  public enum Type {
    SOURCE,
    DESTINATION
  }

  private static void waitForTemporalWorkflow(final UUID connectionId) {
    /*
     * do { try { Thread.sleep(1000); } catch (InterruptedException e) { throw new RuntimeException(e);
     * } } while
     * (temporalClient.isWorkflowRunning(temporalClient.getConnectionManagerName(connectionId)));
     */
    try {
      Thread.sleep(10 * 1000);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

}
