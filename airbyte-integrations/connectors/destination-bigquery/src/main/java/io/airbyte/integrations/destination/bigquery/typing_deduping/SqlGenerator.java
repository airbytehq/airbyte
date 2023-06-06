package io.airbyte.integrations.destination.bigquery.typing_deduping;

import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.LinkedHashMap;

public interface SqlGenerator<DialectTableDefinition> {

  /**
   * Represents a table identifier that has been sanitized for use in SQL (i.e. quoted/escaped). In general, callers should not instantiate this class
   * directly. Instead, use {@link #sanitizeNames(String, String)}.
   * <p>
   * Only use the constructor if you already have sanitized names or are writing a test.
   */
  // TODO - is this a reasonable interface? maybe it's on the sqlgenerator implementation to do this as needed?
  // We need to be able to reference both namespace.name and namespace._airbyte_raw_name
  // alternatively, should we extend this to the column names?
  record SanitizedTableIdentifier(String namespace, String name) {

  }

  SanitizedTableIdentifier sanitizeNames(String namespace, String name);

  /**
   * Generate a SQL statement to create a fresh table to match the given stream.
   * <p>
   * This method may throw an exception if the table already exists. Callers should use
   * {@link #alterTable(SanitizedTableIdentifier, ConfiguredAirbyteStream, LinkedHashMap, Object)} if the table is known to exist.
   */
  String createTable(SanitizedTableIdentifier id, ConfiguredAirbyteStream stream, LinkedHashMap<String, AirbyteType> types);

  /**
   * Generate a SQL statement to alter the table definition to match the given stream.
   * <p>
   * The operations may differ based on the existing table definition (e.g. BigQuery does not allow altering a partitioning scheme, and requires you
   * to drop+recreate the table).
   */
  String alterTable(SanitizedTableIdentifier id,
                    ConfiguredAirbyteStream stream,
                    LinkedHashMap<String, AirbyteType> types,
                    DialectTableDefinition existingTable);

  /**
   * Generate a SQL statement to copy new data from the raw table into the final table.
   */
  // TODO maybe this should be broken into smaller methods, idk
  String updateTable(SanitizedTableIdentifier id, ConfiguredAirbyteStream stream, LinkedHashMap<String, AirbyteType> types);

}
