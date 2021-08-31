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
  private final AirbyteStream stream;
  private final JdbcDatabase db;
  private final ExtendedNameTransformer nameTransformer;
  private final SqlOperations sqlOperations;
  private final S3ParquetWriter parquetWriter;

  public DatabricksStreamCopier(String stagingFolder,
                                String schema,
                                ConfiguredAirbyteStream configuredStream,
                                AmazonS3 s3Client,
                                JdbcDatabase db,
                                S3Config s3Config,
                                ExtendedNameTransformer nameTransformer,
                                SqlOperations sqlOperations,
                                S3WriterFactory writerFactory,
                                Timestamp uploadTime) throws Exception {
    this.stream = configuredStream.getStream();
    this.db = db;
    this.nameTransformer = nameTransformer;
    this.sqlOperations = sqlOperations;
    this.tmpTableName = nameTransformer.getTmpTableName(stream.getName());
    this.s3Client = s3Client;
    this.s3Config = s3Config;
    this.parquetWriter = (S3ParquetWriter) writerFactory
        .create(getS3DestinationConfig(s3Config, stagingFolder), s3Client, configuredStream, uploadTime);
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
  public void createTemporaryTable() throws Exception {

  }

  @Override
  public void copyStagingFileToTemporaryTable() throws Exception {

  }

  @Override
  public void createDestinationSchema() throws Exception {

  }

  @Override
  public String createDestinationTable() throws Exception {
    return null;
  }

  @Override
  public String generateMergeStatement(String destTableName) throws Exception {
    return null;
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
