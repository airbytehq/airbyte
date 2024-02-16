/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.cdk.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator;
import io.airbyte.cdk.integrations.destination.staging.StagingOperations;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.StringJoiner;
import java.util.UUID;
import java.util.stream.Stream;
import net.snowflake.client.jdbc.SnowflakeSQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class SnowflakeSqlOperations extends JdbcSqlOperations implements StagingOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);
  private static final int MAX_FILES_IN_LOADING_QUERY_LIMIT = 1000;

  // This is an unfortunately fragile way to capture this, but Snowflake doesn't
  // provide a more specific permission exception error code
  private static final String NO_PRIVILEGES_ERROR_MESSAGE = "but current role has no privileges on it";
  private static final String IP_NOT_IN_WHITE_LIST_ERR_MSG = "not allowed to access Snowflake";

  public static final int UPLOAD_RETRY_LIMIT = 3;

  private static final String CREATE_STAGE_QUERY =
      "CREATE STAGE IF NOT EXISTS %s encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');";
  private static final String PUT_FILE_QUERY = "PUT file://%s @%s/%s PARALLEL = %d;";
  private static final String LIST_STAGE_QUERY = "LIST @%s/%s/%s;";
  // the 1s1t copy query explicitly quotes the raw table+schema name.
  private static final String COPY_QUERY_1S1T =
      """
      COPY INTO "%s"."%s" FROM '@%s/%s'
      file_format = (
        type = csv
        compression = auto
        field_delimiter = ','
        skip_header = 0
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        NULL_IF=('')
      )""";
  private static final String DROP_STAGE_QUERY = "DROP STAGE IF EXISTS %s;";
  private static final String REMOVE_QUERY = "REMOVE @%s;";

  private final NamingConventionTransformer nameTransformer;

  public SnowflakeSqlOperations(NamingConventionTransformer nameTransformer) {
    this.nameTransformer = nameTransformer;
  }

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    try {
      if (!schemaSet.contains(schemaName) && !isSchemaExists(database, schemaName)) {
        // 1s1t is assuming a lowercase airbyte_internal schema name, so we need to quote it
        database.execute(String.format("CREATE SCHEMA IF NOT EXISTS \"%s\";", schemaName));
        schemaSet.add(schemaName);
      }
    } catch (final Exception e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        """
        CREATE TABLE IF NOT EXISTS "%s"."%s" (
          "%s" VARCHAR PRIMARY KEY,
          "%s" TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp(),
          "%s" TIMESTAMP WITH TIME ZONE DEFAULT NULL,
          "%s" VARIANT
        ) data_retention_time_in_days = 0;""",
        schemaName,
        tableName,
        JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
        JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
        JavaBaseConstants.COLUMN_NAME_DATA);
  }

  @Override
  public boolean isSchemaExists(final JdbcDatabase database, final String outputSchema) throws Exception {
    try (final Stream<JsonNode> results = database.unsafeQuery(SHOW_SCHEMAS)) {
      return results.map(schemas -> schemas.get(NAME).asText()).anyMatch(outputSchema::equals);
    } catch (final Exception e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
  }

  @Override
  public String truncateTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format("TRUNCATE TABLE \"%s\".\"%s\";\n", schemaName, tableName);
  }

  @Override
  public String dropTableIfExistsQuery(final String schemaName, final String tableName) {
    return String.format("DROP TABLE IF EXISTS \"%s\".\"%s\";\n", schemaName, tableName);
  }

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<PartialAirbyteMessage> records,
                                    final String schemaName,
                                    final String tableName)
      throws SQLException {
    LOGGER.info("actual size of batch: {}", records.size());

    // snowflake query syntax:
    // requires selecting from a set of values in order to invoke the parse_json function.
    // INSERT INTO public.users (ab_id, data, emitted_at) SELECT column1, parse_json(column2), column3
    // FROM VALUES
    // (?, ?, ?),
    // ...
    final String insertQuery;
    // Note that the column order is weird here - that's intentional, to avoid needing to change
    // SqlOperationsUtils.insertRawRecordsInSingleQuery to support a different column order.
    insertQuery = String.format(
        "INSERT INTO \"%s\".\"%s\" (\"%s\", \"%s\", \"%s\") SELECT column1, parse_json(column2), column3 FROM VALUES\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT);
    final String recordQuery = "(?, ?, ?),\n";
    SqlOperationsUtils.insertRawRecordsInSingleQuery(insertQuery, recordQuery, database, records);
  }

  @Override
  protected void insertRecordsInternalV2(final JdbcDatabase jdbcDatabase, final List<PartialAirbyteMessage> list, final String s, final String s1)
      throws Exception {
    // Snowflake doesn't have standard inserts... so we don't do this at real runtime.
    // Intentionally do nothing. This method is called from the `check` method.
    // It probably shouldn't be, but this is the easiest path to getting this working.
  }

  protected String generateFilesList(final List<String> files) {
    if (0 < files.size() && files.size() < MAX_FILES_IN_LOADING_QUERY_LIMIT) {
      // see https://docs.snowflake.com/en/user-guide/data-load-considerations-load.html#lists-of-files
      final StringJoiner joiner = new StringJoiner(",");
      files.forEach(filename -> joiner.add("'" + filename.substring(filename.lastIndexOf("/") + 1) + "'"));
      return " files = (" + joiner + ")";
    } else {
      return "";
    }
  }

  @Override
  protected Optional<ConfigErrorException> checkForKnownConfigExceptions(final Exception e) {
    if (e instanceof SnowflakeSQLException && e.getMessage().contains(NO_PRIVILEGES_ERROR_MESSAGE)) {
      return Optional.of(new ConfigErrorException(
          "Encountered Error with Snowflake Configuration: Current role does not have permissions on the target schema please verify your privileges",
          e));
    }
    if (e instanceof SnowflakeSQLException && e.getMessage().contains(IP_NOT_IN_WHITE_LIST_ERR_MSG)) {
      return Optional.of(new ConfigErrorException(
          """
              Snowflake has blocked access from Airbyte IP address. Please make sure that your Snowflake user account's
               network policy allows access from all Airbyte IP addresses. See this page for the list of Airbyte IPs:
               https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud#allowlist-ip-addresses and this page
               for documentation on Snowflake network policies: https://docs.snowflake.com/en/user-guide/network-policies
          """,
          e));
    }
    return Optional.empty();
  }

  /**
   * This method is used in Check connection method to make sure that user has the Write permission
   */
  protected void attemptWriteToStage(final String outputSchema,
                                     final String stageName,
                                     final JdbcDatabase database)
      throws Exception {

    final CsvSerializedBuffer csvSerializedBuffer = new CsvSerializedBuffer(
        new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX),
        new StagingDatabaseCsvSheetGenerator(true),
        true);

    // create a dummy stream\records that will bed used to test uploading
    csvSerializedBuffer.accept(new AirbyteRecordMessage()
        .withData(Jsons.jsonNode(Map.of("testKey", "testValue")))
        .withEmittedAt(System.currentTimeMillis()));
    csvSerializedBuffer.flush();

    uploadRecordsToStage(database, csvSerializedBuffer, outputSchema, stageName,
        stageName.endsWith("/") ? stageName : stageName + "/");
  }

  @Override
  public String getStageName(final String namespace, final String streamName) {
    return String.join(".",
        '"' + nameTransformer.convertStreamName(namespace) + '"',
        '"' + nameTransformer.convertStreamName(streamName) + '"');
  }

  @Override
  public String getStagingPath(final UUID connectionId,
                               final String namespace,
                               final String streamName,
                               final String outputTableName,
                               final Instant writeDatetime) {
    // see https://docs.snowflake.com/en/user-guide/data-load-considerations-stage.html
    final var zonedDateTime = ZonedDateTime.ofInstant(writeDatetime, ZoneOffset.UTC);
    return nameTransformer.applyDefaultCase(String.format("%s/%02d/%02d/%02d/%s/",
        zonedDateTime.getYear(),
        zonedDateTime.getMonthValue(),
        zonedDateTime.getDayOfMonth(),
        zonedDateTime.getHour(),
        connectionId));
  }

  @Override
  public String uploadRecordsToStage(final JdbcDatabase database,
                                     final SerializableBuffer recordsData,
                                     final String namespace,
                                     final String stageName,
                                     final String stagingPath)
      throws IOException {
    final List<Exception> exceptionsThrown = new ArrayList<>();
    boolean succeeded = false;
    while (exceptionsThrown.size() < UPLOAD_RETRY_LIMIT && !succeeded) {
      try {
        uploadRecordsToBucket(database, stageName, stagingPath, recordsData);
        succeeded = true;
      } catch (final Exception e) {
        LOGGER.error("Failed to upload records into stage {}", stagingPath, e);
        exceptionsThrown.add(e);
      }
      if (!succeeded) {
        LOGGER.info("Retrying to upload records into stage {} ({}/{}})", stagingPath, exceptionsThrown.size(), UPLOAD_RETRY_LIMIT);
      }
    }
    if (!succeeded) {
      throw new RuntimeException(
          String.format("Exceptions thrown while uploading records into stage: %s", Strings.join(exceptionsThrown, "\n")));
    }
    LOGGER.info("Successfully loaded records to stage {} with {} re-attempt(s)", stagingPath, exceptionsThrown.size());
    return recordsData.getFilename();
  }

  private void uploadRecordsToBucket(final JdbcDatabase database,
                                     final String stageName,
                                     final String stagingPath,
                                     final SerializableBuffer recordsData)
      throws Exception {
    final String query = getPutQuery(stageName, stagingPath, recordsData.getFile().getAbsolutePath());
    LOGGER.debug("Executing query: {}", query);
    database.execute(query);
    if (!checkStageObjectExists(database, stageName, stagingPath, recordsData.getFilename())) {
      LOGGER.error(String.format("Failed to upload data into stage, object @%s not found",
          (stagingPath + "/" + recordsData.getFilename()).replaceAll("/+", "/")));
      throw new RuntimeException("Upload failed");
    }
  }

  protected String getPutQuery(final String stageName, final String stagingPath, final String filePath) {
    return String.format(PUT_FILE_QUERY, filePath, stageName, stagingPath, Runtime.getRuntime().availableProcessors());
  }

  private boolean checkStageObjectExists(final JdbcDatabase database, final String stageName, final String stagingPath, final String filename)
      throws SQLException {
    final String query = getListQuery(stageName, stagingPath, filename);
    LOGGER.debug("Executing query: {}", query);
    final boolean result;
    try (final Stream<JsonNode> stream = database.unsafeQuery(query)) {
      result = stream.findAny().isPresent();
    }
    return result;
  }

  /**
   * Creates a SQL query to list all files that have been staged
   *
   * @param stageName name of staging folder
   * @param stagingPath path to the files within the staging folder
   * @param filename name of the file within staging area
   * @return SQL query string
   */
  protected String getListQuery(final String stageName, final String stagingPath, final String filename) {
    return String.format(LIST_STAGE_QUERY, stageName, stagingPath, filename).replaceAll("/+", "/");
  }

  @Override
  public void createStageIfNotExists(final JdbcDatabase database, final String stageName) throws Exception {
    final String query = getCreateStageQuery(stageName);
    LOGGER.debug("Executing query: {}", query);
    try {
      database.execute(query);
    } catch (final Exception e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
  }

  /**
   * Creates a SQL query to create a staging folder. This query will create a staging folder if one
   * previously did not exist
   *
   * @param stageName name of the staging folder
   * @return SQL query string
   */
  protected String getCreateStageQuery(final String stageName) {
    return String.format(CREATE_STAGE_QUERY, stageName);
  }

  @Override
  public void copyIntoTableFromStage(final JdbcDatabase database,
                                     final String stageName,
                                     final String stagingPath,
                                     final List<String> stagedFiles,
                                     final String tableName,
                                     final String schemaName)
      throws SQLException {
    try {
      final String query = getCopyQuery(stageName, stagingPath, stagedFiles, tableName, schemaName);
      LOGGER.debug("Executing query: {}", query);
      database.execute(query);
    } catch (final SQLException e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
  }

  /**
   * Creates a SQL query to bulk copy data into fully qualified destination table See
   * https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html for more context
   *
   * @param stageName name of staging folder
   * @param stagingPath path of staging folder to data files
   * @param stagedFiles collection of the staging files
   * @param dstTableName name of destination table
   * @param schemaName name of schema
   * @return SQL query string
   */
  protected String getCopyQuery(final String stageName,
                                final String stagingPath,
                                final List<String> stagedFiles,
                                final String dstTableName,
                                final String schemaName) {
    return String.format(COPY_QUERY_1S1T + generateFilesList(stagedFiles) + ";", schemaName, dstTableName, stageName, stagingPath);
  }

  @Override
  public void dropStageIfExists(final JdbcDatabase database, final String stageName, final String stagingPath) throws Exception {
    try {
      final String query = getDropQuery(stageName);
      LOGGER.debug("Executing query: {}", query);
      database.execute(query);
    } catch (final SQLException e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
  }

  /**
   * Creates a SQL query to drop staging area and all associated files within the staged area
   *
   * @param stageName name of staging folder
   * @return SQL query string
   */
  protected String getDropQuery(final String stageName) {
    return String.format(DROP_STAGE_QUERY, stageName);
  }

  /**
   * Creates a SQL query used to remove staging files that were just staged See
   * https://docs.snowflake.com/en/sql-reference/sql/remove.html for more context
   *
   * @param stageName name of staging folder
   * @return SQL query string
   */
  protected String getRemoveQuery(final String stageName) {
    return String.format(REMOVE_QUERY, stageName);
  }

}
