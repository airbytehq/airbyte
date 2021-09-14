package io.airbyte.integrations.destination.databricks;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetFormatConfig;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetWriter;
import io.airbyte.integrations.destination.s3.writer.S3WriterFactory;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.Timestamp;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This implementation is similar to {@link io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier}.
 * The difference is that this implementation creates Parquet staging files, instead of CSV ones.
 */
public class DatabricksStreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksStreamCopier.class);
  private static final ObjectMapper MAPPER = new ObjectMapper();

  private final AmazonS3 s3Client;
  private final S3Config s3Config;
  private final String tmpTableName;
  private final DestinationSyncMode syncMode;
  private final AirbyteStream stream;
  private final JdbcDatabase db;
  private final String database;
  private final String streamName;
  private final ExtendedNameTransformer nameTransformer;
  private final DatabricksSqlOperations sqlOperations;
  private final S3ParquetWriter parquetWriter;

  public DatabricksStreamCopier(String stagingFolder,
                                DestinationSyncMode syncMode,
                                String schema,
                                ConfiguredAirbyteStream configuredStream,
                                String streamName,
                                AmazonS3 s3Client,
                                JdbcDatabase db,
                                S3Config s3Config,
                                ExtendedNameTransformer nameTransformer,
                                SqlOperations sqlOperations,
                                S3WriterFactory writerFactory,
                                Timestamp uploadTime) throws Exception {
    this.stream = configuredStream.getStream();
    this.syncMode = syncMode;
    this.db = db;
    this.database = schema;
    this.streamName = streamName;
    this.nameTransformer = nameTransformer;
    this.sqlOperations = (DatabricksSqlOperations) sqlOperations;
    this.tmpTableName = nameTransformer.getTmpTableName(streamName);
    this.s3Client = s3Client;
    this.s3Config = s3Config;
    this.parquetWriter = (S3ParquetWriter) writerFactory
        .create(getS3DestinationConfig(s3Config, stagingFolder), s3Client, configuredStream, uploadTime);
    LOGGER.info(parquetWriter.parquetSchema.toString());
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
    LOGGER.info("Creating database in destination if it doesn't exist: {}", database);
    sqlOperations.createSchemaIfNotExists(db, database);
  }

  @Override
  public void createTemporaryTable() throws Exception {
    LOGGER.info("Preparing tmp table in destination for stream: {}, database: {}, tmp table name: {}.", streamName, database, tmpTableName);
    LOGGER.info(parquetWriter.parquetSchema.toString());
    sqlOperations.createTableIfNotExists(db, database, tmpTableName);
  }

  @Override
  public void copyStagingFileToTemporaryTable() throws Exception {
    LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, database: {}, .", tmpTableName, streamName, database);
    // TODO: load data sql operation 
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }


  @Override
  public String createDestinationTable() throws Exception {
    var destTableName = nameTransformer.getRawTableName(streamName);
    LOGGER.info("Preparing table {} in destination.", destTableName);
    sqlOperations.createTableIfNotExists(db, database, destTableName);
    LOGGER.info("Table {} in destination prepared.", tmpTableName);

    return destTableName;
  }

  @Override
  public String generateMergeStatement(String destTableName) {
    LOGGER.info("Preparing to merge tmp table {} to dest table: {}, database: {}, in destination.", tmpTableName, destTableName, database);
    var queries = new StringBuilder();
    if (syncMode.equals(DestinationSyncMode.OVERWRITE)) {
      queries.append(sqlOperations.truncateTableQuery(db, database, destTableName));
      LOGGER.info("Destination OVERWRITE mode detected. Dest table: {}, database: {}, truncated.", destTableName, database);
    }
    queries.append(sqlOperations.copyTableQuery(db, database, tmpTableName, destTableName));
    return queries.toString();
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {

  }

  private S3DestinationConfig getS3DestinationConfig(S3Config s3Config, String stagingFolder) {
    return new S3DestinationConfig(
        s3Config.getEndpoint(),
        s3Config.getBucketName(),
        stagingFolder,
        s3Config.getRegion(),
        s3Config.getAccessKeyId(),
        s3Config.getSecretAccessKey(),
        // use default parquet format config
        new S3ParquetFormatConfig(MAPPER.createObjectNode())
    );
  }

}
