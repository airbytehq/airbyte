/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.AirbyteProtocolType.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.TextNode;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Union;
import java.util.Comparator;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteTypeUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteTypeUtils.class);

  protected static boolean nodeMatches(final JsonNode node, final String value) {
    if (node == null || !node.isTextual()) {
      return false;
    }
    return node.equals(TextNode.valueOf(value));
  }

  // Extracts the appropriate protocol type from the representative JSON
  protected static AirbyteType getAirbyteProtocolType(final JsonNode node) {
    // JSON could be a string (ex: "number")
    if (node.isTextual()) {
      return matches(node.asText());
    }

    // or, JSON could be a node with fields
    final JsonNode propertyType = node.get("type");
    final JsonNode airbyteType = node.get("airbyte_type");
    final JsonNode format = node.get("format");

    if (nodeMatches(propertyType, "boolean")) {
      return BOOLEAN;
    } else if (nodeMatches(propertyType, "integer")) {
      return INTEGER;
    } else if (nodeMatches(propertyType, "number")) {
      return nodeMatches(airbyteType, "integer") ? INTEGER : NUMBER;
    } else if (nodeMatches(propertyType, "string")) {
      if (nodeMatches(format, "date")) {
        return DATE;
      } else if (nodeMatches(format, "time")) {
        if (nodeMatches(airbyteType, "time_without_timezone")) {
          return TIME_WITHOUT_TIMEZONE;
        } else if (nodeMatches(airbyteType, "time_with_timezone")) {
          return TIME_WITH_TIMEZONE;
        }
      } else if (nodeMatches(format, "date-time")) {
        if (nodeMatches(airbyteType, "timestamp_without_timezone")) {
          return TIMESTAMP_WITHOUT_TIMEZONE;
        } else if (airbyteType == null || nodeMatches(airbyteType, "timestamp_with_timezone")) {
          return TIMESTAMP_WITH_TIMEZONE;
        }
      } else {
        return STRING;
      }
    }

    return UNKNOWN;
  }

  // Picks which type in a Union takes precedence
  public static AirbyteType chooseUnionType(final Union u) {
    final Comparator<AirbyteType> comparator = Comparator.comparing(t ->
        {
          if (t instanceof Array) {
            return -2;
          } else if (t instanceof Struct) {
            return -1;
          } else if (t instanceof final AirbyteProtocolType p) {
            return List.of(AirbyteProtocolType.values()).indexOf(p);
          }
          return Integer.MAX_VALUE;
        }
    );

    return u.options().stream().min(comparator).orElse(UNKNOWN);
  }

}
