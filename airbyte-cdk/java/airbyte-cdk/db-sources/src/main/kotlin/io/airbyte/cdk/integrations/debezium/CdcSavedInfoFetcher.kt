/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage
import java.util.*

/**
 * This interface is used to fetch the saved info required for debezium to run incrementally. Each
 * connector saves offset and schema history in different manner
 */
interface CdcSavedInfoFetcher {
    val savedOffset: JsonNode?

    val savedSchemaHistory: AirbyteSchemaHistoryStorage.SchemaHistory<Optional<JsonNode>>?
}
