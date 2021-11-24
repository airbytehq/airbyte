package io.airbyte.integrations.destination.bigquery.strategy;

import static com.amazonaws.util.StringUtils.UTF8;
import static io.airbyte.integrations.destination.bigquery.helpers.LoggerHelper.printHeapMemoryConsumption;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.CsvOptions;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.LoadJobConfiguration;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableId;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.BigQueryWriteConfig;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUploadGCSStrategy implements BigQueryUploadStrategy {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUploadGCSStrategy.class);

  private final BigQuery bigquery;

  public BigQueryUploadGCSStrategy(BigQuery bigquery) {
    this.bigquery = bigquery;
  }

  @Override
  public void upload(BigQueryWriteConfig writer, AirbyteMessage airbyteMessage, ConfiguredAirbyteCatalog catalog) {
    var airbyteRecordMessage = airbyteMessage.getRecord();
    var gcsCsvWriter = writer.getGcsCsvWriter();
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(airbyteRecordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
    final JsonNode formattedData = StandardNameTransformer.formatJsonPath(airbyteRecordMessage.getData());
    try {
      gcsCsvWriter.getCsvPrinter().printRecord(
          UUID.randomUUID().toString(),
          formattedEmittedAt,
          Jsons.serialize(formattedData));
    } catch (IOException e) {
      e.printStackTrace();
      LOGGER.warn("An error occurred writing CSV file.");
    }
  }

  @Override
  public void close(List<BigQueryWriteConfig> writeConfigList, boolean hasFailed, AirbyteMessage lastStateMessage) {
    if (!writeConfigList.isEmpty()) {
      LOGGER.info("GCS connectors that need to be closed:" + writeConfigList);
      writeConfigList.parallelStream().forEach(writer -> {
        final GcsCsvWriter gcsCsvWriter = writer.getGcsCsvWriter();

        try {
          LOGGER.info("Closing connector:" + gcsCsvWriter);
          gcsCsvWriter.close(hasFailed);
        } catch (final IOException | RuntimeException e) {
          LOGGER.error(String.format("Failed to close %s gcsWriter, \n details: %s", gcsCsvWriter, e.getMessage()));
          printHeapMemoryConsumption();
          throw new RuntimeException(e);
        }
      });
    }

    // copy data from tmp gcs storage to bigquery tables
    writeConfigList
        .forEach(pair -> {
          try {
            loadCsvFromGcsTruncate(pair);
          } catch (final Exception e) {
            LOGGER.error("Failed to load data from GCS CSV file to BigQuery tmp table with reason: " + e.getMessage());
            throw new RuntimeException(e);
          }
        });
  }

  private void loadCsvFromGcsTruncate(final BigQueryWriteConfig bigQueryWriteConfig)
      throws Exception {
    try {
      final TableId tmpTable = bigQueryWriteConfig.getTmpTable();
      final Schema schema = bigQueryWriteConfig.getSchema();
      final String csvFile = bigQueryWriteConfig.getGcsCsvWriter().getGcsCsvFileLocation();

      // Initialize client that will be used to send requests. This client only needs to be created
      // once, and can be reused for multiple requests.
      LOGGER.info(String.format("Started copying data from %s GCS csv file to %s tmp BigQuery table with schema: \n %s",
          csvFile, tmpTable, schema));

      final var csvOptions = CsvOptions.newBuilder().setEncoding(UTF8).setSkipLeadingRows(1).build();

      final LoadJobConfiguration configuration =
          LoadJobConfiguration.builder(tmpTable, csvFile)
              .setFormatOptions(csvOptions)
              .setSchema(schema)
              .setWriteDisposition(bigQueryWriteConfig.getSyncMode())
              .build();

      // For more information on Job see:
      // https://googleapis.dev/java/google-cloud-clients/latest/index.html?com/google/cloud/bigquery/package-summary.html
      // Load the table
      final Job loadJob = bigquery.create(JobInfo.of(configuration));

      LOGGER.info("Created a new job GCS csv file to tmp BigQuery table: " + loadJob);
      LOGGER.info("Waiting for job to complete...");

      // Load data from a GCS parquet file into the table
      // Blocks until this load table job completes its execution, either failing or succeeding.
      final Job completedJob = loadJob.waitFor();

      // Check for errors
      if (completedJob == null) {
        LOGGER.error("Job not executed since it no longer exists.");
        throw new Exception("Job not executed since it no longer exists.");
      } else if (completedJob.getStatus().getError() != null) {
        // You can also look at queryJob.getStatus().getExecutionErrors() for all
        // errors, not just the latest one.
        final String msg = "BigQuery was unable to load into the table due to an error: \n"
            + loadJob.getStatus().getError();
        LOGGER.error(msg);
        throw new Exception(msg);
      }
      LOGGER.info("Table is successfully overwritten by CSV file loaded from GCS");
    } catch (final BigQueryException | InterruptedException e) {
      LOGGER.error("Column not added during load append \n" + e.toString());
      throw new RuntimeException("Column not added during load append \n" + e.toString());
    }
  }
}
