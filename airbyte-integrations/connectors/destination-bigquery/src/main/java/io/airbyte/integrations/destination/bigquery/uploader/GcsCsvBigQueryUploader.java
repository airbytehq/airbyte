package io.airbyte.integrations.destination.bigquery.uploader;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.*;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;
import io.airbyte.protocol.models.AirbyteRecordMessage;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

import static com.amazonaws.util.StringUtils.UTF8;

public class GcsCsvBigQueryUploader extends AbstractGscBigQueryUploader<GcsCsvWriter> {

    public GcsCsvBigQueryUploader(TableId table, TableId tmpTable, GcsCsvWriter writer, JobInfo.WriteDisposition syncMode, Schema schema, GcsDestinationConfig gcsDestinationConfig, BigQuery bigQuery, boolean isKeepFilesInGcs) {
        super(table, tmpTable, writer, syncMode, schema, gcsDestinationConfig, bigQuery, isKeepFilesInGcs);
    }

    @Override
    protected LoadJobConfiguration getLoadConfiguration() {
        final var csvOptions = CsvOptions.newBuilder().setEncoding(UTF8).setSkipLeadingRows(1).build();

        return LoadJobConfiguration.builder(tmpTable, writer.getFileLocation())
                .setFormatOptions(csvOptions)
                .setSchema(schema)
                .setWriteDisposition(syncMode)
                .build();
    }

    @Override
    protected JsonNode formatRecord(final AirbyteRecordMessage recordMessage) {
        final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
        final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
        final JsonNode formattedData = StandardNameTransformer.formatJsonPath(recordMessage.getData());
        return Jsons.jsonNode(ImmutableMap.of(
                JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT, formattedEmittedAt,
                JavaBaseConstants.COLUMN_NAME_DATA, Jsons.serialize(formattedData))
        );
    }
}
