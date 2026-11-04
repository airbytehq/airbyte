/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.StringAccessor
import io.airbyte.cdk.util.Jsons

/**
 * json and jsonb as JSON values. The value is the JSON text Postgres returns, which the PROTOBUF
 * path passes on as is. Not lossless: a JSON value is no primary key or cursor candidate.
 */
data object PostgresJsonFieldType :
    JdbcFieldType<String>(
        LeafAirbyteSchemaType.JSONB,
        StringAccessor,
        PostgresJsonCodec,
    )

/**
 * Unlike [JsonStringCodec], decodes the scalars a json column may hold too (`1`, `"a"`, `true`),
 * and the textual node in which Debezium hands over a json value.
 */
data object PostgresJsonCodec : JsonCodec<String> {
    override fun encode(decoded: String): JsonNode = JsonStringCodec.encode(decoded)

    override fun decode(encoded: JsonNode): String =
        if (encoded.isTextual) encoded.textValue() else Jsons.writeValueAsString(encoded)
}
