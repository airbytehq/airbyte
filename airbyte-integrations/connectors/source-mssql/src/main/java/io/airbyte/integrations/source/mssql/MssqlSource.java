/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.integrations.debezium.AirbyteDebeziumHandler.isAnyStreamIncrementalSyncMode;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_UPDATED_AT;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifier;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.logStreamSyncStatus;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.queryTable;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbReadUtil.convertNameNamespacePairFromV0;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbReadUtil.identifyStreamsForCursorBased;
import static io.airbyte.integrations.source.mssql.MssqlQueryUtils.getCursorBasedSyncStatusForStreams;
import static io.airbyte.integrations.source.mssql.MssqlQueryUtils.getTableSizeInfoForStreams;
import static io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.initPairToOrderedColumnInfoMap;
import static io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.streamsForInitialOrderedColumnLoad;
import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.cdk.db.util.SSLCertificateUtils;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedSource;
import io.airbyte.cdk.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.cdk.integrations.debezium.CdcStateHandler;
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.cdk.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumRecordIterator;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumRecordPublisher;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumShutdownProcedure;
import io.airbyte.cdk.integrations.debezium.internals.RelationalDbDebeziumEventConverter;
import io.airbyte.cdk.integrations.debezium.internals.RelationalDbDebeziumPropertiesManager;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.models.CursorBasedStatus;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.source.mssql.cursor_based.MssqlCursorBasedStateManager;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadHandler;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadStreamStateManager;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.CursorBasedStreams;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.InitialLoadStreams;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.connector.sqlserver.Lsn;
import io.debezium.engine.ChangeEvent;
import java.io.IOException;
import java.net.URI;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.CertificateException;
import java.sql.Connection;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlSource.class);
  public static final String DESCRIBE_TABLE_QUERY =
      """
      sp_columns "%s"
      """;
  public static final String NULL_CURSOR_VALUE_WITH_SCHEMA_QUERY =
      """
        SELECT CASE WHEN (SELECT TOP 1 1 FROM "%s"."%s" WHERE "%s" IS NULL)=1 then 1 else 0 end as %s
      """;
  public static final String DRIVER_CLASS = DatabaseDriver.MSSQLSERVER.getDriverClassName();
  public static final String MSSQL_CDC_OFFSET = "mssql_cdc_offset";
  public static final String MSSQL_DB_HISTORY = "mssql_db_history";
  public static final String IS_COMPRESSED = "is_compressed";
  public static final String CDC_LSN = "_ab_cdc_lsn";
  public static final String CDC_EVENT_SERIAL_NO = "_ab_cdc_event_serial_no";
  public static final String HIERARCHYID = "hierarchyid";
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;
  public static final String CDC_DEFAULT_CURSOR = "_ab_cdc_cursor";
  public static final String TUNNEL_METHOD = "tunnel_method";
  public static final String NO_TUNNEL = "NO_TUNNEL";
  public static final String SSL_METHOD = "ssl_method";
  public static final String SSL_METHOD_UNENCRYPTED = "unencrypted";

  public static final String JDBC_DELIMITER = ";";
  private List<String> schemas;

  public static Source sshWrappedSource(final MssqlSource source) {
    return new SshWrappedSource(source, JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public MssqlSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new MssqlSourceOperations());
  }

  @Override
  protected AirbyteStateType getSupportedStateType(final JsonNode config) {
    return MssqlCdcHelper.isCdc(config) ? AirbyteStateType.GLOBAL : AirbyteStateType.STREAM;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    // #15808 Disallow connecting to db with disable, prefer or allow SSL mode when connecting directly
    // and not over SSH tunnel
    if (cloudDeploymentMode()) {
      if (config.has(TUNNEL_METHOD)
          && config.get(TUNNEL_METHOD).has(TUNNEL_METHOD)
          && config.get(TUNNEL_METHOD).get(TUNNEL_METHOD).asText().equals(NO_TUNNEL)) {
        // If no SSH tunnel.
        if (config.has(SSL_METHOD) && config.get(SSL_METHOD).has(SSL_METHOD) &&
            SSL_METHOD_UNENCRYPTED.equalsIgnoreCase(config.get(SSL_METHOD).get(SSL_METHOD).asText())) {
          // Fail in case SSL method is unencrypted.
          return new AirbyteConnectionStatus()
              .withStatus(AirbyteConnectionStatus.Status.FAILED)
              .withMessage("Unsecured connection not allowed. " +
                  "If no SSH Tunnel set up, please use one of the following SSL methods: " +
                  "encrypted_trust_server_certificate, encrypted_verify_certificate.");
        }
      }
    }
    return super.check(config);
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableFullRefresh(final JdbcDatabase database,
                                                               final List<String> columnNames,
                                                               final String schemaName,
                                                               final String tableName,
                                                               final SyncMode syncMode,
                                                               final Optional<String> cursorField) {
    LOGGER.info("Queueing query for table: {}", tableName);
    // This corresponds to the initial sync for in INCREMENTAL_MODE. The ordering of the records matters
    // as intermediate state messages are emitted.
    if (syncMode.equals(SyncMode.INCREMENTAL)) {
      final String quotedCursorField = enquoteIdentifier(cursorField.get(), getQuoteString());
      final String newIdentifiers = getWrappedColumnNames(database, null, columnNames, schemaName, tableName);
      final String preparedSqlQuery =
          String.format("SELECT %s FROM %s ORDER BY %s ASC", newIdentifiers,
              getFullyQualifiedTableNameWithQuoting(schemaName, tableName, getQuoteString()), quotedCursorField);
      LOGGER.info("Prepared SQL query for TableFullRefresh is: " + preparedSqlQuery);
      return queryTable(database, preparedSqlQuery, tableName, schemaName);
    } else {
      // If we are in FULL_REFRESH mode, state messages are never emitted, so we don't care about ordering
      // of the records.
      final String newIdentifiers = getWrappedColumnNames(database, null, columnNames, schemaName, tableName);
      final String preparedSqlQuery =
          String.format("SELECT %s FROM %s", newIdentifiers, getFullyQualifiedTableNameWithQuoting(schemaName, tableName, getQuoteString()));

      LOGGER.info("Prepared SQL query for TableFullRefresh is: " + preparedSqlQuery);
      return queryTable(database, preparedSqlQuery, tableName, schemaName);
    }
  }

  /**
   * See {@link MssqlQueryUtils#getWrappedColumnNames}
   */
  @Override
  protected String getWrappedColumnNames(final JdbcDatabase database,
                                         final Connection connection,
                                         final List<String> columnNames,
                                         final String schemaName,
                                         final String tableName) {
    return MssqlQueryUtils.getWrappedColumnNames(database, quoteString, columnNames, schemaName, tableName);
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode mssqlConfig) {
    final List<String> additionalParameters = new ArrayList<>();

    final StringBuilder jdbcUrl = new StringBuilder(
        String.format("jdbc:sqlserver://%s:%s;databaseName=%s;",
            mssqlConfig.get(JdbcUtils.HOST_KEY).asText(),
            mssqlConfig.get(JdbcUtils.PORT_KEY).asText(),
            mssqlConfig.get(JdbcUtils.DATABASE_KEY).asText()));

    if (mssqlConfig.has("schemas") && mssqlConfig.get("schemas").isArray()) {
      schemas = new ArrayList<>();
      for (final JsonNode schema : mssqlConfig.get("schemas")) {
        schemas.add(schema.asText());
      }
    }

    if (mssqlConfig.has("ssl_method")) {
      readSsl(mssqlConfig, additionalParameters);
    } else {
      additionalParameters.add("trustServerCertificate=true");
    }

    if (!additionalParameters.isEmpty()) {
      jdbcUrl.append(String.join(";", additionalParameters));
    }

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, mssqlConfig.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.PASSWORD_KEY, mssqlConfig.get(JdbcUtils.PASSWORD_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString());

    if (mssqlConfig.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.CONNECTION_PROPERTIES_KEY, mssqlConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY));
    }

    final Map<String, String> additionalParams = new HashMap<>();
    additionalParameters.forEach(param -> {
      final int i = param.indexOf('=');
      additionalParams.put(param.substring(0, i), param.substring(i + 1));
    });

    configBuilder.putAll(additionalParams);

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "INFORMATION_SCHEMA",
        "sys",
        "spt_fallback_db",
        "spt_monitor",
        "spt_values",
        "spt_fallback_usg",
        "MSreplication_options",
        "spt_fallback_dev",
        "cdc"); // is this actually ok? what if the user wants cdc schema for some reason?
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    final AirbyteCatalog catalog = super.discover(config);

    if (MssqlCdcHelper.isCdc(config)) {
      final List<AirbyteStream> streams = catalog.getStreams().stream()
          .map(MssqlSource::overrideSyncModes)
          .map(MssqlSource::removeIncrementalWithoutPk)
          .map(MssqlSource::setIncrementalToSourceDefined)
          .map(MssqlSource::setDefaultCursorFieldForCdc)
          .map(MssqlSource::addCdcMetadataColumns)
          .collect(toList());

      catalog.setStreams(streams);
    }

    return catalog;
  }

  @Override
  public List<TableInfo<CommonField<JDBCType>>> discoverInternal(final JdbcDatabase database) throws Exception {
    final List<TableInfo<CommonField<JDBCType>>> internals = super.discoverInternal(database);
    if (schemas != null && !schemas.isEmpty()) {
      // process explicitly filtered (from UI) schemas
      final List<TableInfo<CommonField<JDBCType>>> resultInternals = internals
          .stream()
          .filter(this::isTableInRequestedSchema)
          .toList();
      for (final TableInfo<CommonField<JDBCType>> info : resultInternals) {
        LOGGER.debug("Found table (schema: {}): {}", info.getNameSpace(), info.getName());
      }
      return resultInternals;
    } else {
      LOGGER.info("No schemas explicitly set on UI to process, so will process all of existing schemas in DB");
      return internals;
    }
  }

  @Override
  protected boolean verifyCursorColumnValues(final JdbcDatabase database, final String schema, final String tableName, final String columnName)
      throws SQLException {

    boolean nullValExist = false;
    final String resultColName = "nullValue";
    final String descQuery = String.format(DESCRIBE_TABLE_QUERY, tableName);
    final Optional<JsonNode> field = database.bufferedResultSetQuery(conn -> conn.createStatement()
        .executeQuery(descQuery),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet))
        .stream()
        .peek(x -> LOGGER.info("MsSQL Table Structure {}, {}, {}", x.toString(), schema, tableName))
        .filter(x -> x.get("TABLE_OWNER") != null)
        .filter(x -> x.get("COLUMN_NAME") != null)
        .filter(x -> x.get("TABLE_OWNER").asText().equals(schema))
        .filter(x -> x.get("COLUMN_NAME").asText().equalsIgnoreCase(columnName))
        .findFirst();
    if (field.isPresent()) {
      final JsonNode jsonNode = field.get();
      final JsonNode isNullable = jsonNode.get("IS_NULLABLE");
      if (isNullable != null) {
        if (isNullable.asText().equalsIgnoreCase("YES")) {
          final String query = String.format(NULL_CURSOR_VALUE_WITH_SCHEMA_QUERY,
              schema, tableName, columnName, resultColName);

          LOGGER.debug("null value query: {}", query);
          final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.createStatement().executeQuery(query),
              resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
          Preconditions.checkState(jsonNodes.size() == 1);
          nullValExist = jsonNodes.get(0).get(resultColName).booleanValue();
          LOGGER.info("null cursor value for MsSQL source : {}, shema {} , tableName {}, columnName {} ", nullValExist, schema, tableName,
              columnName);
        }
      }
    }
    // return !nullValExist;
    // will enable after we have sent comms to users this affects
    return true;
  }

  private boolean isTableInRequestedSchema(final TableInfo<CommonField<JDBCType>> tableInfo) {
    return schemas
        .stream()
        .anyMatch(schema -> schema.equals(tableInfo.getNameSpace()));
  }

  @Override
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(final JsonNode config)
      throws Exception {
    final List<CheckedConsumer<JdbcDatabase, Exception>> checkOperations = new ArrayList<>(
        super.getCheckOperations(config));

    if (MssqlCdcHelper.isCdc(config)) {
      checkOperations.add(database -> assertCdcEnabledInDb(config, database));
      checkOperations.add(database -> assertCdcSchemaQueryable(config, database));
      checkOperations.add(database -> assertSqlServerAgentRunning(database));
    }

    return checkOperations;
  }

  protected void assertCdcEnabledInDb(final JsonNode config, final JdbcDatabase database)
      throws SQLException {
    final List<JsonNode> queryResponse = database.queryJsons(connection -> {
      final String sql = "SELECT name, is_cdc_enabled FROM sys.databases WHERE name = ?";
      final PreparedStatement ps = connection.prepareStatement(sql);
      ps.setString(1, config.get(JdbcUtils.DATABASE_KEY).asText());
      LOGGER.info(String.format("Checking that cdc is enabled on database '%s' using the query: '%s'",
          config.get(JdbcUtils.DATABASE_KEY).asText(), sql));
      return ps;
    }, sourceOperations::rowToJson);

    if (queryResponse.size() < 1) {
      throw new RuntimeException(String.format(
          "Couldn't find '%s' in sys.databases table. Please check the spelling and that the user has relevant permissions (see docs).",
          config.get(JdbcUtils.DATABASE_KEY).asText()));
    }
    if (!(queryResponse.get(0).get("is_cdc_enabled").asBoolean())) {
      throw new RuntimeException(String.format(
          "Detected that CDC is not enabled for database '%s'. Please check the documentation on how to enable CDC on MS SQL Server.",
          config.get(JdbcUtils.DATABASE_KEY).asText()));
    }
  }

  protected void assertCdcSchemaQueryable(final JsonNode config, final JdbcDatabase database)
      throws SQLException {
    final List<JsonNode> queryResponse = database.queryJsons(connection -> {
      boolean isAzureSQL = false;

      try (final Statement stmt = connection.createStatement();
          final ResultSet editionRS = stmt.executeQuery("SELECT ServerProperty('Edition')")) {
        isAzureSQL = editionRS.next() && "SQL Azure".equals(editionRS.getString(1));
      }

      // Azure SQL does not support USE clause
      final String sql =
          isAzureSQL ? "SELECT * FROM cdc.change_tables"
              : "USE [" + config.get(JdbcUtils.DATABASE_KEY).asText() + "]; SELECT * FROM cdc.change_tables";
      final PreparedStatement ps = connection.prepareStatement(sql);
      LOGGER.info(String.format(
          "Checking user '%s' can query the cdc schema and that we have at least 1 cdc enabled table using the query: '%s'",
          config.get(JdbcUtils.USERNAME_KEY).asText(), sql));
      return ps;
    }, sourceOperations::rowToJson);

    // Ensure at least one available CDC table
    if (queryResponse.size() < 1) {
      throw new RuntimeException(
          "No cdc-enabled tables found. Please check the documentation on how to enable CDC on MS SQL Server.");
    }
  }

  // todo: ensure this works for Azure managed SQL (since it uses different sql server agent)
  protected void assertSqlServerAgentRunning(final JdbcDatabase database) throws SQLException {
    try {
      // EngineEdition property values can be found at
      // https://learn.microsoft.com/en-us/sql/t-sql/functions/serverproperty-transact-sql?view=sql-server-ver16
      // SQL Server Agent is always running on SQL Managed Instance:
      // https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/transact-sql-tsql-differences-sql-server?view=azuresql#sql-server-agent
      final Integer engineEdition = database.queryInt("SELECT ServerProperty('EngineEdition')");
      if (engineEdition == 8) {
        LOGGER.info(String.format("SQL Server Agent is assumed to be running when EngineEdition == '%s'", engineEdition));
      } else {
        final List<JsonNode> queryResponse = database.queryJsons(connection -> {
          final String sql =
              "SELECT status_desc FROM sys.dm_server_services WHERE [servicename] LIKE 'SQL Server Agent%' OR [servicename] LIKE 'SQL Server 代理%' ";
          final PreparedStatement ps = connection.prepareStatement(sql);
          LOGGER.info(String.format("Checking that the SQL Server Agent is running using the query: '%s'", sql));
          return ps;
        }, sourceOperations::rowToJson);

        if (!(queryResponse.get(0).get("status_desc").toString().contains("Running"))) {
          throw new RuntimeException(String.format(
              "The SQL Server Agent is not running. Current state: '%s'. Please check the documentation on ensuring SQL Server Agent is running.",
              queryResponse.get(0).get("status_desc").toString()));
        }
      }
    } catch (final Exception e) {
      if (e.getCause() != null && e.getCause().getClass().equals(com.microsoft.sqlserver.jdbc.SQLServerException.class)) {
        LOGGER.warn(String.format(
            "Skipping check for whether the SQL Server Agent is running, SQLServerException thrown: '%s'",
            e.getMessage()));
      } else {
        throw e;
      }
    }
  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final JdbcDatabase database,
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt) {
    final JsonNode sourceConfig = database.getSourceConfig();
    if (MssqlCdcHelper.isCdc(sourceConfig) && isAnyStreamIncrementalSyncMode(catalog)) {
      LOGGER.info("using OC + CDC");
      return MssqlInitialReadUtil.getCdcReadIterators(database, catalog, tableNameToTable, stateManager, emittedAt, getQuoteString());
    } else {
      if (isAnyStreamIncrementalSyncMode(catalog)) {
        LOGGER.info("Syncing via Primary Key");
        final MssqlCursorBasedStateManager cursorBasedStateManager = new MssqlCursorBasedStateManager(stateManager.getRawStateMessages(), catalog);
        final InitialLoadStreams initialLoadStreams = streamsForInitialOrderedColumnLoad(cursorBasedStateManager, catalog);
        final Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> pairToCursorBasedStatus =
            getCursorBasedSyncStatusForStreams(database, initialLoadStreams.streamsForInitialLoad(), stateManager, quoteString);
        final CursorBasedStreams cursorBasedStreams =
            new CursorBasedStreams(identifyStreamsForCursorBased(catalog, initialLoadStreams.streamsForInitialLoad()), pairToCursorBasedStatus);

        logStreamSyncStatus(initialLoadStreams.streamsForInitialLoad(), "Primary Key");
        logStreamSyncStatus(cursorBasedStreams.streamsForCursorBased(), "Cursor");

        final MssqlInitialLoadStreamStateManager mssqlInitialLoadStreamStateManager = new MssqlInitialLoadStreamStateManager(catalog,
            initialLoadStreams, initPairToOrderedColumnInfoMap(database, initialLoadStreams, tableNameToTable, quoteString),
            namespacePair -> Jsons.jsonNode(pairToCursorBasedStatus.get(convertNameNamespacePairFromV0(namespacePair))));
        final MssqlInitialLoadHandler initialLoadHandler =
            new MssqlInitialLoadHandler(sourceConfig, database, new MssqlSourceOperations(), quoteString, mssqlInitialLoadStreamStateManager,
                getTableSizeInfoForStreams(database, initialLoadStreams.streamsForInitialLoad(), quoteString));

        final List<AutoCloseableIterator<AirbyteMessage>> initialLoadIterator = new ArrayList<>(initialLoadHandler.getIncrementalIterators(
            new ConfiguredAirbyteCatalog().withStreams(initialLoadStreams.streamsForInitialLoad()),
            tableNameToTable,
            emittedAt));

        // Build Cursor based iterator
        final List<AutoCloseableIterator<AirbyteMessage>> cursorBasedIterator =
            new ArrayList<>(super.getIncrementalIterators(database,
                new ConfiguredAirbyteCatalog().withStreams(
                    cursorBasedStreams.streamsForCursorBased()),
                tableNameToTable,
                cursorBasedStateManager, emittedAt));

        return Stream.of(initialLoadIterator, cursorBasedIterator).flatMap(Collection::stream).collect(Collectors.toList());

      }
    }

    LOGGER.info("using CDC: {}", false);
    return super.getIncrementalIterators(database, catalog, tableNameToTable, stateManager, emittedAt);
  }

  public AutoCloseableIterator<AirbyteMessage> getDebeziumSnapshotIterators(
                                                                            final JsonNode config,
                                                                            final ConfiguredAirbyteCatalog catalog,
                                                                            final CdcTargetPosition<Lsn> targetPosition,
                                                                            final Duration firstRecordWaitTime,
                                                                            final Duration subsequentRecordWaitTime,
                                                                            final MssqlCdcConnectorMetadataInjector cdcMetadataInjector,
                                                                            final Properties properties,
                                                                            final CdcStateHandler cdcStateHandler,
                                                                            final Instant emittedAt) {

    LOGGER.info("Running snapshot for " + catalog.getStreams().size() + " new tables");
    final var queue = new LinkedBlockingQueue<ChangeEvent<String, String>>(AirbyteDebeziumHandler.QUEUE_CAPACITY);

    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeDummyStateForSnapshotPurpose();
    final var emptyHistory = new AirbyteSchemaHistoryStorage.SchemaHistory<Optional<JsonNode>>(Optional.empty(), false);
    final var schemaHistoryManager = AirbyteSchemaHistoryStorage.initializeDBHistory(emptyHistory, cdcStateHandler.compressSchemaHistoryForState());
    final var propertiesManager = new RelationalDbDebeziumPropertiesManager(properties, config, catalog);
    final DebeziumRecordPublisher tableSnapshotPublisher = new DebeziumRecordPublisher(propertiesManager);
    tableSnapshotPublisher.start(queue, offsetManager, Optional.of(schemaHistoryManager));

    final AutoCloseableIterator<ChangeEventWithMetadata> eventIterator = new DebeziumRecordIterator<>(
        queue,
        targetPosition,
        tableSnapshotPublisher::hasClosed,
        new DebeziumShutdownProcedure<>(queue, tableSnapshotPublisher::close, tableSnapshotPublisher::hasClosed),
        firstRecordWaitTime,
        subsequentRecordWaitTime);

    final var eventConverter = new RelationalDbDebeziumEventConverter(cdcMetadataInjector, emittedAt);
    return AutoCloseableIterators.concatWithEagerClose(
        AutoCloseableIterators.transform(eventIterator, eventConverter::toAirbyteMessage),
        AutoCloseableIterators.fromIterator(
            MoreIterators.singletonIteratorFromSupplier(
                cdcStateHandler::saveStateAfterCompletionOfSnapshotOfNewStreams)));
  }

  @Override
  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  private static AirbyteStream overrideSyncModes(final AirbyteStream stream) {
    return stream.withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
  }

  // Note: in place mutation.
  private static AirbyteStream removeIncrementalWithoutPk(final AirbyteStream stream) {
    if (stream.getSourceDefinedPrimaryKey().isEmpty()) {
      stream.getSupportedSyncModes().remove(SyncMode.INCREMENTAL);
    }

    return stream;
  }

  // Note: in place mutation.
  private static AirbyteStream setIncrementalToSourceDefined(final AirbyteStream stream) {
    if (stream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL)) {
      stream.setSourceDefinedCursor(true);
    }

    return stream;
  }

  /*
   * To prepare for Destination v2, cdc streams must have a default cursor field Cursor format: the
   * airbyte [emittedAt] + [sync wide record counter]
   */
  private static AirbyteStream setDefaultCursorFieldForCdc(final AirbyteStream stream) {
    if (stream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL)) {
      stream.setDefaultCursorField(ImmutableList.of(CDC_DEFAULT_CURSOR));
    }
    return stream;
  }

  // Note: in place mutation.
  private static AirbyteStream addCdcMetadataColumns(final AirbyteStream stream) {

    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode airbyteIntegerType = Jsons.jsonNode(ImmutableMap.of("type", "number", "airbyte_type", "integer"));
    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LSN, stringType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);
    properties.set(CDC_EVENT_SERIAL_NO, stringType);
    properties.set(CDC_DEFAULT_CURSOR, airbyteIntegerType);

    return stream;
  }

  private void readSsl(final JsonNode sslMethod, final List<String> additionalParameters) {
    final JsonNode config = sslMethod.get("ssl_method");
    switch (config.get("ssl_method").asText()) {
      case "unencrypted" -> {
        additionalParameters.add("encrypt=false");
        additionalParameters.add("trustServerCertificate=true");
      }
      case "encrypted_trust_server_certificate" -> {
        additionalParameters.add("encrypt=true");
        additionalParameters.add("trustServerCertificate=true");
      }
      case "encrypted_verify_certificate" -> {
        additionalParameters.add("encrypt=true");
        additionalParameters.add("trustServerCertificate=false");

        if (config.has("certificate")) {
          String certificate = config.get("certificate").asText();
          String password = RandomStringUtils.randomAlphanumeric(100);
          final URI keyStoreUri;
          try {
            keyStoreUri = SSLCertificateUtils.keyStoreFromCertificate(certificate, password, null, null);
          } catch (IOException | KeyStoreException | NoSuchAlgorithmException | CertificateException e) {
            throw new RuntimeException(e);
          }
          additionalParameters
              .add("trustStore=" + keyStoreUri.getPath());
          additionalParameters
              .add("trustStorePassword=" + password);
        }

        if (config.has("hostNameInCertificate")) {
          additionalParameters
              .add("hostNameInCertificate=" + config.get("hostNameInCertificate").asText());
        }
      }
    }
  }

  @Override
  public Collection<AutoCloseableIterator<AirbyteMessage>> readStreams(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state)
      throws Exception {
    final JdbcDatabase database = createDatabase(config);
    logPreSyncDebugData(database, catalog);
    return super.readStreams(config, catalog, state);
  }

  private boolean cloudDeploymentMode() {
    return AdaptiveSourceRunner.CLOUD_MODE.equalsIgnoreCase(featureFlags.deploymentMode());
  }

  public Duration getConnectionTimeoutMssql(final Map<String, String> connectionProperties) {
    return getConnectionTimeout(connectionProperties);
  }

  @Override
  public JdbcDatabase createDatabase(final JsonNode sourceConfig) throws SQLException {
    return createDatabase(sourceConfig, JDBC_DELIMITER);
  }

  public static void main(final String[] args) throws Exception {
    final Source source = MssqlSource.sshWrappedSource(new MssqlSource());
    LOGGER.info("starting source: {}", MssqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MssqlSource.class);
  }

  @Override
  protected void logPreSyncDebugData(final JdbcDatabase database, final ConfiguredAirbyteCatalog catalog) throws SQLException {
    super.logPreSyncDebugData(database, catalog);
    MssqlQueryUtils.getIndexInfoForStreams(database, catalog, getQuoteString());
  }

}
