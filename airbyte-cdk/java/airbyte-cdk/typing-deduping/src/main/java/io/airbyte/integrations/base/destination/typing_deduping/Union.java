/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;

/**
 * Represents a {type: [a, b, ...]} schema. This is theoretically equivalent to {oneOf: [{type: a},
 * {type: b}, ...]} but legacy normalization only handles the {type: [...]} schemas.
 * <p>
 * Eventually we should:
 * <ol>
 * <li>Announce a breaking change to handle both oneOf styles the same</li>
 * <li>Test against some number of API sources to verify that they won't break badly</li>
 * <li>Update {@link AirbyteType#fromJsonSchema(JsonNode)} to parse both styles into
 * SupportedOneOf</li>
 * <li>Delete UnsupportedOneOf</li>
 * </ol>
 */
public record Union(List<AirbyteType> options) implements AirbyteType {

  /**
   * This is a hack to handle weird schemas like {type: [object, string]}. If a stream's top-level
   * schema looks like this, we still want to be able to extract the object properties (i.e. treat it
   * as though the string option didn't exist).
   *
   * @throws IllegalArgumentException if we cannot extract columns from this schema
   */
  public LinkedHashMap<String, AirbyteType> asColumns() {
    final long numObjectOptions = options.stream().filter(o -> o instanceof Struct).count();
    if (numObjectOptions > 1) {
      LOGGER.error("Can't extract columns from a schema with multiple object options");
      return new LinkedHashMap<>();
    }

    return (options.stream().filter(o -> o instanceof Struct).findFirst())
        .map(o -> ((Struct) o).properties())
        .orElseGet(() -> {
          LOGGER.error("Can't extract columns from a schema with no object options");
          return new LinkedHashMap<>();
        });
  }

  // Picks which type in a Union takes precedence
  public AirbyteType chooseType() {
    final Comparator<AirbyteType> comparator = Comparator.comparing(t -> {
      if (t instanceof Array) {
        return -2;
      } else if (t instanceof Struct) {
        return -1;
      } else if (t instanceof final AirbyteProtocolType p) {
        return List.of(AirbyteProtocolType.values()).indexOf(p);
      }
      return Integer.MAX_VALUE;
    });

    return options.stream().min(comparator).orElse(AirbyteProtocolType.UNKNOWN);
  }

}
