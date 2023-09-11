/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Optional;

/**
 * This interface is used to fetch the saved info required for debezium to run incrementally. Each
 * connector saves offset and schema history in different manner
 */
public interface CdcSavedInfoFetcher {

  JsonNode getSavedOffset();

  SchemaHistoryInfo getSavedSchemaHistory();

  record SchemaHistoryInfo(Optional<JsonNode> schemaHistory, boolean isSchemaHistoryCompressed, boolean compressionEnabled) {}

}
