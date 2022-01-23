package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SpecVersion;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

@SuppressWarnings("OptionalUsedAsFieldOrParameterType")
public class ContinuousFeedConfig {

  private static final JsonNode JSON_SCHEMA_DRAFT_07;
  private static final JsonSchemaValidator SCHEMA_VALIDATOR = new JsonSchemaValidator();
  private static final ObjectMapper MAPPER = MoreMappers.initMapper();

  static {
    final JsonSchemaFactory jsonSchemaFactory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);
    try {
      final String jsonSchemaDraft07 = MoreResources.readResource("json_schema_draft_07.json");
      JSON_SCHEMA_DRAFT_07 = Jsons.deserialize(jsonSchemaDraft07);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public enum MockCatalogType {
    SINGLE_STREAM,
    MULTI_STREAM
  }

  private final long seed;
  private final AirbyteCatalog mockCatalog;
  private final long maxMessages;
  private final Optional<Long> messageIntervalMs;

  public ContinuousFeedConfig(final JsonNode config) throws JsonValidationException {
    this.seed = parseSeed(config);
    this.mockCatalog = parseMockCatalog(config);
    this.maxMessages = parseMaxMessages(config);
    this.messageIntervalMs = parseMessageIntervalMs(config);
  }

  static long parseSeed(final JsonNode config) {
    if (!config.has("seed")) {
      return System.currentTimeMillis();
    }
    return config.get("seed").asLong();
  }

  static AirbyteCatalog parseMockCatalog(final JsonNode config) throws JsonValidationException {
    final JsonNode mockCatalogConfig = config.get("mock_catalog");
    final MockCatalogType mockCatalogType = MockCatalogType.valueOf(mockCatalogConfig.get("type").asText());
    switch (mockCatalogType) {
      case SINGLE_STREAM -> {
        final String streamName = mockCatalogConfig.get("stream_name").asText();
        final String streamSchemaText = mockCatalogConfig.get("stream_schema").asText();
        final Optional<JsonNode> streamSchema = Jsons.tryDeserialize(streamSchemaText);
        if (streamSchema.isEmpty()) {
          throw new JsonValidationException(String.format("Stream \"%s\" has invalid schema: %s", streamName, streamSchemaText));
        }
        processSchema(streamSchema.get());
        checkSchema(streamName, streamSchema.get());

        final AirbyteStream stream = new AirbyteStream().withName(streamName).withJsonSchema(streamSchema.get());
        return new AirbyteCatalog().withStreams(Collections.singletonList(stream));
      }
      case MULTI_STREAM -> {
        final String streamSchemasText = mockCatalogConfig.get("stream_schemas").asText();
        final Optional<JsonNode> streamSchemas = Jsons.tryDeserialize(streamSchemasText);
        if (streamSchemas.isEmpty()) {
          throw new JsonValidationException("Input stream schemas are invalid: %s" + streamSchemasText);
        }

        final List<AirbyteStream> streams = new LinkedList<>();
        for (final Map.Entry<String, JsonNode> entry : MoreIterators.toList(streamSchemas.get().fields())) {
          final String streamName = entry.getKey();
          final JsonNode streamSchema = Jsons.clone(entry.getValue());
          processSchema(streamSchema);
          checkSchema(streamName, streamSchema);
          streams.add(new AirbyteStream().withName(streamName).withJsonSchema(streamSchema));
        }
        return new AirbyteCatalog().withStreams(streams);
      }
      default -> throw new IllegalArgumentException("Unsupported mock catalog type: " + mockCatalogType);
    }
  }

  /**
   * Validate the stream schema against Json schema draft 07.
   */
  private static void checkSchema(final String streamName, final JsonNode streamSchema) throws JsonValidationException {
    final Set<String> validationMessages = SCHEMA_VALIDATOR.validate(JSON_SCHEMA_DRAFT_07, streamSchema);
    if (!validationMessages.isEmpty()) {
      throw new JsonValidationException(String.format(
          "Stream \"%s\" has invalid schema.\n- Errors: %s\n- Schema: %s",
          streamName,
          Strings.join(validationMessages, "; "),
          streamSchema.toString()));
    }
  }

  /**
   * Patch the schema so that 1) it allows no additional properties, and 2) all fields are required.
   * This is necessary because the mock Json object generation library may add extra properties, or
   * omit non-required fields. TODO (liren): patch the library so we don't need to patch the schema here.
   */
  private static void processSchema(final JsonNode schema) {
    if (schema.has("type") && schema.get("type").asText().equals("object")) {
      // disallow additional properties
      ((ObjectNode) schema).put("additionalProperties", false);
      if (!schema.has("properties")) {
        return;
      }
      // mark every field as required
      final ArrayNode requiredFields = MAPPER.createArrayNode();
      MoreIterators.toList(schema.get("properties").fieldNames()).forEach(requiredFields::add);
      ((ObjectNode) schema).set("required", requiredFields);

      final Iterator<JsonNode> iterator = schema.get("properties").elements();
      while (iterator.hasNext()) {
        processSchema(iterator.next());
      }
    }
  }

  static long parseMaxMessages(final JsonNode config) {
    return config.get("max_messages").asLong();
  }

  static Optional<Long> parseMessageIntervalMs(final JsonNode config) {
    if (config.has("message_interval_ms")) {
      final long messageIntervalMs = config.get("message_interval_ms").asLong();
      if (messageIntervalMs > 0) {
        return Optional.of(messageIntervalMs);
      }
    }
    return Optional.empty();
  }

  public long getSeed() {
    return seed;
  }

  public AirbyteCatalog getMockCatalog() {
    return mockCatalog;
  }

  public long getMaxMessages() {
    return maxMessages;
  }

  public Optional<Long> getMessageIntervalMs() {
    return messageIntervalMs;
  }

  @Override
  public String toString() {
    return String.format("%s{maxMessages=%d, seed=%d, messageIntervalMs=%s, mockCatalog=%s}",
        ContinuousFeedConfig.class.getSimpleName(),
        maxMessages,
        seed,
        messageIntervalMs.toString(),
        mockCatalog.toString());
  }

  @Override
  public boolean equals(final Object other) {
    if (!(other instanceof final ContinuousFeedConfig that)) {
      return false;
    }
    return this.maxMessages == that.maxMessages
        && this.seed == that.seed
        && this.messageIntervalMs.equals(that.messageIntervalMs)
        && this.mockCatalog.equals(that.mockCatalog);
  }

  @Override
  public int hashCode() {
    return Objects.hash(seed, maxMessages, messageIntervalMs, mockCatalog);
  }

}
