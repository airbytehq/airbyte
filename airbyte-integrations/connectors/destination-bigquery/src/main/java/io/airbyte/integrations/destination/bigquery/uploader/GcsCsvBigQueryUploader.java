package io.airbyte.integrations.destination.bigquery.uploader;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.*;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;
import io.airbyte.protocol.models.AirbyteRecordMessage;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

import static com.amazonaws.util.StringUtils.UTF8;

public class GcsCsvBigQueryUploader extends AbstractGscBigQueryUploader<GcsCsvWriter> {

    public GcsCsvBigQueryUploader(TableId table, TableId tmpTable, GcsCsvWriter writer, JobInfo.WriteDisposition syncMode, GcsDestinationConfig gcsDestinationConfig, BigQuery bigQuery, boolean isKeepFilesInGcs, BigQueryRecordFormatter recordFormatter) {
        super(table, tmpTable, writer, syncMode, gcsDestinationConfig, bigQuery, isKeepFilesInGcs, recordFormatter);
    }

    @Override
    protected LoadJobConfiguration getLoadConfiguration() {
        final var csvOptions = CsvOptions.newBuilder().setEncoding(UTF8).setSkipLeadingRows(1).build();

        return LoadJobConfiguration.builder(tmpTable, writer.getFileLocation())
                .setFormatOptions(csvOptions)
                .setSchema(recordFormatter.getBigQuerySchema())
                .setWriteDisposition(syncMode)
                .build();
    }
}
