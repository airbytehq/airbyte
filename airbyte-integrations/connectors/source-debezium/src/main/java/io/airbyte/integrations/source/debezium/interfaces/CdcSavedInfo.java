package io.airbyte.integrations.source.debezium.interfaces;

import com.fasterxml.jackson.databind.JsonNode;

public interface CdcSavedInfo {

  JsonNode getSavedOffset();

  JsonNode getSavedSchemaHistory();
}
