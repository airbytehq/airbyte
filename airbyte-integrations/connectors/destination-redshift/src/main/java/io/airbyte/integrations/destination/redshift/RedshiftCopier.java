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

package io.airbyte.integrations.destination.redshift;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream.DestinationSyncMode;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is meant to represent all the required operations to replicate an
 * {@link io.airbyte.protocol.models.AirbyteStream} into Redshift using the Copy strategy. The data
 * is streamed into a staging S3 bucket in multiple parts. This file is then loaded into a Redshift
 * temporary table via a Copy statement, before being moved into the final destination table. The
 * staging files and temporary tables are best-effort cleaned up. A single S3 file is currently
 * sufficiently performant.
 */
public class RedshiftCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftCopier.class);
  private static final NamingConventionTransformer NAMING_RESOLVER = new RedshiftSQLNameTransformer();
  private static final RedshiftSqlOperations REDSHIFT_SQL_OPS = new RedshiftSqlOperations();

  private static final int DEFAULT_UPLOAD_THREADS = 10; // The S3 cli uses 10 threads by default.
  private static final int DEFAULT_QUEUE_CAPACITY = DEFAULT_UPLOAD_THREADS;
  // The smallest part size is 5MB. An S3 upload can be maximally formed of 10,000 parts. This gives
  // us an upper limit of 10,000 * 10 / 1000 = 100 GB per table with a 10MB part size limit.
  // WARNING: Too large a part size can cause potential OOM errors.
  private static final int PART_SIZE_MB = 10;

  private final String s3BucketName;
  private final String stagingFolder;
  private final DestinationSyncMode destSyncMode;
  private final String schemaName;
  private final String streamName;
  private final AmazonS3 s3Client;
  private final JdbcDatabase redshiftDb;
  private final String s3KeyId;
  private final String s3Key;
  private final String s3Region;

  private final StreamTransferManager multipartUploadManager;
  private final MultiPartOutputStream outputStream;
  private final CSVPrinter csvPrinter;
  private final String tmpTableName;

  public RedshiftCopier(
                        String s3BucketName,
                        String stagingFolder,
                        DestinationSyncMode destSyncMode,
                        String schema,
                        String streamName,
                        AmazonS3 client,
                        JdbcDatabase redshiftDb,
                        String s3KeyId,
                        String s3key,
                        String s3Region)
      throws IOException {
    this.s3BucketName = s3BucketName;
    this.stagingFolder = stagingFolder;
    this.destSyncMode = destSyncMode;
    this.schemaName = schema;
    this.streamName = streamName;
    this.s3Client = client;
    this.redshiftDb = redshiftDb;
    this.s3KeyId = s3KeyId;
    this.s3Key = s3key;
    this.s3Region = s3Region;

    this.tmpTableName = NAMING_RESOLVER.getTmpTableName(streamName);
    // The stream transfer manager lets us greedily stream into S3. The native AWS SDK does not
    // have support for streaming multipart uploads;
    // The alternative is first writing the entire output to disk before loading into S3. This is not
    // feasible with large tables.
    // Data is chunked into parts. A part is sent off to a queue to be uploaded once it has reached it's
    // configured part size.
    // Memory consumption is queue capacity * part size = 10 * 10 = 100 MB at current configurations.
    this.multipartUploadManager =
        new StreamTransferManager(s3BucketName, getPath(stagingFolder, streamName), client)
            .numUploadThreads(DEFAULT_UPLOAD_THREADS)
            .queueCapacity(DEFAULT_QUEUE_CAPACITY)
            .partSize(PART_SIZE_MB);
    // We only need one output stream as we only have one input stream. This is reasonably performant.
    // See the above comment.
    this.outputStream = multipartUploadManager.getMultiPartOutputStreams().get(0);

    var writer = new PrintWriter(outputStream, true, StandardCharsets.UTF_8);
    this.csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT);
  }

  public static void closeAsOneTransaction(List<RedshiftCopier> copiers, boolean hasFailed, JdbcDatabase redshiftDb) throws Exception {
    try {
      StringBuilder mergeCopiersToFinalTableQuery = new StringBuilder();
      for (var copier : copiers) {
        var mergeQuery = copier.copyToRedshiftTmpTableAndPrepMergeToFinalTable(hasFailed);
        mergeCopiersToFinalTableQuery.append(mergeQuery);
      }
      REDSHIFT_SQL_OPS.executeTransaction(redshiftDb, mergeCopiersToFinalTableQuery.toString());
    } finally {
      for (var copier : copiers) {
        copier.removeS3FileAndDropTmpTable();
      }
    }
  }

  public void uploadToS3(AirbyteRecordMessage message) throws IOException {
    var id = UUID.randomUUID();
    var data = Jsons.serialize(message.getData());
    var emittedAt = Timestamp.from(Instant.ofEpochMilli(message.getEmittedAt()));
    csvPrinter.printRecord(id, data, emittedAt);
  }

  public void removeS3FileAndDropTmpTable() throws Exception {
    var s3StagingFile = getPath(stagingFolder, streamName);
    LOGGER.info("Begin cleaning s3 staging file {}.", s3StagingFile);
    if (s3Client.doesObjectExist(s3BucketName, s3StagingFile)) {
      s3Client.deleteObject(s3BucketName, s3StagingFile);
    }
    LOGGER.info("S3 staging file {} cleaned.", s3StagingFile);

    LOGGER.info("Begin cleaning {} tmp table in destination.", tmpTableName);
    REDSHIFT_SQL_OPS.dropTableIfExists(redshiftDb, schemaName, tmpTableName);
    LOGGER.info("{} tmp table in destination cleaned.", tmpTableName);
  }

  private static String getPath(String runFolder, String key) {
    return String.join("/", runFolder, key);
  }

  private static String getFullS3Path(String s3BucketName, String runFolder, String key) {
    return String.join("/", "s3:/", s3BucketName, runFolder, key);
  }

  private String copyToRedshiftTmpTableAndPrepMergeToFinalTable(boolean hasFailed) throws Exception {
    if (hasFailed) {
      multipartUploadManager.abort();
      return "";
    }
    closeS3WriteStreamAndUpload();
    createTmpTableAndCopyS3FileInto();
    return mergeIntoDestTableIncrementalOrFullRefreshQuery();
  }

  private void closeS3WriteStreamAndUpload() throws IOException {
    LOGGER.info("Uploading remaining data for {} stream.", streamName);
    csvPrinter.close();
    outputStream.close();
    multipartUploadManager.complete();
    LOGGER.info("All data for {} stream uploaded.", streamName);
  }

  private void createTmpTableAndCopyS3FileInto() throws SQLException {
    LOGGER.info("Preparing tmp table in destination for stream {}. tmp table name: {}.", streamName, tmpTableName);
    REDSHIFT_SQL_OPS.createTableIfNotExists(redshiftDb, schemaName, tmpTableName);
    LOGGER.info("Starting copy to tmp table {} in destination for stream {} .", tmpTableName, streamName);
    REDSHIFT_SQL_OPS.copyS3CsvFileIntoTable(redshiftDb, getFullS3Path(s3BucketName, stagingFolder, streamName), schemaName, tmpTableName, s3KeyId,
        s3Key,
        s3Region);
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  private String mergeIntoDestTableIncrementalOrFullRefreshQuery() throws Exception {
    LOGGER.info("Preparing tmp table {} in destination.", tmpTableName);
    var destTableName = NAMING_RESOLVER.getRawTableName(streamName);
    REDSHIFT_SQL_OPS.createTableIfNotExists(redshiftDb, schemaName, destTableName);
    LOGGER.info("Tmp table {} in destination prepared.", tmpTableName);

    LOGGER.info("Preparing to merge tmp table {} to dest table {} in destination.", tmpTableName, destTableName);
    var queries = new StringBuilder();
    if (destSyncMode.equals(DestinationSyncMode.OVERWRITE)) {
      queries.append(REDSHIFT_SQL_OPS.truncateTableQuery(schemaName, destTableName));
      LOGGER.info("Destination OVERWRITE mode detected. Dest table {} truncated.", destTableName);
    }
    queries.append(REDSHIFT_SQL_OPS.copyTableQuery(schemaName, tmpTableName, destTableName));
    return queries.toString();
  }

}
