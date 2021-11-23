/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static com.amazonaws.util.StringUtils.UTF8;
import static io.airbyte.integrations.destination.bigquery.helpers.LoggerHelper.printHeapMemoryConsumption;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.CopyJobConfiguration;
import com.google.cloud.bigquery.CsvOptions;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobInfo.CreateDisposition;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.LoadJobConfiguration;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.cloud.bigquery.TableId;
import io.airbyte.commons.bytes.ByteUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.bigquery.strategy.BigQueryUploadStrategy;
import io.airbyte.integrations.destination.bigquery.strategy.BigQueryUploadGCSStrategy;
import io.airbyte.integrations.destination.bigquery.strategy.BigQueryUploadBasicStrategy;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsS3Helper;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordConsumer.class);

  private final BigQuery bigquery;
  private final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final boolean isGcsUploadingMode;
  private final boolean isKeepFilesInGcs;
  private long bufferSizeInBytes;

  private final List<AirbyteMessage> buffer;
  private static final int MAX_BATCH_SIZE_BYTES = 1024 * 1024 * 1024 / 4; // 256 mib
  private final ConfiguredAirbyteCatalog catalog;

  private AirbyteMessage lastStateMessage = null;
  private AirbyteMessage lastFlushedState;
  private AirbyteMessage pendingState;

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
    this.buffer = new ArrayList<>(10_000);
    this.isKeepFilesInGcs = isKeepFilesInGcs;
    this.bufferSizeInBytes = 0;
  }

  @Override
  protected void startTracked() {
    // todo (cgardens) - move contents of #write into this method.
  }

  @Override
  public void acceptTracked(final AirbyteMessage message) throws IOException {
    if (message.getType() == Type.STATE) {
      lastStateMessage = message;
      pendingState = message;
    } else if (message.getType() == Type.RECORD) {
      processRecord(message);
    } else {
      LOGGER.warn("Unexpected message: " + message.getType());
    }
  }

  private void processRecord(AirbyteMessage message) {
    long messageSizeInBytes = ByteUtils.getSizeInBytes(Jsons.serialize(message));
    if (bufferSizeInBytes + messageSizeInBytes >= MAX_BATCH_SIZE_BYTES) {
      // select the way of uploading - normal or through the GCS
      flushQueueToDestination();
      bufferSizeInBytes = 0;
    }
    buffer.add(message);
    bufferSizeInBytes += messageSizeInBytes;
  }

  protected void flushQueueToDestination() {
    // ignore other message types.
    buffer.forEach(airbyteMessage -> {
      final AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair.fromRecordMessage(airbyteMessage.getRecord());
      if (!writeConfigs.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog), Jsons.serialize(airbyteMessage.getRecord())));
      }
      final BigQueryWriteConfig writer = writeConfigs.get(pair);
      if (writer.getGcsCsvWriter() != null) {
        new BigQueryUploadGCSStrategy(bigquery).upload(writer, airbyteMessage, catalog);
      } else {
        new BigQueryUploadBasicStrategy(bigquery, catalog, outputRecordCollector, lastStateMessage);
      }
    });

    buffer.clear();

    if (pendingState != null) {
      lastFlushedState = pendingState;
      pendingState = null;
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
      new BigQueryUploadGCSStrategy(bigquery).close(gcsWritersList, hasFailed);
    }

    if (isGcsUploadingMode && !isKeepFilesInGcs) {
      deleteDataFromGcsBucket();
    }

    if (lastFlushedState != null) {
      outputRecordCollector.accept(lastFlushedState);
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

      if (keysToDelete.size() > 0) {
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
