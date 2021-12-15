package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Schema;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.AirbyteRecordMessage;

public abstract class BigQueryRecordFormatter {

    private Schema bigQuerySchema;
    protected final StandardNameTransformer namingResolver;
    protected final JsonNode jsonSchema;

    public BigQueryRecordFormatter(JsonNode jsonSchema, StandardNameTransformer namingResolver) {
        this.namingResolver = namingResolver;
        this.jsonSchema = jsonSchema;
    }

    public abstract JsonNode formatRecord(AirbyteRecordMessage recordMessage);

    public Schema getBigQuerySchema() {
        if (bigQuerySchema == null)
            bigQuerySchema = getBigQuerySchema(jsonSchema);
        return bigQuerySchema;
    }

    protected abstract Schema getBigQuerySchema(JsonNode jsonSchema);
}
