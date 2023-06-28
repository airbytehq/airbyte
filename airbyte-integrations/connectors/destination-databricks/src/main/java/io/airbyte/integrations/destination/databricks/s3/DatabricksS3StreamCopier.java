/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.s3;

import static org.apache.logging.log4j.util.Strings.EMPTY;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.databricks.DatabricksDestinationConfig;
import io.airbyte.integrations.destination.databricks.DatabricksStreamCopier;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetFormatConfig;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetWriter;
import io.airbyte.integrations.destination.s3.writer.S3WriterFactory;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.Timestamp;
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This implementation is similar to {@link StreamCopier}. The difference is that this
 * implementation creates Parquet staging files, instead of CSV ones.
 * <p>
 * </p>
 * It does the following operations:
 * <ul>
 * <li>1. Parquet writer writes data stream into staging parquet file in
 * s3://bucket-name/bucket-path/staging-folder.</li>
 * <li>2. Create a tmp delta table based on the staging parquet file.</li>
 * <li>3. Create the destination delta table based on the tmp delta table schema in
 * s3://bucket/stream-name.</li>
 * <li>4. Copy the staging parquet file into the destination delta table.</li>
 * <li>5. Delete the tmp delta table, and the staging parquet file.</li>
 * </ul>
 */
public class DatabricksS3StreamCopier extends DatabricksStreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksS3StreamCopier.class);
  private static final ObjectMapper MAPPER = new ObjectMapper();

  private final AmazonS3 s3Client;
  private final S3DestinationConfig s3Config;
  private final S3ParquetWriter parquetWriter;

  public DatabricksS3StreamCopier(final String stagingFolder,
                                  final String catalog,
                                  final String schema,
                                  final ConfiguredAirbyteStream configuredStream,
                                  final AmazonS3 s3Client,
                                  final JdbcDatabase database,
                                  final DatabricksDestinationConfig databricksConfig,
                                  final StandardNameTransformer nameTransformer,
                                  final SqlOperations sqlOperations,
                                  final S3WriterFactory writerFactory,
                                  final Timestamp uploadTime)
      throws Exception {
    super(stagingFolder, catalog, schema, configuredStream, database, databricksConfig, nameTransformer, sqlOperations);
    this.s3Client = s3Client;
    this.s3Config = databricksConfig.storageConfig().getS3DestinationConfigOrThrow();
    final S3DestinationConfig stagingS3Config = getStagingS3DestinationConfig(s3Config, stagingFolder);
    this.parquetWriter = (S3ParquetWriter) writerFactory.create(stagingS3Config, s3Client, configuredStream, uploadTime);

    LOGGER.info("[Stream {}] Parquet schema: {}", streamName, parquetWriter.getSchema());

    parquetWriter.initialize();

    LOGGER.info("[Stream {}] Tmp table {} location: {}", streamName, tmpTableName, getTmpTableLocation());
    LOGGER.info("[Stream {}] Data table {} location: {}", streamName, destTableName, getDestTableLocation());
  }

  @Override
  public String prepareStagingFile() {
    return String.join("/", s3Config.getBucketPath(), stagingFolder);
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage, final String fileName) throws Exception {
    parquetWriter.write(id, recordMessage);
  }

  @Override
  public void closeStagingUploader(final boolean hasFailed) throws Exception {
    parquetWriter.close(hasFailed);
  }

  @Override
  protected String getTmpTableLocation() {
    return String.format("s3://%s/%s",
        s3Config.getBucketName(), parquetWriter.getOutputPrefix());
  }

  @Override
  protected String getDestTableLocation() {
    return String.format("s3://%s/%s/%s/%s",
        s3Config.getBucketName(), s3Config.getBucketPath(), databricksConfig.schema(), streamName);
  }

  @Override
  protected String getCreateTempTableStatement() {
    return String.format("CREATE TABLE %s.%s.%s USING parquet LOCATION '%s';", catalogName, schemaName, tmpTableName, getTmpTableLocation());
  }

  @Override
  public String generateMergeStatement(final String destTableName) {
    final String copyData = String.format(
        "COPY INTO %s.%s.%s " +
            "FROM '%s' " +
            "FILEFORMAT = PARQUET " +
            "PATTERN = '%s' " +
            "COPY_OPTIONS ('mergeSchema' = '%s')",
        catalogName,
        schemaName,
        destTableName,
        getTmpTableLocation(),
        parquetWriter.getOutputFilename(),
        databricksConfig.enableSchemaEvolution());
    LOGGER.info(copyData);
    return copyData;
  }

  @Override
  protected void deleteStagingFile() {
    LOGGER.info("[Stream {}] Deleting staging file: {}", streamName, parquetWriter.getOutputFilePath());
    s3Client.deleteObject(s3Config.getBucketName(), parquetWriter.getOutputFilePath());
  }

  @Override
  public void closeNonCurrentStagingFileWriters() throws Exception {
    parquetWriter.close(false);
  }

  @Override
  public String getCurrentFile() {
    return "";
  }

  /**
   * The staging data location is s3://<bucket-name>/<bucket-path>/<staging-folder>. This method
   * creates an {@link S3DestinationConfig} whose bucket path is <bucket-path>/<staging-folder>.
   */
  static S3DestinationConfig getStagingS3DestinationConfig(final S3DestinationConfig config, final String stagingFolder) {
    return S3DestinationConfig.create(config)
        .withBucketPath(String.join("/", config.getBucketPath(), stagingFolder))
        .withFormatConfig(new S3ParquetFormatConfig(MAPPER.createObjectNode()))
        .withFileNamePattern(Optional.ofNullable(config.getFileNamePattern()).orElse(EMPTY))
        .get();
  }

}
