package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Object;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.UnsupportedOneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Primitive;
import java.util.LinkedHashMap;
import java.util.List;

public sealed interface AirbyteType permits Array, OneOf, Object, UnsupportedOneOf, Primitive {

  /**
   * The most common call pattern is probably to use this method on the stream schema, verify that it's an {@link Object} schema, and then call
   * {@link Object#properties()} to get the columns.
   * <p>
   * If the top-level schema is not an object, then we can't really do anything with it, and should probably fail the sync.
   * <p>
   * TODO legacy code: handle weird schemas with top-level {type: [object, ...]}
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
   * This is purely a legacy type that we should eventually delete. See also {@link OneOf}.
   */
  record UnsupportedOneOf(List<AirbyteType> options) implements AirbyteType {

  }

  /**
   * Represents a {type: [a, b, ...]} schema. This is theoretically equivalent to {oneOf: [{type: a}, {type: b}, ...]} but legacy normalization only
   * handles the {type: [...]} schemas.
   * <p>
   * Eventually we should:
   * <ol>
   *   <li>Announce a breaking change to handle both oneOf styles the same</li>
   *   <li>Test against some number of API sources to verify that they won't break badly</li>
   *   <li>Update {@link AirbyteType#fromJsonSchema(JsonNode)} to parse both styles into SupportedOneOf</li>
   *   <li>Delete UnsupportedOneOf</li>
   *  </ol>
   */
  record OneOf(List<AirbyteType> options) implements AirbyteType {

    /**
     * This is a hack to handle weird schemas like {type: [object, string]}. If a stream's top-level schema looks like this, we still want to be able
     * to extract the object properties (i.e. treat it as though the string option didn't exist).
     *
     * @throws IllegalArgumentException if we cannot extract columns from this schema
     */
    public LinkedHashMap<String, AirbyteType> asColumns() {
      final long numObjectOptions = options.stream().filter(o -> o instanceof Object).count();
      if (numObjectOptions > 1) {
        throw new IllegalArgumentException("Can't extract columns from a schema with multiple object options");
      }

      return (options.stream().filter(o -> o instanceof Object).findFirst())
          .map(o -> ((Object) o).properties())
          .orElseThrow(() -> new IllegalArgumentException("Can't extract columns from a schema with no object options"));
    }
  }
}
