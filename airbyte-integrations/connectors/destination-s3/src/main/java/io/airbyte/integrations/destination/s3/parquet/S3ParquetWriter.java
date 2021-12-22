/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.parquet;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.avro.AvroRecordFactory;
import io.airbyte.integrations.destination.s3.writer.BaseS3Writer;
import io.airbyte.integrations.destination.s3.writer.S3Writer;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.sql.Timestamp;
import java.util.UUID;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericData.Record;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.s3a.Constants;
import org.apache.parquet.avro.AvroParquetWriter;
import org.apache.parquet.hadoop.ParquetWriter;
import org.apache.parquet.hadoop.util.HadoopOutputFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import tech.allegro.schema.json2avro.converter.JsonAvroConverter;

public class S3ParquetWriter extends BaseS3Writer implements S3Writer {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3ParquetWriter.class);

  private final ParquetWriter<Record> parquetWriter;
  private final AvroRecordFactory avroRecordFactory;
  private final Schema schema;
  private final String outputFilename;
  private final String objectKey;

  public S3ParquetWriter(final S3DestinationConfig config,
                         final AmazonS3 s3Client,
                         final ConfiguredAirbyteStream configuredStream,
                         final Timestamp uploadTimestamp,
                         final Schema schema,
                         final JsonAvroConverter converter)
      throws URISyntaxException, IOException {
    super(config, s3Client, configuredStream);

    this.outputFilename = BaseS3Writer.getOutputFilename(uploadTimestamp, S3Format.PARQUET);
    objectKey = String.join("/", outputPrefix, outputFilename);

    LOGGER.info("Full S3 path for stream '{}': s3://{}/{}", stream.getName(), config.getBucketName(), objectKey);

    final URI uri = new URI(
        String.format("s3a://%s/%s/%s", config.getBucketName(), outputPrefix, outputFilename));
    final Path path = new Path(uri);

    final S3ParquetFormatConfig formatConfig = (S3ParquetFormatConfig) config.getFormatConfig();
    final Configuration hadoopConfig = getHadoopConfig(config);
    this.parquetWriter = AvroParquetWriter.<GenericData.Record>builder(HadoopOutputFile.fromPath(path, hadoopConfig))
        .withSchema(schema)
        .withCompressionCodec(formatConfig.getCompressionCodec())
        .withRowGroupSize(formatConfig.getBlockSize())
        .withMaxPaddingSize(formatConfig.getMaxPaddingSize())
        .withPageSize(formatConfig.getPageSize())
        .withDictionaryPageSize(formatConfig.getDictionaryPageSize())
        .withDictionaryEncoding(formatConfig.isDictionaryEncoding())
        .build();
    this.avroRecordFactory = new AvroRecordFactory(schema, converter);
    this.schema = schema;
  }

  public static Configuration getHadoopConfig(final S3DestinationConfig config) {
    final Configuration hadoopConfig = new Configuration();
    hadoopConfig.set(Constants.ACCESS_KEY, config.getAccessKeyId());
    hadoopConfig.set(Constants.SECRET_KEY, config.getSecretAccessKey());
    if (config.getEndpoint().isEmpty()) {
      hadoopConfig.set(Constants.ENDPOINT, String.format("s3.%s.amazonaws.com", config.getBucketRegion()));
    } else {
      hadoopConfig.set(Constants.ENDPOINT, config.getEndpoint());
      hadoopConfig.set(Constants.PATH_STYLE_ACCESS, "true");
    }
    hadoopConfig.set(Constants.AWS_CREDENTIALS_PROVIDER,
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider");
    return hadoopConfig;
  }

  public Schema getSchema() {
    return schema;
  }

  /**
   * The file path includes prefix and filename, but does not include the bucket name.
   */
  public String getOutputFilePath() {
    return outputPrefix + "/" + outputFilename;
  }

  public String getOutputFilename() {
    return outputFilename;
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage) throws IOException {
    parquetWriter.write(avroRecordFactory.getAvroRecord(id, recordMessage));
  }

  @Override
  protected void closeWhenSucceed() throws IOException {
    parquetWriter.close();
  }

  @Override
  protected void closeWhenFail() throws IOException {
    parquetWriter.close();
  }

  @Override
  public String getOutputPath() {
    return objectKey;
  }

}
