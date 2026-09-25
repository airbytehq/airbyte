/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.JsonDecoder
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.LosslessFieldType
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode

/** Top-level, not in the enum's companion: enum entries initialise before their companion. */
private const val FLOAT_TS_FIELD = "float_ts"
private const val CHANNEL_ID_FIELD = "channel_id"

/**
 * The five streams of the connector, exactly as the legacy `source-slack` connector declared them:
 * name, JSON schema (a resource copied from the legacy catalog), primary key, cursor and sync
 * modes. Slack has no schema to discover: DISCOVER lists these, and READ reads whatever subset is
 * configured.
 */
enum class SlackStream(
    val streamName: String,
    val primaryKey: List<List<String>>,
    val cursorField: String?,
    /** The Slack Web API method the stream reads; each method has its own rate limit bucket. */
    val method: String,
) {
    USERS("users", listOf(listOf("id")), null, "users.list"),
    CHANNELS("channels", listOf(listOf("id")), null, "conversations.list"),
    CHANNEL_MEMBERS(
        "channel_members",
        listOf(listOf("member_id"), listOf("channel_id")),
        null,
        "conversations.members",
    ),
    CHANNEL_MESSAGES(
        "channel_messages",
        listOf(listOf("channel_id"), listOf("ts")),
        FLOAT_TS_FIELD,
        "conversations.history",
    ),
    THREADS(
        "threads",
        listOf(listOf("channel_id"), listOf("ts")),
        FLOAT_TS_FIELD,
        "conversations.replies"
    );

    val id: StreamIdentifier
        get() = StreamIdentifier.from(StreamDescriptor().withName(streamName))

    val incremental: Boolean
        get() = cursorField != null

    val supportedSyncModes: List<SyncMode>
        get() =
            if (incremental) listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
            else listOf(SyncMode.FULL_REFRESH)

    /** The legacy JSON schema of the stream (`schemas/<name>.json`); a fresh copy. */
    fun jsonSchema(): ObjectNode = schemaTemplate.deepCopy()

    /** One [EmittedField] per top-level property of the legacy schema, carrying its schema. */
    fun fields(): List<EmittedField> = fieldsFromSchema(schemaTemplate)

    private val schemaTemplate: ObjectNode by lazy {
        Jsons.readTree(ResourceUtils.readResource("schemas/$streamName.json")) as ObjectNode
    }

    companion object {
        const val FLOAT_TS = FLOAT_TS_FIELD
        const val CHANNEL_ID = CHANNEL_ID_FIELD

        fun byName(name: String): SlackStream? = entries.firstOrNull { it.streamName == name }

        fun fieldsFromSchema(schema: JsonNode): List<EmittedField> =
            schema.get("properties")?.properties()?.map { (name: String, propertySchema: JsonNode)
                ->
                EmittedField(
                    name,
                    SlackFieldType(propertySchema as? ObjectNode ?: Jsons.objectNode())
                )
            }
                ?: emptyList()
    }
}

/**
 * [io.airbyte.cdk.discover.FieldType] of a top-level property of a Slack record. Slack objects are
 * emitted as the raw JSON Slack returns, so every field carries its legacy JSON schema and passes
 * its value through unchanged; [airbyteSchemaType] is derived from that schema with the Bulk CDK's
 * own rules (a `["null", "string"]` type array is JSONB to the CDK), so that READ-time catalog
 * validation always agrees with DISCOVER.
 */
data class SlackFieldType(private val jsonSchemaTemplate: ObjectNode) : LosslessFieldType {

    override val airbyteSchemaType: AirbyteSchemaType = airbyteSchemaTypeOf(jsonSchemaTemplate)

    override val jsonEncoder: JsonEncoder<JsonNode> = PassThroughJsonCodec

    override val jsonDecoder: JsonDecoder<JsonNode> = PassThroughJsonCodec

    fun jsonSchema(): ObjectNode = jsonSchemaTemplate.deepCopy()

    companion object {
        /**
         * The [AirbyteSchemaType] of a property schema, exactly as the Bulk CDK (1.1.12,
         * `StateManagerFactory.airbyteTypeFromJsonSchema`) derives it from the configured catalog
         * at READ time: only a textual `type` is understood (a `type` array is JSONB), `string` is
         * refined by `format`, `airbyte_type` and `contentEncoding`, `number` by `airbyte_type`,
         * and an array recurses into its `items`.
         */
        fun airbyteSchemaTypeOf(jsonSchema: JsonNode): AirbyteSchemaType {
            fun value(key: String): String =
                jsonSchema[key]?.takeIf { it.isTextual }?.asText() ?: ""
            return when (value("type")) {
                "array" ->
                    ArrayAirbyteSchemaType(
                        jsonSchema["items"]?.let(::airbyteSchemaTypeOf)
                            ?: LeafAirbyteSchemaType.JSONB
                    )
                "null" -> LeafAirbyteSchemaType.NULL
                "boolean" -> LeafAirbyteSchemaType.BOOLEAN
                "number" ->
                    when (value("airbyte_type")) {
                        "integer",
                        "big_integer", -> LeafAirbyteSchemaType.INTEGER
                        else -> LeafAirbyteSchemaType.NUMBER
                    }
                "string" ->
                    when (value("format")) {
                        "date" -> LeafAirbyteSchemaType.DATE
                        "date-time" ->
                            if (value("airbyte_type") == "timestamp_with_timezone") {
                                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
                            } else {
                                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                            }
                        "time" ->
                            if (value("airbyte_type") == "time_with_timezone") {
                                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
                            } else {
                                LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                            }
                        else ->
                            if (value("contentEncoding") == "base64") {
                                LeafAirbyteSchemaType.BINARY
                            } else {
                                LeafAirbyteSchemaType.STRING
                            }
                    }
                else -> LeafAirbyteSchemaType.JSONB
            }
        }
    }
}

/** Record values are already JSON; nothing to encode or decode. */
object PassThroughJsonCodec : JsonEncoder<JsonNode>, JsonDecoder<JsonNode> {
    override fun encode(decoded: JsonNode): JsonNode = decoded

    override fun decode(encoded: JsonNode): JsonNode = encoded
}
