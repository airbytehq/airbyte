/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.integrations.destination.s3.writer.BaseS3Writer.determineOutputFilename;
import static org.apache.hadoop.fs.s3a.Constants.ACCESS_KEY;
import static org.apache.hadoop.fs.s3a.Constants.AWS_CREDENTIALS_PROVIDER;
import static org.apache.hadoop.fs.s3a.Constants.SECRET_KEY;
import static org.apache.hadoop.fs.s3a.Constants.SECURE_CONNECTIONS;
import static org.apache.iceberg.CatalogProperties.FILE_IO_IMPL;
import static org.apache.iceberg.CatalogProperties.WAREHOUSE_LOCATION;
import static org.apache.iceberg.aws.AwsProperties.S3FILEIO_ACCESS_KEY_ID;
import static org.apache.iceberg.aws.AwsProperties.S3FILEIO_SECRET_ACCESS_KEY;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import io.airbyte.integrations.destination.s3.template.S3FilenameTemplateParameterObject;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.io.IOException;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.Map;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericData.Record;
import org.apache.hadoop.conf.Configuration;
import org.apache.iceberg.PartitionSpec;
import org.apache.iceberg.Schema;
import org.apache.iceberg.Table;
import org.apache.iceberg.catalog.Namespace;
import org.apache.iceberg.catalog.TableIdentifier;
import org.apache.iceberg.hadoop.HadoopCatalog;
import org.apache.iceberg.io.DataWriter;
import org.apache.iceberg.parquet.Parquet;
import org.apache.iceberg.parquet.ParquetAvroWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HadoopCatalogIcebergS3ParquetWriter {

  private static final Logger LOGGER = LoggerFactory.getLogger(HadoopCatalogIcebergS3ParquetWriter.class);

  private final DataWriter<Record> parquetWriter;
  private final Table table;
  private final S3DestinationConfig config;
  private final AirbyteStream stream;
  private final HadoopCatalog catalog;
  private final AmazonS3 s3Client;
  private final String tableStorageRelativePath;

  public HadoopCatalogIcebergS3ParquetWriter(
                                             final S3DestinationConfig config,
                                             final ConfiguredAirbyteStream configuredStream,
                                             final Schema schema,
                                             final String schemaName,
                                             final String tableName,
                                             final Timestamp uploadTime)
      throws IOException {

    this.config = config;
    this.stream = configuredStream.getStream();
    this.s3Client = config.getS3Client();

    String outputFilename = determineOutputFilename(S3FilenameTemplateParameterObject
        .builder()
        .s3Format(S3Format.PARQUET)
        .timestamp(uploadTime)
        .fileExtension(S3Format.PARQUET.getFileExtension())
        .build());

    String warehousePath = String.format("s3a://%s/%s", this.config.getBucketName(), this.config.getBucketPath());

    this.tableStorageRelativePath = String.join("/", this.config.getBucketPath(), schemaName, tableName);
    initializeS3Storage();

    this.catalog = createCatalog(warehousePath);
    LOGGER.info("Warehouse path {}", warehousePath);
    Namespace namespace = Namespace.of(schemaName);
    TableIdentifier name = TableIdentifier.of(namespace, tableName);
    catalog.createTable(name, schema);
    // Create table may change the column ids of given schema before committing to metadata file which
    // brings inconsistencies between table schema and the schema used by parquetWriter.
    // For sharing consistent schema between parquetWriter and a table, loadTable is used to get the
    // updated schema which can be used by the parquetWriter
    // https://github.com/apache/iceberg/blob/master/core/src/main/java/org/apache/iceberg/TableMetadata.java#L102-L105
    this.table = catalog.loadTable(name);
    String tableLocation = table.location() + "/" + outputFilename;
    LOGGER.info("Table {} at data file location {} is created", table.name(), tableLocation);

    this.parquetWriter = Parquet.writeData(table.io().newOutputFile(tableLocation))
        .schema(table.schema())
        .createWriterFunc(ParquetAvroWriter::buildWriter)
        .overwrite()
        .withSpec(PartitionSpec.unpartitioned())
        .build();
  }

  private void initializeS3Storage() {
    try {
      final String bucket = config.getBucketName();
      if (!s3Client.doesBucketExistV2(bucket)) {
        LOGGER.info("Bucket {} does not exist; creating...", bucket);
        s3Client.createBucket(bucket);
        LOGGER.info("Bucket {} has been created.", bucket);
      }
    } catch (Exception e) {
      LOGGER.error("Failed to initialize S3 storage: ", e);
      throw e;
    }
  }

  public String getTableStorageRelativePath() {
    return tableStorageRelativePath;
  }

  public Table getTable() {
    return table;
  }

  public void write(GenericData.Record record) {
    parquetWriter.write(record);
  }

  private void closeWhenSucceed() throws IOException {
    parquetWriter.close();
  }

  private void closeWhenFail() throws IOException {
    parquetWriter.close();
  }

  public void close(final boolean hasFailed)
      throws IOException {
    try {
      if (hasFailed) {
        LOGGER.warn("Failure detected. Aborting upload of stream '{}'...", stream.getName());
        closeWhenFail();
        LOGGER.warn("Upload of stream '{}' aborted.", stream.getName());
      } else {
        LOGGER.info("Uploading remaining data for stream '{}'.", stream.getName());
        closeWhenSucceed();
        LOGGER.info("Upload completed for stream '{}'.", stream.getName());
      }
    } finally {
      table.newAppend().appendFile(parquetWriter.toDataFile()).commit();
      catalog.close();
    }
  }

  private HadoopCatalog createCatalog(String warehousePath) {
    S3AccessKeyCredentialConfig credentialConfig = (S3AccessKeyCredentialConfig) config.getS3CredentialConfig();

    System.setProperty("aws.region", config.getBucketRegion());

    Map<String, String> properties = new HashMap<>();
    properties.put(WAREHOUSE_LOCATION, warehousePath);
    properties.put(FILE_IO_IMPL, "org.apache.iceberg.aws.s3.S3FileIO");
    properties.put(S3FILEIO_ACCESS_KEY_ID, credentialConfig.getAccessKeyId());
    properties.put(S3FILEIO_SECRET_ACCESS_KEY, credentialConfig.getSecretAccessKey());

    Configuration configuration = new Configuration();
    configuration.set(AWS_CREDENTIALS_PROVIDER, "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider");
    configuration.set(ACCESS_KEY, credentialConfig.getAccessKeyId());
    configuration.set(SECRET_KEY, credentialConfig.getSecretAccessKey());
    configuration.set(SECURE_CONNECTIONS, "true");

    HadoopCatalog hadoopCatalog = new HadoopCatalog();
    hadoopCatalog.setConf(configuration);

    hadoopCatalog.initialize("hadoop-catalog", properties);

    return hadoopCatalog;
  }

}
