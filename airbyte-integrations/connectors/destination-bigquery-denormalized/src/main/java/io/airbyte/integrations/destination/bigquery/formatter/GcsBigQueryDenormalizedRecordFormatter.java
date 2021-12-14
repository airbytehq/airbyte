package io.airbyte.integrations.destination.bigquery.formatter;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.QueryParameterValue;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

public class GcsBigQueryDenormalizedRecordFormatter extends DefaultBigQueryDenormalizedRecordFormatter {

  public GcsBigQueryDenormalizedRecordFormatter(
      StandardNameTransformer namingResolver,
      Set<String> fieldsWithRefDefinition) {
    super(namingResolver, fieldsWithRefDefinition);
  }

  @Override
  protected void addAirbyteColumns(ObjectNode data, AirbyteRecordMessage recordMessage) {
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);

    data.put(JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString());
    data.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, emittedAtMicroseconds);
  }
}
