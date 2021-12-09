package io.airbyte.integrations.destination.bigquery.uploader;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.*;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.avro.GcsAvroWriter;
import io.airbyte.protocol.models.AirbyteRecordMessage;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

public class GcsAvroBigQueryUploader extends AbstractGscBigQueryUploader<GcsAvroWriter> {

    public GcsAvroBigQueryUploader(TableId table, TableId tmpTable, GcsAvroWriter writer, JobInfo.WriteDisposition syncMode, Schema schema, GcsDestinationConfig gcsDestinationConfig, BigQuery bigQuery, boolean isKeepFilesInGcs) {
        super(table, tmpTable, writer, syncMode, schema, gcsDestinationConfig, bigQuery, isKeepFilesInGcs);
    }

    @Override
    protected LoadJobConfiguration getLoadConfiguration() {
        return LoadJobConfiguration.builder(tmpTable, writer.getFileLocation()).setFormatOptions(FormatOptions.avro()).setSchema(schema)
                .setWriteDisposition(syncMode)
                .build();
    }

    @Override
    protected JsonNode formatRecord(final AirbyteRecordMessage recordMessage) {
        final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
        final JsonNode formattedData = StandardNameTransformer.formatJsonPath(recordMessage.getData());
        return Jsons.jsonNode(ImmutableMap.of(
                JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
                JavaBaseConstants.COLUMN_NAME_DATA, formattedData.toString(),
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT, emittedAtMicroseconds));
    }

}
