package io.airbyte.integrations.destination.bigquery.typing_deduping;

import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.LinkedHashMap;

// TODO would be cool if we could centralize the name sanitizing logic (i.e. quoting+espacing)
// right now it's on the sqlgenerator+destinationinteractor to do it everywhere
public interface SqlGenerator<DialectTableDefinition> {

  /**
   * Generate a SQL statement to create a fresh table to match the given stream.
   * <p>
   * This method may throw an exception if the table already exists. Callers should use
   * {@link #alterTable(ConfiguredAirbyteStream, LinkedHashMap, Object)} if the table is known to exist.
   */
  String createTable(ConfiguredAirbyteStream stream, LinkedHashMap<String, AirbyteType> types);

  /**
   * Generate a SQL statement to alter the table definition to match the given stream.
   * <p>
   * The operations may differ based on the existing table definition (e.g. BigQuery does not allow altering a partitioning scheme, and requires you
   * to drop+recreate the table).
   */
  String alterTable(ConfiguredAirbyteStream stream,
                    LinkedHashMap<String, AirbyteType> types,
                    DialectTableDefinition existingTable);

  /**
   * Generate a SQL statement to copy new data from the raw table into the final table.
   */
  // TODO maybe this should be broken into smaller methods, idk
  String updateTable(ConfiguredAirbyteStream stream, LinkedHashMap<String, AirbyteType> types);

}
