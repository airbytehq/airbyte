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

package io.airbyte.integrations.destination.bigquery;

import static com.amazonaws.util.StringUtils.UTF8;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.CopyJobConfiguration;
import com.google.cloud.bigquery.CsvOptions;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobInfo.CreateDisposition;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.LoadJobConfiguration;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.cloud.bigquery.TableId;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsS3Helper;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.nio.ByteBuffer;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordConsumer.class);

  private final BigQuery bigquery;
  private final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final boolean isGcsUploadingMode;
  private final boolean isKeepFilesInGcs;

  private AirbyteMessage lastStateMessage = null;

  public BigQueryRecordConsumer(BigQuery bigquery,
                                Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
                                ConfiguredAirbyteCatalog catalog,
                                Consumer<AirbyteMessage> outputRecordCollector,
                                boolean isGcsUploadingMode,
                                boolean isKeepFilesInGcs) {
    this.bigquery = bigquery;
    this.writeConfigs = writeConfigs;
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
    this.isGcsUploadingMode = isGcsUploadingMode;
    this.isKeepFilesInGcs = isKeepFilesInGcs;
  }

  @Override
  protected void startTracked() {
    // todo (cgardens) - move contents of #write into this method.
  }

  @Override
  public void acceptTracked(AirbyteMessage message) throws IOException {
    if (message.getType() == Type.STATE) {
      lastStateMessage = message;
    } else if (message.getType() == Type.RECORD) {
      final AirbyteRecordMessage recordMessage = message.getRecord();

      // ignore other message types.
      AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);
      if (!writeConfigs.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
      }
      final BigQueryWriteConfig writer = writeConfigs.get(pair);

      // select the way of uploading - normal or through the GCS
      if (writer.getGcsCsvWriter() == null) {
        // Normal uploading way
        try {
          writer.getWriter()
              .write(ByteBuffer.wrap((Jsons.serialize(formatRecord(writer.getSchema(), recordMessage)) + "\n").getBytes(Charsets.UTF_8)));
        } catch (IOException | RuntimeException e) {
          LOGGER.error("Got an error while writing message:" + e.getMessage());
          LOGGER.error(String.format(
              "Failed to process a message for job: %s, \nStreams numbers: %s, \nSyncMode: %s, \nTableName: %s, \nTmpTableName: %s, \nAirbyteMessage: %s",
              writer.getWriter().getJob(), catalog.getStreams().size(), writer.getSyncMode(), writer.getTable(), writer.getTmpTable(), message));
          printHeapMemoryConsumption();
          throw new RuntimeException(e);
        }
      } else {
        // GCS uploading way, this data will be moved to bigquery in close method
        GcsCsvWriter gcsCsvWriter = writer.getGcsCsvWriter();
        gcsCsvWriter.write(UUID.randomUUID(), recordMessage);
      }
    } else {
      LOGGER.warn("Unexpected message: " + message.getType());
    }
  }

  protected JsonNode formatRecord(Schema schema, AirbyteRecordMessage recordMessage) {
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
    final JsonNode formattedData = StandardNameTransformer.formatJsonPath(recordMessage.getData());
    return Jsons.jsonNode(ImmutableMap.of(
        JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
        JavaBaseConstants.COLUMN_NAME_DATA, Jsons.serialize(formattedData),
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT, formattedEmittedAt));
  }

  @Override
  public void close(boolean hasFailed) {
    LOGGER.info("Started closing all connections");
    // process gcs streams
    if (isGcsUploadingMode) {
      closeGcsStreamsAndCopyDataToBigQuery(hasFailed);
    }

    closeNormalBigqueryStreams(hasFailed);

    if (isGcsUploadingMode && !isKeepFilesInGcs) {
      deleteDataFromGcsBucket();
    }
  }

  private void closeGcsStreamsAndCopyDataToBigQuery(boolean hasFailed) {
    final List<BigQueryWriteConfig> gcsWritersList = writeConfigs.values().parallelStream()
        .filter(el -> el.getGcsCsvWriter() != null)
        .collect(Collectors.toList());

    if (!gcsWritersList.isEmpty()) {
      LOGGER.info("GCS connectors that need to be closed:" + gcsWritersList);
      gcsWritersList.parallelStream().forEach(writer -> {
        final GcsCsvWriter gcsCsvWriter = writer.getGcsCsvWriter();

        try {
          LOGGER.info("Closing connector:" + gcsCsvWriter);
          gcsCsvWriter.close(hasFailed);
        } catch (IOException | RuntimeException e) {
          LOGGER.error(String.format("Failed to close %s gcsWriter, \n details: %s", gcsCsvWriter, e.getMessage()));
          printHeapMemoryConsumption();
          throw new RuntimeException(e);
        }
      });
    }

    // copy data from tmp gcs storage to bigquery tables
    writeConfigs.values().stream()
        .filter(pair -> pair.getGcsCsvWriter() != null)
        .forEach(pair -> {
          try {
            loadCsvFromGcsTruncate(pair);
          } catch (Exception e) {
            LOGGER.error("Failed to load data from GCS CSV file to BibQuery tmp table with reason: " + e.getMessage());
            throw new RuntimeException(e);
          }
        });
  }

  private void loadCsvFromGcsTruncate(BigQueryWriteConfig bigQueryWriteConfig)
      throws Exception {
    try {

      TableId tmpTable = bigQueryWriteConfig.getTmpTable();
      Schema schema = bigQueryWriteConfig.getSchema();

      String csvFile = bigQueryWriteConfig.getGcsCsvWriter().getGcsCsvFileLocation();

      // Initialize client that will be used to send requests. This client only needs to be created
      // once, and can be reused for multiple requests.
      LOGGER.info(String.format("Started coping data from %s GCS csv file to %s tmp BigQuery table with schema: \n %s",
          csvFile, tmpTable, schema));

      CsvOptions csvOptions = CsvOptions.newBuilder().setEncoding(UTF8).setSkipLeadingRows(1).build();

      LoadJobConfiguration configuration =
          LoadJobConfiguration.builder(tmpTable, csvFile)
              .setFormatOptions(csvOptions)
              .setSchema(schema)
              .setWriteDisposition(bigQueryWriteConfig.getSyncMode())
              .build();

      // For more information on Job see:
      // https://googleapis.dev/java/google-cloud-clients/latest/index.html?com/google/cloud/bigquery/package-summary.html
      // Load the table
      Job loadJob = bigquery.create(JobInfo.of(configuration));

      LOGGER.info("Crated a new job GCS csv file to tmp BigQuery table: " + loadJob);
      LOGGER.info("Waiting for job to complete...");

      // Load data from a GCS parquet file into the table
      // Blocks until this load table job completes its execution, either failing or succeeding.
      Job completedJob = loadJob.waitFor();

      // Check for errors
      if (completedJob == null) {
        LOGGER.error("Job not executed since it no longer exists.");
        throw new Exception("Job not executed since it no longer exists.");
      } else if (completedJob.getStatus().getError() != null) {
        // You can also look at queryJob.getStatus().getExecutionErrors() for all
        // errors, not just the latest one.
        String msg = "BigQuery was unable to load into the table due to an error: \n"
            + loadJob.getStatus().getError();
        LOGGER.error(msg);
        throw new Exception(msg);
      }
      LOGGER.info("Table is successfully overwritten by CSV file loaded from GCS");
    } catch (BigQueryException | InterruptedException e) {
      LOGGER.error("Column not added during load append \n" + e.toString());
      throw new RuntimeException("Column not added during load append \n" + e.toString());
    }
  }

  private void closeNormalBigqueryStreams(boolean hasFailed) {
    try {
      writeConfigs.values().parallelStream().forEach(bigQueryWriteConfig -> Exceptions.toRuntime(() -> {
        TableDataWriteChannel writer = bigQueryWriteConfig.getWriter();
        try {
          writer.close();
        } catch (IOException | RuntimeException e) {
          LOGGER.error(String.format("Failed to close writer: %s, \nStreams numbers: %s",
              writer.getJob(), catalog.getStreams().size()));
          printHeapMemoryConsumption();
          throw new RuntimeException(e);
        }
      }));

      LOGGER.info("Waiting for jobs to be finished/closed");
      writeConfigs.values().forEach(bigQueryWriteConfig -> Exceptions.toRuntime(() -> {
        if (bigQueryWriteConfig.getWriter().getJob() != null) {
          try {
            bigQueryWriteConfig.getWriter().getJob().waitFor();
          } catch (RuntimeException e) {
            LOGGER.error(
                String.format("Failed to process a message for job: %s, \nStreams numbers: %s, \nSyncMode: %s, \nTableName: %s, \nTmpTableName: %s",
                    bigQueryWriteConfig.getWriter().getJob(), catalog.getStreams().size(), bigQueryWriteConfig.getSyncMode(),
                    bigQueryWriteConfig.getTable(), bigQueryWriteConfig.getTmpTable()));
            printHeapMemoryConsumption();
            throw new RuntimeException(e);
          }
        }
      }));

      if (!hasFailed) {
        LOGGER.info("Migration finished with no explicit errors. Copying data from tmp tables to permanent");
        writeConfigs.values()
            .forEach(
                bigQueryWriteConfig -> copyTable(bigquery, bigQueryWriteConfig.getTmpTable(), bigQueryWriteConfig.getTable(),
                    bigQueryWriteConfig.getSyncMode()));
        // BQ is still all or nothing if a failure happens in the destination.
        outputRecordCollector.accept(lastStateMessage);
      } else {
        LOGGER.warn("Had errors while migrations");
      }
    } finally {
      // clean up tmp tables;
      LOGGER.info("Removing tmp tables...");
      writeConfigs.values().forEach(bigQueryWriteConfig -> bigquery.delete(bigQueryWriteConfig.getTmpTable()));
      LOGGER.info("Finishing destination process...completed");
    }
  }

  private void deleteDataFromGcsBucket() {
    writeConfigs.values().forEach(writeConfig -> {
      GcsDestinationConfig gcsDestinationConfig = writeConfig.getGcsDestinationConfig();
      AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);

      String gcsBucketName = gcsDestinationConfig.getBucketName();
      String gcs_bucket_path = gcsDestinationConfig.getBucketPath();

      List<KeyVersion> keysToDelete = new LinkedList<>();
      List<S3ObjectSummary> objects = s3Client
          .listObjects(gcsBucketName, gcs_bucket_path)
          .getObjectSummaries();
      for (S3ObjectSummary object : objects) {
        keysToDelete.add(new KeyVersion(object.getKey()));
      }

      if (keysToDelete.size() > 0) {
        LOGGER.info("Tearing down test bucket path: {}/{}", gcsBucketName, gcs_bucket_path);
        // Google Cloud Storage doesn't accept request to delete multiple objects
        for (KeyVersion keyToDelete : keysToDelete) {
          s3Client.deleteObject(gcsBucketName, keyToDelete.getKey());
        }
        LOGGER.info("Deleted {} file(s).", keysToDelete.size());
      }
      s3Client.shutdown();
    });
  }

  // https://cloud.google.com/bigquery/docs/managing-tables#copying_a_single_source_table
  private static void copyTable(
                                BigQuery bigquery,
                                TableId sourceTableId,
                                TableId destinationTableId,
                                WriteDisposition syncMode) {

    final CopyJobConfiguration configuration = CopyJobConfiguration.newBuilder(destinationTableId, sourceTableId)
        .setCreateDisposition(CreateDisposition.CREATE_IF_NEEDED)
        .setWriteDisposition(syncMode)
        .build();

    final Job job = bigquery.create(JobInfo.of(configuration));
    final ImmutablePair<Job, String> jobStringImmutablePair = BigQueryUtils.executeQuery(job);
    if (jobStringImmutablePair.getRight() != null) {
      LOGGER.error("Failed on copy tables with error:" + job.getStatus());
      throw new RuntimeException("BigQuery was unable to copy table due to an error: \n" + job.getStatus().getError());
    }
    LOGGER.info("successfully copied tmp table: {} to final table: {}", sourceTableId, destinationTableId);
  }

  private void printHeapMemoryConsumption() {
    int mb = 1024 * 1024;
    MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
    long xmx = memoryBean.getHeapMemoryUsage().getMax() / mb;
    long xms = memoryBean.getHeapMemoryUsage().getInit() / mb;
    LOGGER.info("Initial Memory (xms) mb = " + xms);
    LOGGER.info("Max Memory (xmx) : mb + " + xmx);
  }

}
