package io.airbyte.integrations.destination.bigquery.typing_deduping;

import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.LinkedHashMap;

/**
 * A destination-agnostic class that converts stream JSON schemas into their underlying Airbyte types.
 */
public class CatalogParser {

  public LinkedHashMap<String, AirbyteType> getTypes(ConfiguredAirbyteStream stream) {
    // TODO
    return null;
  }

}
