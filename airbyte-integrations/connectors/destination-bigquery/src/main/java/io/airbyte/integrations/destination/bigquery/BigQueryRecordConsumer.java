/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.google.cloud.bigquery.BigQuery;
import io.airbyte.commons.bytes.ByteUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.bigquery.BigQueryDestination.UploadingMethod;
import io.airbyte.integrations.destination.bigquery.strategy.BigQueryUploadGCSStrategy;
import io.airbyte.integrations.destination.bigquery.strategy.BigQueryUploadStandardStrategy;
import io.airbyte.integrations.destination.bigquery.strategy.BigQueryUploadStrategy;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsS3Helper;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordConsumer.class);

  private final BigQuery bigquery;
  private final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final boolean isGcsUploadingMode;
  private final boolean isKeepFilesInGcs;

  private final ConfiguredAirbyteCatalog catalog;

  private AirbyteMessage lastStateMessage = null;


  protected final Map<UploadingMethod, BigQueryUploadStrategy> bigQueryUploadStrategyMap = new ConcurrentHashMap<>();

  public BigQueryRecordConsumer(final BigQuery bigquery,
      final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
      final ConfiguredAirbyteCatalog catalog,
      final Consumer<AirbyteMessage> outputRecordCollector,
      final boolean isGcsUploadingMode,
      final boolean isKeepFilesInGcs) {
    this.bigquery = bigquery;
    this.writeConfigs = writeConfigs;
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
    this.isGcsUploadingMode = isGcsUploadingMode;
    this.isKeepFilesInGcs = isKeepFilesInGcs;
    bigQueryUploadStrategyMap.put(UploadingMethod.STANDARD, new BigQueryUploadStandardStrategy(bigquery, catalog, outputRecordCollector));
    bigQueryUploadStrategyMap.put(UploadingMethod.GCS, new BigQueryUploadGCSStrategy(bigquery));
  }

  @Override
  protected void startTracked() {
    // todo (cgardens) - move contents of #write into this method.
  }

  @Override
  public void acceptTracked(final AirbyteMessage message) throws IOException {
    if (message.getType() == Type.STATE) {
      lastStateMessage = message;
    } else if (message.getType() == Type.RECORD) {
      processRecord(message);
    } else {
      LOGGER.warn("Unexpected message: {}", message.getType());
    }
  }

  private void processRecord(AirbyteMessage message) {
    final var pair = AirbyteStreamNameNamespacePair.fromRecordMessage(message.getRecord());
    final var writer = writeConfigs.get(pair);
    if (isGcsUploadingMode) {
      bigQueryUploadStrategyMap.get(UploadingMethod.GCS).upload(writer, message, catalog);
    } else {
      bigQueryUploadStrategyMap.get(UploadingMethod.STANDARD).upload(writer, message, catalog);
    }
  }


  @Override
  public void close(final boolean hasFailed) {
    LOGGER.info("Started closing all connections");
    // process gcs streams
    if (isGcsUploadingMode) {
      final List<BigQueryWriteConfig> gcsWritersList = writeConfigs.values().parallelStream()
          .filter(el -> el.getGcsCsvWriter() != null)
          .collect(Collectors.toList());
      bigQueryUploadStrategyMap.get(UploadingMethod.GCS).close(gcsWritersList, hasFailed, lastStateMessage);
    }

    bigQueryUploadStrategyMap.get(UploadingMethod.STANDARD).close(new ArrayList<>(writeConfigs.values()), hasFailed, lastStateMessage);

    if (isGcsUploadingMode && !isKeepFilesInGcs) {
      deleteDataFromGcsBucket();
    }
  }

  private void deleteDataFromGcsBucket() {
    writeConfigs.values().forEach(writeConfig -> {
      final GcsDestinationConfig gcsDestinationConfig = writeConfig.getGcsDestinationConfig();
      final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);

      final String gcsBucketName = gcsDestinationConfig.getBucketName();
      final String gcs_bucket_path = gcsDestinationConfig.getBucketPath();

      final List<KeyVersion> keysToDelete = new LinkedList<>();
      final List<S3ObjectSummary> objects = s3Client
          .listObjects(gcsBucketName, gcs_bucket_path)
          .getObjectSummaries();
      for (final S3ObjectSummary object : objects) {
        keysToDelete.add(new KeyVersion(object.getKey()));
      }

      if (!keysToDelete.isEmpty()) {
        LOGGER.info("Tearing down test bucket path: {}/{}", gcsBucketName, gcs_bucket_path);
        // Google Cloud Storage doesn't accept request to delete multiple objects
        for (final KeyVersion keyToDelete : keysToDelete) {
          s3Client.deleteObject(gcsBucketName, keyToDelete.getKey());
        }
        LOGGER.info("Deleted {} file(s).", keysToDelete.size());
      }
      s3Client.shutdown();
    });
  }
}
