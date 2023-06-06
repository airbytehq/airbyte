package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.LegacyOneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Object;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Primitive;
import java.util.LinkedHashMap;
import java.util.List;

public sealed interface AirbyteType permits Array, LegacyOneOf, Object, OneOf, Primitive {

  /**
   * The most common call pattern is probably to use this method on the stream schema, verify that it's an {@link Object} schema, and then call
   * {@link Object#properties()} to get the columns.
   * <p>
   * If the top-level schema is not an object, then we can't really do anything with it, and should probably fail the sync.
   */
  static AirbyteType fromJsonSchema(JsonNode schema) {
    // TODO
    return null;
  }

  enum Primitive implements AirbyteType {
    STRING,
    NUMBER,
    INTEGER,
    BOOLEAN,
    TIMESTAMP_WITH_TIMEZONE,
    TIMESTAMP_WITHOUT_TIMEZONE,
    TIME_WITH_TIMEZONE,
    TIME_WITHOUT_TIMEZONE,
    DATE,
    // TODO maybe this should be its own class
    UNKNOWN
  }

  /**
   * @param properties Use LinkedHashMap to preserve insertion order.
   */
  // TODO maybe we shouldn't call this thing Object, since java.lang.Object also exists?
  record Object(LinkedHashMap<String, AirbyteType> properties) implements AirbyteType {

  }

  record Array(AirbyteType items) implements AirbyteType {

  }

  /**
   * Represents a {oneOf: [...]} schema.
   * <p>
   * See also {@link LegacyOneOf} - in principle, {type: [a, b, ...]} schemas should also parse into OneOf, but we want to maintain legacy behavior
   * for now.
   */
  record OneOf(List<AirbyteType> options) implements AirbyteType {

  }

  /**
   * Represents a {type: [a, b, ...]} schema. This is theoretically equivalent to {oneOf: [{type: a}, {type: b}, ...]} but legacy normalization only
   * handles the {type: [...]} schemas.
   * <p>
   * Eventually we should:
   * <ol>
   *   <li>Announce a breaking change to handle both oneOf styles the same</li>
   *   <li>Test against some number of API sources to verify that they won't break badly</li>
   *   <li>Update AirbyteType consumers to handle {@link OneOf} and LegacyOneOf identically</li>
   *   <li>Update {@link AirbyteType#fromJsonSchema(JsonNode)} to parse both styles into OneOf</li>
   *   <li>Delete this class</li>
   *  </ol>
   */
  record LegacyOneOf(List<AirbyteType> options) implements AirbyteType {

  }
}
