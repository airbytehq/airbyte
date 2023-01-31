/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.snowflake.SnowflakeInternalStagingSqlOperations.UPLOAD_RETRY_LIMIT;

import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.BlobInfo;
import com.google.cloud.storage.BucketInfo;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsConfig;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.staging.StagingOperations;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.channels.Channels;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.joda.time.DateTime;

public class SnowflakeGcsStagingSqlOperations extends SnowflakeSqlOperations implements StagingOperations {

  private final NamingConventionTransformer nameTransformer;
  private final Storage storageClient;
  private final GcsConfig gcsConfig;
  private final Set<String> fullObjectKeys = new HashSet<>();

  public SnowflakeGcsStagingSqlOperations(final NamingConventionTransformer nameTransformer, final GcsConfig gcsConfig) {
    this.nameTransformer = nameTransformer;
    this.gcsConfig = gcsConfig;
    this.storageClient = getStorageClient(gcsConfig);
  }

  private Storage getStorageClient(final GcsConfig gcsConfig) {
    try {
      final InputStream credentialsInputStream = new ByteArrayInputStream(gcsConfig.getCredentialsJson().getBytes(StandardCharsets.UTF_8));
      final GoogleCredentials credentials = GoogleCredentials.fromStream(credentialsInputStream);
      return StorageOptions.newBuilder()
          .setCredentials(credentials)
          .setProjectId(gcsConfig.getProjectId())
          .build()
          .getService();
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }

  }

  @Override
  public String getStageName(final String namespace, final String streamName) {
    return nameTransformer.applyDefaultCase(String.join("_",
        nameTransformer.convertStreamName(namespace),
        nameTransformer.convertStreamName(streamName)));
  }

  @Override
  public String getStagingPath(final UUID connectionId, final String namespace, final String streamName, final DateTime writeDatetime) {
    // see https://docs.snowflake.com/en/user-guide/data-load-considerations-stage.html
    return nameTransformer.applyDefaultCase(String.format("%s/%s_%02d_%02d_%02d/%s/",
        getStageName(namespace, streamName),
        writeDatetime.year().get(),
        writeDatetime.monthOfYear().get(),
        writeDatetime.dayOfMonth().get(),
        writeDatetime.hourOfDay().get(),
        connectionId));
  }

  @Override
  public void createStageIfNotExists(final JdbcDatabase database, final String stageName) throws Exception {
    final String bucket = gcsConfig.getBucketName();
    if (!doesBucketExist(bucket)) {
      LOGGER.info("Bucket {} does not exist; creating...", bucket);
      storageClient.create(BucketInfo.newBuilder(bucket).build());
      LOGGER.info("Bucket {} has been created.", bucket);
    }
  }

  private boolean doesBucketExist(final String bucket) {
    return storageClient.get(bucket, Storage.BucketGetOption.fields()) != null;
  }

  @Override
  public String uploadRecordsToStage(final JdbcDatabase database, final SerializableBuffer recordsData, final String schemaName, final String stageName, final String stagingPath)
      throws Exception {
    final List<Exception> exceptionsThrown = new ArrayList<>();
    while (exceptionsThrown.size() < UPLOAD_RETRY_LIMIT) {
      try {
        return loadDataIntoBucket(stagingPath, recordsData);
      } catch (final Exception e) {
        LOGGER.error("Failed to upload records into storage {}", stagingPath, e);
        exceptionsThrown.add(e);
      }
    }
    throw new RuntimeException(String.format("Exceptions thrown while uploading records into storage: %s", Strings.join(exceptionsThrown, "\n")));
  }

  private String loadDataIntoBucket(final String objectPath, final SerializableBuffer recordsData) throws IOException {

    final String fullObjectKey = objectPath + recordsData.getFilename();
    fullObjectKeys.add(fullObjectKey);

    final var blobId = BlobId.of(gcsConfig.getBucketName(), fullObjectKey);
    final var blobInfo = BlobInfo.newBuilder(blobId).build();
    final var blob = storageClient.create(blobInfo);
    final var channel = blob.writer();
    try (channel) {
      final OutputStream outputStream = Channels.newOutputStream(channel);
      final InputStream dataInputStream = recordsData.getInputStream();
      dataInputStream.transferTo(outputStream);
    } catch (final Exception e) {
      LOGGER.error("Failed to load data into storage {}", objectPath, e);
      throw new RuntimeException(e);
    }
    return recordsData.getFilename();
  }

  @Override
  public void copyIntoTableFromStage(final JdbcDatabase database,
                                        final String stageName,
                                        final String stagingPath,
                                        final List<String> stagedFiles,
                                        final String tableName,
                                        final String schemaName)
      throws Exception {
    LOGGER.info("Starting copy to target table from stage: {} in destination from stage: {}, schema: {}, .",
        tableName, stagingPath, schemaName);
    // Print actual SQL query if user needs to manually force reload from staging
    Exceptions.toRuntime(() -> database.execute(getCopyQuery(stagingPath, stagedFiles,
        tableName, schemaName)));
    LOGGER.info("Copy to target table {}.{} in destination complete.", schemaName, tableName);
  }

  private String getCopyQuery(final String stagingPath, final List<String> stagedFiles, final String dstTableName, final String schemaName) {

    return String.format(
        "COPY INTO %s.%s FROM '%s' storage_integration = gcs_airbyte_integration "
            + " file_format = (type = csv compression = auto field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') "
            + generateFilesList(stagedFiles) + ";",
        schemaName,
        dstTableName,
        generateBucketPath(stagingPath));
  }

  private String generateBucketPath(final String stagingPath) {
    return "gcs://" + gcsConfig.getBucketName() + "/" + stagingPath;
  }

  @Override
  public void cleanUpStage(final JdbcDatabase database, final String stageName, final List<String> stagedFiles) throws Exception {
    cleanUpBucketObject(stagedFiles);
  }

  private void cleanUpBucketObject(final List<String> currentStagedFiles) {
    currentStagedFiles.forEach(candidate -> fullObjectKeys.forEach(fullBlobPath -> {
      if (fullBlobPath.contains(candidate)) {
        removeBlob(fullBlobPath);
      }
    }));
  }

  private void removeBlob(final String file) {
    final var blobId = BlobId.of(gcsConfig.getBucketName(), file);
    storageClient.delete(blobId);
  }

  @Override
  public void dropStageIfExists(final JdbcDatabase database, final String stageName) throws Exception {
    dropBucketObject();
  }

  private void dropBucketObject() {
    if (!fullObjectKeys.isEmpty()) {
      final Iterator<String> iterator = fullObjectKeys.iterator();
      while (iterator.hasNext()) {
        final String element = iterator.next();
        if (element != null) {
          removeBlob(element);
          iterator.remove();
        }
      }
    }
  }

}
