package io.airbyte.integrations.destination.jdbc.copy.gcs;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.BaseWriteChannel;
import com.google.cloud.WriteChannel;
import com.google.cloud.storage.Blob;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.BlobInfo;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.AbstractStreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.protocol.models.DestinationSyncMode;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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

public abstract class GcsStreamCopier extends AbstractStreamCopier {

    private static final Logger LOGGER = LoggerFactory.getLogger(GcsStreamCopier.class);

    private final String gcsStagingFile;
    private final Storage storageClient;
    private final GcsConfig gcsConfig;
    private final WriteChannel channel;
    private final CSVPrinter csvPrinter;
    private final String tmpTableName;

    public GcsStreamCopier(String stagingFolder,
                          DestinationSyncMode destSyncMode,
                          String schema,
                          String streamName,
                          Storage storageClient,
                          JdbcDatabase db,
                          GcsConfig gcsConfig,
                          ExtendedNameTransformer nameTransformer,
                          SqlOperations sqlOperations) {
        super(destSyncMode, schema, streamName, db, nameTransformer, sqlOperations);
        this.storageClient = storageClient;
        this.gcsConfig = gcsConfig;

        this.gcsStagingFile = String.join("/", stagingFolder, schemaName, streamName);
        this.tmpTableName = nameTransformer.getTmpTableName(streamName);

        Blob blob = storageClient.get(BlobId.of(gcsConfig.getBucketName(), gcsStagingFile));
        this.channel = blob.writer();
        OutputStream outputStream = Channels.newOutputStream(channel);

        var writer = new PrintWriter(outputStream, true, StandardCharsets.UTF_8);
        try {
            this.csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public void write(UUID id, String jsonDataString, Timestamp emittedAt) throws Exception {
        csvPrinter.printRecord(id, jsonDataString, emittedAt);
    }

    @Override
    public void closeStagingUploader(boolean hasFailed) throws Exception {
        LOGGER.info("Uploading remaining data for {} stream.", streamName);
        csvPrinter.close();
        channel.close();
        LOGGER.info("All data for {} stream uploaded.", streamName);
    }

    @Override
    public void copyStagingFileToTemporaryTable() throws Exception {
        LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, schema: {}, .", tmpTableName, streamName, schemaName);
        copyGcsCsvFileIntoTable(db, getFullGcsPath(gcsConfig.getBucketName(), gcsStagingFile), schemaName, tmpTableName, gcsConfig);
        LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
    }

    @Override
    public void removeFileAndDropTmpTable() throws Exception {
        LOGGER.info("Begin cleaning gcs staging file {}.", gcsStagingFile);
        var blobId = BlobId.of(gcsConfig.getBucketName(), gcsStagingFile);
        if (storageClient.get(blobId).exists()) {
            storageClient.delete(blobId);
        }
        LOGGER.info("GCS staging file {} cleaned.", gcsStagingFile);

        LOGGER.info("Begin cleaning {} tmp table in destination.", tmpTableName);
        sqlOperations.dropTableIfExists(db, schemaName, tmpTableName);
        LOGGER.info("{} tmp table in destination cleaned.", tmpTableName);
    }

    private static String getFullGcsPath(String bucketName, String stagingFile) {
        return String.join("/", "gcs://", bucketName, stagingFile);
    }

    public static void attemptWriteToPersistence(GcsConfig gcsConfig) throws IOException {
        final String outputTableName = "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
        attemptWriteAndDeleteGcsObject(gcsConfig, outputTableName);
    }

    private static void attemptWriteAndDeleteGcsObject(GcsConfig gcsConfig, String outputTableName) throws IOException {
        var storage = getStorageClient(gcsConfig);
        var blobId = BlobId.of(gcsConfig.getBucketName(), "check-content/" + outputTableName);
        var blobInfo = BlobInfo.newBuilder(blobId).build();

        storage.create(blobInfo, "".getBytes());
        storage.delete(blobId);
    }

    public static Storage getStorageClient(GcsConfig gcsConfig) throws IOException {
        InputStream credentialsInputStream = new ByteArrayInputStream(gcsConfig.getCredentialsJson().getBytes());
        GoogleCredentials credentials = GoogleCredentials.fromStream(credentialsInputStream);
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
