/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.integrations.debezium.AirbyteDebeziumHandler.shouldUseCDC;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifier;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifierList;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getIdentifierWithQuoting;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.queryTable;
import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.microsoft.sqlserver.jdbc.SQLServerResultSetMetaData;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.debezium.internals.FirstRecordWaitTimeUtil;
import io.airbyte.integrations.debezium.internals.mssql.MssqlCdcTargetPosition;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.mssql.MssqlCdcHelper.SnapshotIsolation;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.connector.sqlserver.Lsn;
import java.io.File;
import java.sql.Connection;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Supplier;
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
        SELECT CAST(IIF(EXISTS(SELECT TOP 1 1 FROM "%s"."%s" WHERE "%s" IS NULL), 1, 0) AS BIT) AS %s
      """;
  static final String DRIVER_CLASS = DatabaseDriver.MSSQLSERVER.getDriverClassName();
  public static final String MSSQL_CDC_OFFSET = "mssql_cdc_offset";
  public static final String MSSQL_DB_HISTORY = "mssql_db_history";
  public static final String CDC_LSN = "_ab_cdc_lsn";
  public static final String CDC_EVENT_SERIAL_NO = "_ab_cdc_event_serial_no";
  private static final String HIERARCHYID = "hierarchyid";
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;
  private List<String> schemas;

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new MssqlSource(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  MssqlSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new MssqlSourceOperations());
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableFullRefresh(final JdbcDatabase database,
                                                               final List<String> columnNames,
                                                               final String schemaName,
                                                               final String tableName,
                                                               final SyncMode syncMode,
                                                               final Optional<String> cursorField) {
    LOGGER.info("Queueing query for table: {}", tableName);
    // This corresponds to the initial sync for in INCREMENTAL_MODE. The ordering of the records matters as intermediate state messages are emitted.
    if (syncMode.equals(SyncMode.INCREMENTAL)) {
      final String quotedCursorField = enquoteIdentifier(cursorField.get(), getQuoteString());
      final String newIdentifiers = getWrappedColumnNames(database, null, columnNames, schemaName, tableName);
      final String preparedSqlQuery =
          String.format("SELECT %s FROM %s ORDER BY %s ASC", newIdentifiers,
              getFullyQualifiedTableNameWithQuoting(schemaName, tableName, getQuoteString()), quotedCursorField);
      LOGGER.info("Prepared SQL query for TableFullRefresh is: " + preparedSqlQuery);
      return queryTable(database, preparedSqlQuery);
    } else {
      // If we are in FULL_REFRESH mode, state messages are never emitted, so we don't care about ordering of the records.
      final String newIdentifiers = getWrappedColumnNames(database, null, columnNames, schemaName, tableName);
      final String preparedSqlQuery =
          String.format("SELECT %s FROM %s", newIdentifiers, getFullyQualifiedTableNameWithQuoting(schemaName, tableName, getQuoteString()));

      LOGGER.info("Prepared SQL query for TableFullRefresh is: " + preparedSqlQuery);
      return queryTable(database, preparedSqlQuery);
    }
  }

  /**
   * There is no support for hierarchyid even in the native SQL Server JDBC driver. Its value can be
   * converted to a nvarchar(4000) data type by calling the ToString() method. So we make a separate
   * query to get Table's MetaData, check is there any hierarchyid columns, and wrap required fields
   * with the ToString() function in the final Select query. Reference:
   * https://docs.microsoft.com/en-us/sql/t-sql/data-types/hierarchyid-data-type-method-reference?view=sql-server-ver15#data-type-conversion
   *
   * @return the list with Column names updated to handle functions (if nay) properly
   */
  @Override
  protected String getWrappedColumnNames(final JdbcDatabase database,
                                         final Connection connection,
                                         final List<String> columnNames,
                                         final String schemaName,
                                         final String tableName) {
    final List<String> hierarchyIdColumns = new ArrayList<>();
    try {
      final String identifierQuoteString = database.getMetaData().getIdentifierQuoteString();
      final SQLServerResultSetMetaData sqlServerResultSetMetaData = (SQLServerResultSetMetaData) database
          .queryMetadata(String
              .format("SELECT TOP 1 %s FROM %s", // only first row is enough to get field's type
                  enquoteIdentifierList(columnNames, getQuoteString()),
                  getFullyQualifiedTableNameWithQuoting(schemaName, tableName, getQuoteString())));

      // metadata will be null if table doesn't contain records
      if (sqlServerResultSetMetaData != null) {
        for (int i = 1; i <= sqlServerResultSetMetaData.getColumnCount(); i++) {
          if (HIERARCHYID.equals(sqlServerResultSetMetaData.getColumnTypeName(i))) {
            hierarchyIdColumns.add(sqlServerResultSetMetaData.getColumnName(i));
          }
        }
      }

      // iterate through names and replace Hierarchyid field for query is with toString() function
      // Eventually would get columns like this: testColumn.toString as "testColumn"
      // toString function in SQL server is the only way to get human readable value, but not mssql
      // specific HEX value
      return String.join(", ", columnNames.stream()
          .map(
              el -> hierarchyIdColumns.contains(el) ? String
                  .format("%s.ToString() as %s%s%s", el, identifierQuoteString, el, identifierQuoteString)
                  : getIdentifierWithQuoting(el, getQuoteString()))
          .toList());
    } catch (final SQLException e) {
      LOGGER.error("Failed to fetch metadata to prepare a proper request.", e);
      throw new RuntimeException(e);
    }
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
      checkOperations.add(database -> assertSnapshotIsolationAllowed(config, database));
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

  protected void assertSnapshotIsolationAllowed(final JsonNode config, final JdbcDatabase database)
      throws SQLException {
    if (MssqlCdcHelper.getSnapshotIsolationConfig(config) != SnapshotIsolation.SNAPSHOT) {
      return;
    }

    final List<JsonNode> queryResponse = database.queryJsons(connection -> {
      final String sql = "SELECT name, snapshot_isolation_state FROM sys.databases WHERE name = ?";
      final PreparedStatement ps = connection.prepareStatement(sql);
      ps.setString(1, config.get(JdbcUtils.DATABASE_KEY).asText());
      LOGGER.info(String.format(
          "Checking that snapshot isolation is enabled on database '%s' using the query: '%s'",
          config.get(JdbcUtils.DATABASE_KEY).asText(), sql));
      return ps;
    }, sourceOperations::rowToJson);

    if (queryResponse.size() < 1) {
      throw new RuntimeException(String.format(
          "Couldn't find '%s' in sys.databases table. Please check the spelling and that the user has relevant permissions (see docs).",
          config.get(JdbcUtils.DATABASE_KEY).asText()));
    }
    if (queryResponse.get(0).get("snapshot_isolation_state").asInt() != 1) {
      throw new RuntimeException(String.format(
          "Detected that snapshot isolation is not enabled for database '%s'. MSSQL CDC relies on snapshot isolation. "
              + "Please check the documentation on how to enable snapshot isolation on MS SQL Server.",
          config.get(JdbcUtils.DATABASE_KEY).asText()));
    }
  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(
                                                                             final JdbcDatabase database,
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt) {
    final JsonNode sourceConfig = database.getSourceConfig();
    if (MssqlCdcHelper.isCdc(sourceConfig) && shouldUseCDC(catalog)) {
      LOGGER.info("using CDC: {}", true);
      final Duration firstRecordWaitTime = FirstRecordWaitTimeUtil.getFirstRecordWaitTime(sourceConfig);
      final AirbyteDebeziumHandler<Lsn> handler =
          new AirbyteDebeziumHandler<>(sourceConfig,
              MssqlCdcTargetPosition.getTargetPosition(database, sourceConfig.get(JdbcUtils.DATABASE_KEY).asText()), true, firstRecordWaitTime);

      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(catalog,
          new MssqlCdcSavedInfoFetcher(stateManager.getCdcStateManager().getCdcState()),
          new MssqlCdcStateHandler(stateManager),
          new MssqlCdcConnectorMetadataInjector(),
          MssqlCdcHelper.getDebeziumProperties(database, catalog),
          emittedAt, true);

      return Collections.singletonList(incrementalIteratorSupplier.get());
    } else {
      LOGGER.info("using CDC: {}", false);
      return super.getIncrementalIterators(database, catalog, tableNameToTable, stateManager, emittedAt);
    }
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

  // Note: in place mutation.
  private static AirbyteStream addCdcMetadataColumns(final AirbyteStream stream) {

    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LSN, stringType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);
    properties.set(CDC_EVENT_SERIAL_NO, stringType);

    return stream;
  }

  private void readSsl(final JsonNode sslMethod, final List<String> additionalParameters) {
    final JsonNode config = sslMethod.get("ssl_method");
    switch (config.get("ssl_method").asText()) {
      case "unencrypted" -> additionalParameters.add("encrypt=false");
      case "encrypted_trust_server_certificate" -> {
        additionalParameters.add("encrypt=true");
        additionalParameters.add("trustServerCertificate=true");
      }
      case "encrypted_verify_certificate" -> {
        additionalParameters.add("encrypt=true");

        // trust store location code found at https://stackoverflow.com/a/56570588
        final String trustStoreLocation = Optional
            .ofNullable(System.getProperty("javax.net.ssl.trustStore"))
            .orElseGet(() -> System.getProperty("java.home") + "/lib/security/cacerts");
        final File trustStoreFile = new File(trustStoreLocation);
        if (!trustStoreFile.exists()) {
          throw new RuntimeException(
              "Unable to locate the Java TrustStore: the system property javax.net.ssl.trustStore is undefined or "
                  + trustStoreLocation + " does not exist.");
        }
        final String trustStorePassword = System.getProperty("javax.net.ssl.trustStorePassword");
        additionalParameters.add("trustStore=" + trustStoreLocation);
        if (trustStorePassword != null && !trustStorePassword.isEmpty()) {
          additionalParameters
              .add("trustStorePassword=" + config.get("trustStorePassword").asText());
        }
        if (config.has("hostNameInCertificate")) {
          additionalParameters
              .add("hostNameInCertificate=" + config.get("hostNameInCertificate").asText());
        }
      }
    }
  }

  public static void main(final String[] args) throws Exception {
    final Source source = MssqlSource.sshWrappedSource();
    LOGGER.info("starting source: {}", MssqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MssqlSource.class);
  }

}
