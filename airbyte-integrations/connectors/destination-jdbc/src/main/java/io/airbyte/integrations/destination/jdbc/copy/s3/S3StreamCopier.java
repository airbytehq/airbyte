/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class S3StreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3StreamCopier.class);

  private static final int DEFAULT_UPLOAD_THREADS = 10; // The S3 cli uses 10 threads by default.
  private static final int DEFAULT_QUEUE_CAPACITY = DEFAULT_UPLOAD_THREADS;
  // The smallest part size is 5MB. An S3 upload can be maximally formed of 10,000 parts. This gives
  // us an upper limit of 10,000 * 10 / 1000 = 100 GB per table with a 10MB part size limit.
  // WARNING: Too large a part size can cause potential OOM errors.
  public static final int DEFAULT_PART_SIZE_MB = 10;
  // It is optimal to write every 10,000,000 records (BATCH_SIZE * DEFAULT_PART) to a new file.
  // The BATCH_SIZE is defined in CopyConsumerFactory.
  // The average size of such a file will be about 1 GB.
  // This will make it easier to work with files and speed up the recording of large amounts of data.
  // In addition, for a large number of records, we will not get a drop in the copy request to
  // QUERY_TIMEOUT when
  // the records from the file are copied to the staging table.
  public static final int MAX_PARTS_PER_FILE = 1000;

  protected final AmazonS3 s3Client;
  protected final S3Config s3Config;
  protected final String tmpTableName;
  private final DestinationSyncMode destSyncMode;
  protected final String schemaName;
  protected final String streamName;
  protected final JdbcDatabase db;
  private final ExtendedNameTransformer nameTransformer;
  private final SqlOperations sqlOperations;
  protected final Set<String> s3StagingFiles = new HashSet<>();
  private final Map<String, StreamTransferManager> multipartUploadManagers = new HashMap<>();
  private final Map<String, MultiPartOutputStream> outputStreams = new HashMap<>();
  private final Map<String, CSVPrinter> csvPrinters = new HashMap<>();
  private final String s3FileName;
  protected final String stagingFolder;
  private final StagingFilenameGenerator filenameGenerator;

  public S3StreamCopier(final String stagingFolder,
                        final DestinationSyncMode destSyncMode,
                        final String schema,
                        final String streamName,
                        final String s3FileName,
                        final AmazonS3 client,
                        final JdbcDatabase db,
                        final S3Config s3Config,
                        final ExtendedNameTransformer nameTransformer,
                        final SqlOperations sqlOperations) {
    this.destSyncMode = destSyncMode;
    this.schemaName = schema;
    this.streamName = streamName;
    this.s3FileName = s3FileName;
    this.stagingFolder = stagingFolder;
    this.db = db;
    this.nameTransformer = nameTransformer;
    this.sqlOperations = sqlOperations;
    this.tmpTableName = nameTransformer.getTmpTableName(streamName);
    this.s3Client = client;
    this.s3Config = s3Config;
    this.filenameGenerator = new StagingFilenameGenerator(streamName, MAX_PARTS_PER_FILE);
  }

  private String prepareS3StagingFile() {
    return String.join("/", stagingFolder, schemaName, filenameGenerator.getStagingFilename());
  }

  @Override
  public String prepareStagingFile() {
    final var name = prepareS3StagingFile();
    if (!s3StagingFiles.contains(name)) {
      s3StagingFiles.add(name);
      LOGGER.info("S3 upload part size: {} MB", s3Config.getPartSize());
      // The stream transfer manager lets us greedily stream into S3. The native AWS SDK does not
      // have support for streaming multipart uploads;
      // The alternative is first writing the entire output to disk before loading into S3. This is not
      // feasible with large tables.
      // Data is chunked into parts. A part is sent off to a queue to be uploaded once it has reached it's
      // configured part size.
      // Memory consumption is queue capacity * part size = 10 * 10 = 100 MB at current configurations.
      final var manager = new StreamTransferManager(s3Config.getBucketName(), name, s3Client)
          .numUploadThreads(DEFAULT_UPLOAD_THREADS)
          .queueCapacity(DEFAULT_QUEUE_CAPACITY)
          .partSize(s3Config.getPartSize());
      multipartUploadManagers.put(name, manager);
      final var outputStream = manager.getMultiPartOutputStreams().get(0);
      // We only need one output stream as we only have one input stream. This is reasonably performant.
      // See the above comment.
      outputStreams.put(name, outputStream);
      final var writer = new PrintWriter(outputStream, true, StandardCharsets.UTF_8);
      try {
        csvPrinters.put(name, new CSVPrinter(writer, CSVFormat.DEFAULT));
      } catch (final IOException e) {
        throw new RuntimeException(e);
      }
    }
    return name;
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage, final String s3FileName) throws Exception {
    if (csvPrinters.containsKey(s3FileName)) {
      csvPrinters.get(s3FileName).printRecord(id,
          Jsons.serialize(recordMessage.getData()),
          Timestamp.from(Instant.ofEpochMilli(recordMessage.getEmittedAt())));
    }
  }

  @Override
  public void closeStagingUploader(final boolean hasFailed) throws Exception {
    if (hasFailed) {
      for (final var multipartUploadManager : multipartUploadManagers.values()) {
        multipartUploadManager.abort();
      }
    }
    closeAndWaitForUpload();
  }

  @Override
  public void createDestinationSchema() throws Exception {
    LOGGER.info("Creating schema in destination if it doesn't exist: {}", schemaName);
    sqlOperations.createSchemaIfNotExists(db, schemaName);
  }

  @Override
  public void createTemporaryTable() throws Exception {
    LOGGER.info("Preparing tmp table in destination for stream: {}, schema: {}, tmp table name: {}.", streamName, schemaName, tmpTableName);
    sqlOperations.createTableIfNotExists(db, schemaName, tmpTableName);
  }

  @Override
  public void copyStagingFileToTemporaryTable() throws Exception {
    LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, schema: {}, .", tmpTableName, streamName, schemaName);
    s3StagingFiles.forEach(s3StagingFile -> Exceptions.toRuntime(() -> {
      copyS3CsvFileIntoTable(db, getFullS3Path(s3Config.getBucketName(), s3StagingFile), schemaName, tmpTableName, s3Config);
    }));
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  @Override
  public String createDestinationTable() throws Exception {
    final var destTableName = nameTransformer.getRawTableName(streamName);
    LOGGER.info("Preparing table {} in destination.", destTableName);
    sqlOperations.createTableIfNotExists(db, schemaName, destTableName);
    LOGGER.info("Table {} in destination prepared.", tmpTableName);

    return destTableName;
  }

  @Override
  public String generateMergeStatement(final String destTableName) {
    LOGGER.info("Preparing to merge tmp table {} to dest table: {}, schema: {}, in destination.", tmpTableName, destTableName, schemaName);
    final var queries = new StringBuilder();
    if (destSyncMode.equals(DestinationSyncMode.OVERWRITE)) {
      queries.append(sqlOperations.truncateTableQuery(db, schemaName, destTableName));
      LOGGER.info("Destination OVERWRITE mode detected. Dest table: {}, schema: {}, truncated.", destTableName, schemaName);
    }
    queries.append(sqlOperations.copyTableQuery(db, schemaName, tmpTableName, destTableName));
    return queries.toString();
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {
    s3StagingFiles.forEach(s3StagingFile -> {
      LOGGER.info("Begin cleaning s3 staging file {}.", s3StagingFile);
      if (s3Client.doesObjectExist(s3Config.getBucketName(), s3StagingFile)) {
        s3Client.deleteObject(s3Config.getBucketName(), s3StagingFile);
      }
      LOGGER.info("S3 staging file {} cleaned.", s3StagingFile);
    });

    LOGGER.info("Begin cleaning {} tmp table in destination.", tmpTableName);
    sqlOperations.dropTableIfExists(db, schemaName, tmpTableName);
    LOGGER.info("{} tmp table in destination cleaned.", tmpTableName);
  }

  protected static String getFullS3Path(final String s3BucketName, final String s3StagingFile) {
    return String.join("/", "s3:/", s3BucketName, s3StagingFile);
  }

  /**
   * Closes the printers/outputstreams and waits for any buffered uploads to complete.
   */
  private void closeAndWaitForUpload() throws IOException {
    LOGGER.info("Uploading remaining data for {} stream.", streamName);
    for (final var csvPrinter : csvPrinters.values()) {
      csvPrinter.close();
    }
    for (final var outputStream : outputStreams.values()) {
      outputStream.close();
    }
    for (final var multipartUploadManager : multipartUploadManagers.values()) {
      multipartUploadManager.complete();
    }
    LOGGER.info("All data for {} stream uploaded.", streamName);
  }

  public static void attemptS3WriteAndDelete(final S3Config s3Config) {
    attemptS3WriteAndDelete(s3Config, "");
  }

  public static void attemptS3WriteAndDelete(final S3Config s3Config, final String bucketPath) {
    final var prefix = bucketPath.isEmpty() ? "" : bucketPath + (bucketPath.endsWith("/") ? "" : "/");
    final String outputTableName = prefix + "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
    attemptWriteAndDeleteS3Object(s3Config, outputTableName);
  }

  private static void attemptWriteAndDeleteS3Object(final S3Config s3Config, final String outputTableName) {
    final var s3 = getAmazonS3(s3Config);
    final var s3Bucket = s3Config.getBucketName();

    s3.putObject(s3Bucket, outputTableName, "check-content");
    s3.deleteObject(s3Bucket, outputTableName);
  }

  public static AmazonS3 getAmazonS3(final S3Config s3Config) {
    final var endpoint = s3Config.getEndpoint();
    final var region = s3Config.getRegion();
    final var accessKeyId = s3Config.getAccessKeyId();
    final var secretAccessKey = s3Config.getSecretAccessKey();

    final var awsCreds = new BasicAWSCredentials(accessKeyId, secretAccessKey);

    if (endpoint.isEmpty()) {
      return AmazonS3ClientBuilder.standard()
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .withRegion(s3Config.getRegion())
          .build();

    } else {

      final ClientConfiguration clientConfiguration = new ClientConfiguration();
      clientConfiguration.setSignerOverride("AWSS3V4SignerType");

      return AmazonS3ClientBuilder
          .standard()
          .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpoint, region))
          .withPathStyleAccessEnabled(true)
          .withClientConfiguration(clientConfiguration)
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .build();
    }
  }

  public abstract void copyS3CsvFileIntoTable(JdbcDatabase database,
                                              String s3FileLocation,
                                              String schema,
                                              String tableName,
                                              S3Config s3Config)
      throws SQLException;

}
