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

package io.airbyte.integrations.destination.jdbc.copy.gcs;

import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.WriteChannel;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.BlobInfo;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.nio.channels.Channels;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class GcsStreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsStreamCopier.class);

  private final String gcsStagingFile;
  private final Storage storageClient;
  private final GcsConfig gcsConfig;
  private final WriteChannel channel;
  private final CSVPrinter csvPrinter;
  private final String tmpTableName;
  private final DestinationSyncMode destSyncMode;
  private final String schemaName;
  private final String streamName;
  private final JdbcDatabase db;
  private final ExtendedNameTransformer nameTransformer;
  private final SqlOperations sqlOperations;

  public GcsStreamCopier(final String stagingFolder,
                         final DestinationSyncMode destSyncMode,
                         final String schema,
                         final String streamName,
                         final Storage storageClient,
                         final JdbcDatabase db,
                         final GcsConfig gcsConfig,
                         final ExtendedNameTransformer nameTransformer,
                         final SqlOperations sqlOperations) {
    this.destSyncMode = destSyncMode;
    this.schemaName = schema;
    this.streamName = streamName;
    this.db = db;
    this.nameTransformer = nameTransformer;
    this.sqlOperations = sqlOperations;
    this.tmpTableName = nameTransformer.getTmpTableName(streamName);
    this.storageClient = storageClient;
    this.gcsConfig = gcsConfig;

    this.gcsStagingFile = String.join("/", stagingFolder, schemaName, streamName);

    final var blobId = BlobId.of(gcsConfig.getBucketName(), gcsStagingFile);
    final var blobInfo = BlobInfo.newBuilder(blobId).build();
    final var blob = storageClient.create(blobInfo);
    this.channel = blob.writer();
    final OutputStream outputStream = Channels.newOutputStream(channel);

    final var writer = new PrintWriter(outputStream, true, StandardCharsets.UTF_8);
    try {
      this.csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void write(final UUID id, final String jsonDataString, final Timestamp emittedAt) throws Exception {
    csvPrinter.printRecord(id, jsonDataString, emittedAt);
  }

  @Override
  public void closeStagingUploader(final boolean hasFailed) throws Exception {
    LOGGER.info("Uploading remaining data for {} stream.", streamName);
    csvPrinter.close();
    channel.close();
    LOGGER.info("All data for {} stream uploaded.", streamName);
  }

  @Override
  public void copyStagingFileToTemporaryTable() throws Exception {
    LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, schema: {}.", tmpTableName, streamName, schemaName);
    copyGcsCsvFileIntoTable(db, getFullGcsPath(gcsConfig.getBucketName(), gcsStagingFile), schemaName, tmpTableName, gcsConfig);
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {
    LOGGER.info("Begin cleaning gcs staging file {}.", gcsStagingFile);
    final var blobId = BlobId.of(gcsConfig.getBucketName(), gcsStagingFile);
    if (storageClient.get(blobId).exists()) {
      storageClient.delete(blobId);
    }
    LOGGER.info("GCS staging file {} cleaned.", gcsStagingFile);

    LOGGER.info("Begin cleaning {} tmp table in destination.", tmpTableName);
    sqlOperations.dropTableIfExists(db, schemaName, tmpTableName);
    LOGGER.info("{} tmp table in destination cleaned.", tmpTableName);
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
  public String createDestinationTable() throws Exception {
    final var destTableName = nameTransformer.getRawTableName(streamName);
    LOGGER.info("Preparing table {} in destination.", destTableName);
    sqlOperations.createTableIfNotExists(db, schemaName, destTableName);
    LOGGER.info("Table {} in destination prepared.", tmpTableName);

    return destTableName;
  }

  @Override
  public String generateMergeStatement(final String destTableName) throws Exception {
    LOGGER.info("Preparing to merge tmp table {} to dest table: {}, schema: {}, in destination.", tmpTableName, destTableName, schemaName);
    final var queries = new StringBuilder();
    if (destSyncMode.equals(DestinationSyncMode.OVERWRITE)) {
      queries.append(sqlOperations.truncateTableQuery(db, schemaName, destTableName));
      LOGGER.info("Destination OVERWRITE mode detected. Dest table: {}, schema: {}, will be truncated.", destTableName, schemaName);
    }
    queries.append(sqlOperations.copyTableQuery(db, schemaName, tmpTableName, destTableName));
    return queries.toString();
  }

  private static String getFullGcsPath(final String bucketName, final String stagingFile) {
    // this is intentionally gcs:/ not gcs:// since the join adds the additional slash
    return String.join("/", "gcs:/", bucketName, stagingFile);
  }

  public static void attemptWriteToPersistence(final GcsConfig gcsConfig) throws IOException {
    final String outputTableName = "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
    attemptWriteAndDeleteGcsObject(gcsConfig, outputTableName);
  }

  private static void attemptWriteAndDeleteGcsObject(final GcsConfig gcsConfig, final String outputTableName) throws IOException {
    final var storage = getStorageClient(gcsConfig);
    final var blobId = BlobId.of(gcsConfig.getBucketName(), "check-content/" + outputTableName);
    final var blobInfo = BlobInfo.newBuilder(blobId).build();

    storage.create(blobInfo, "".getBytes());
    storage.delete(blobId);
  }

  public static Storage getStorageClient(final GcsConfig gcsConfig) throws IOException {
    final InputStream credentialsInputStream = new ByteArrayInputStream(gcsConfig.getCredentialsJson().getBytes());
    final GoogleCredentials credentials = GoogleCredentials.fromStream(credentialsInputStream);
    return StorageOptions.newBuilder()
        .setCredentials(credentials)
        .setProjectId(gcsConfig.getProjectId())
        .build()
        .getService();
  }

  public abstract void copyGcsCsvFileIntoTable(JdbcDatabase database,
                                               String gcsFileLocation,
                                               String schema,
                                               String tableName,
                                               GcsConfig gcsConfig)
      throws SQLException;

}
