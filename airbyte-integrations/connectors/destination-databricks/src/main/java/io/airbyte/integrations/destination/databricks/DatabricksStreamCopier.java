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

package io.airbyte.integrations.destination.databricks;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetFormatConfig;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetWriter;
import io.airbyte.integrations.destination.s3.writer.S3WriterFactory;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.Timestamp;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This implementation is similar to
 * {@link io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier}. The difference is that
 * this implementation creates Parquet staging files, instead of CSV ones.
 * <p/>
 * It does the following operations:
 * <li>1. Parquet writer writes data stream into staging parquet file in
 * s3://<bucket-name>/<bucket-path>/<staging-folder>.</li>
 * <li>2. Create a tmp delta table based on the staging parquet file.</li>
 * <li>3. Create the destination delta table based on the tmp delta table schema in
 * s3://<bucket>/<stream-name>.</li>
 * <li>4. Copy the staging parquet file into the destination delta table.</li>
 * <li>5. Delete the tmp delta table, and the staging parquet file.</li>
 */
public class DatabricksStreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksStreamCopier.class);
  private static final ObjectMapper MAPPER = new ObjectMapper();

  private final String schemaName;
  private final String streamName;
  private final DestinationSyncMode destinationSyncMode;
  private final AmazonS3 s3Client;
  private final S3DestinationConfig s3Config;
  private final boolean purgeStagingData;
  private final JdbcDatabase database;
  private final DatabricksSqlOperations sqlOperations;

  private final String tmpTableName;
  private final String destTableName;
  private final S3ParquetWriter parquetWriter;
  private final String tmpTableLocation;
  private final String destTableLocation;

  public DatabricksStreamCopier(String stagingFolder,
                                String schema,
                                ConfiguredAirbyteStream configuredStream,
                                AmazonS3 s3Client,
                                JdbcDatabase database,
                                DatabricksDestinationConfig databricksConfig,
                                ExtendedNameTransformer nameTransformer,
                                SqlOperations sqlOperations,
                                S3WriterFactory writerFactory,
                                Timestamp uploadTime)
      throws Exception {
    this.schemaName = schema;
    this.streamName = configuredStream.getStream().getName();
    this.destinationSyncMode = configuredStream.getDestinationSyncMode();
    this.s3Client = s3Client;
    this.s3Config = databricksConfig.getS3DestinationConfig();
    this.purgeStagingData = databricksConfig.isPurgeStagingData();
    this.database = database;
    this.sqlOperations = (DatabricksSqlOperations) sqlOperations;

    this.tmpTableName = nameTransformer.getTmpTableName(streamName);
    this.destTableName = nameTransformer.getIdentifier(streamName);

    S3DestinationConfig stagingS3Config = getStagingS3DestinationConfig(s3Config, stagingFolder);
    this.parquetWriter = (S3ParquetWriter) writerFactory.create(stagingS3Config, s3Client, configuredStream, uploadTime);

    this.tmpTableLocation = String.format("s3://%s/%s",
        s3Config.getBucketName(), parquetWriter.getOutputPrefix());
    this.destTableLocation = String.format("s3://%s/%s/%s/%s",
        s3Config.getBucketName(), s3Config.getBucketPath(), databricksConfig.getDatabaseSchema(), streamName);

    LOGGER.info("[Stream {}] Database schema: {}", streamName, schemaName);
    LOGGER.info("[Stream {}] Parquet schema: {}", streamName, parquetWriter.getParquetSchema());
    LOGGER.info("[Stream {}] Tmp table {} location: {}", streamName, tmpTableName, tmpTableLocation);
    LOGGER.info("[Stream {}] Data table {} location: {}", streamName, destTableName, destTableLocation);

    parquetWriter.initialize();
  }

  @Override
  public void write(UUID id, AirbyteRecordMessage recordMessage) throws Exception {
    parquetWriter.write(id, recordMessage);
  }

  @Override
  public void closeStagingUploader(boolean hasFailed) throws Exception {
    parquetWriter.close(hasFailed);
  }

  @Override
  public void createDestinationSchema() throws Exception {
    LOGGER.info("[Stream {}] Creating database schema if it does not exist: {}", streamName, schemaName);
    sqlOperations.createSchemaIfNotExists(database, schemaName);
  }

  @Override
  public void createTemporaryTable() throws Exception {
    LOGGER.info("[Stream {}] Creating tmp table {} from staging file: {}", streamName, tmpTableName, tmpTableLocation);

    sqlOperations.dropTableIfExists(database, schemaName, tmpTableName);
    String createTmpTable = String.format("CREATE TABLE %s.%s USING parquet LOCATION '%s';", schemaName, tmpTableName, tmpTableLocation);
    LOGGER.info(createTmpTable);
    database.execute(createTmpTable);
  }

  @Override
  public void copyStagingFileToTemporaryTable() {
    // The tmp table is created directly based on the staging file. So no separate copying step is
    // needed.
  }

  @Override
  public String createDestinationTable() throws Exception {
    LOGGER.info("[Stream {}] Creating destination table if it does not exist: {}", streamName, destTableName);

    String createStatement = destinationSyncMode == DestinationSyncMode.OVERWRITE
        // "create or replace" is the recommended way to replace existing table
        ? "CREATE OR REPLACE TABLE"
        : "CREATE TABLE IF NOT EXISTS";

    String createTable = String.format(
        "%s %s.%s " +
            "USING delta " +
            "LOCATION '%s' " +
            "COMMENT 'Created from stream %s' " +
            "TBLPROPERTIES ('airbyte.destinationSyncMode' = '%s', %s) " +
            // create the table based on the schema of the tmp table
            "AS SELECT * FROM %s.%s LIMIT 0",
        createStatement,
        schemaName, destTableName,
        destTableLocation,
        streamName,
        destinationSyncMode.value(),
        String.join(", ", DatabricksConstants.DEFAULT_TBL_PROPERTIES),
        schemaName, tmpTableName);
    LOGGER.info(createTable);
    database.execute(createTable);

    return destTableName;
  }

  @Override
  public String generateMergeStatement(String destTableName) {
    String copyData = String.format(
        "COPY INTO %s.%s " +
            "FROM '%s' " +
            "FILEFORMAT = PARQUET " +
            "PATTERN = '%s'",
        schemaName, destTableName,
        tmpTableLocation,
        parquetWriter.getOutputFilename());
    LOGGER.info(copyData);
    return copyData;
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {
    if (purgeStagingData) {
      LOGGER.info("[Stream {}] Deleting tmp table: {}", streamName, tmpTableName);
      sqlOperations.dropTableIfExists(database, schemaName, tmpTableName);

      LOGGER.info("[Stream {}] Deleting staging file: {}", streamName, parquetWriter.getOutputFilePath());
      s3Client.deleteObject(s3Config.getBucketName(), parquetWriter.getOutputFilePath());
    }
  }

  /**
   * The staging data location is s3://<bucket-name>/<bucket-path>/<staging-folder>. This method
   * creates an {@link S3DestinationConfig} whose bucket path is <bucket-path>/<staging-folder>.
   */
  static S3DestinationConfig getStagingS3DestinationConfig(S3DestinationConfig config, String stagingFolder) {
    return new S3DestinationConfig(
        config.getEndpoint(),
        config.getBucketName(),
        String.join("/", config.getBucketPath(), stagingFolder),
        config.getBucketRegion(),
        config.getAccessKeyId(),
        config.getSecretAccessKey(),
        // use default parquet format config
        new S3ParquetFormatConfig(MAPPER.createObjectNode()));
  }

}
