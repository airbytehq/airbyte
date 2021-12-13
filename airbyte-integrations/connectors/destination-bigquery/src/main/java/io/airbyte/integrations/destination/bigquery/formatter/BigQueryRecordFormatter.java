package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Schema;
import io.airbyte.protocol.models.AirbyteRecordMessage;

public interface BigQueryRecordFormatter {

    JsonNode formatRecord(final Schema schema, final AirbyteRecordMessage recordMessage);
}
