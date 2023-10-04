/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage.SchemaHistory;
import java.util.Optional;

/**
 * This interface is used to fetch the saved info required for debezium to run incrementally. Each
 * connector saves offset and schema history in different manner
 */
public interface CdcSavedInfoFetcher {

  JsonNode getSavedOffset();

  SchemaHistory<Optional<JsonNode>> getSavedSchemaHistory();

}
