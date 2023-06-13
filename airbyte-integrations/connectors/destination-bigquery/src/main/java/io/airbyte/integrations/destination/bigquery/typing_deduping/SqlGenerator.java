package io.airbyte.integrations.destination.bigquery.typing_deduping;

import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.ParsedType;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;

public interface SqlGenerator<DialectTableDefinition, DialectType> {

  /**
   * In general, callers should not directly instantiate this class. Use {@link #quoteStreamId(String, String)} instead.
   *
   * @param finalNamespace    the namespace where the final table will be created
   * @param finalName         the name of the final table
   * @param rawNamespace      the namespace where the raw table will be created (typically "airbyte")
   * @param rawName           the name of the raw table (typically namespace_name, but may be different if there are collisions). There is no
   *                          rawNamespace because we assume that we're writing raw tables to the airbyte namespace.
   */
  record QuotedStreamId(String finalNamespace, String finalName, String rawNamespace, String rawName, String originalNamespace, String originalName) {

    /**
     * Most databases/warehouses use a `schema.name` syntax to identify tables. This is a convenience method to generate that syntax.
     */
    public String finalTableId() {
      return finalNamespace + "." + finalName;
    }

    public String finalTableId(String suffix) {
      // TODO this won't work if the finalName is quoted, e.g. "`foo bar`". In that case we need to unquote, add the suffix, and requote.
      return finalNamespace + "." + finalName + suffix;
    }

    public String rawTableId() {
      return rawNamespace + "." + rawName;
    }
  }

  /**
   * In general, callers should not directly instantiate this class. Use {@link #quoteColumnId(String)} instead.
   *
   * @param name          the name of the column in the final table. Usable directly in a SQL query. For example, "`foo`" or "foo".
   * @param originalName  the name of the field in the raw JSON blob
   * @param canonicalName the name of the field according to the destination. Used for deduping. Useful if a destination warehouse handles columns
   *                      ignoring case, but preserves case in the table schema.
   */
  record QuotedColumnId(String name, String originalName, String canonicalName) {

  }

  QuotedStreamId quoteStreamId(String namespace, String name);

  QuotedColumnId quoteColumnId(String name);

  ParsedType<DialectType> toDialectType(AirbyteType type);

  /**
   * Generate a SQL statement to create a fresh table to match the given stream.
   * <p>
   * The generated SQL may throw an exception if the table already exists. Callers should use {@link #alterTable(StreamConfig, java.lang.Object)} if
   * the table is known to exist.
   */
  String createTable(final StreamConfig<DialectType> stream);

  /**
   * Generate a SQL statement to alter an existing table to match the given stream.
   * <p>
   * The operations may differ based on the existing table definition (BigQuery does not allow altering a partitioning scheme and requires you to
   * recreate+rename the table; snowflake only allows altering some column types to certain other types, etc.).
   */
  String alterTable(final StreamConfig<DialectType> stream, DialectTableDefinition existingTable);

  /**
   * Generate a SQL statement to copy new data from the raw table into the final table.
   * <p>
   * Supports both incremental and one-shot loading. (maybe.)
   * <p>
   * Responsible for:
   * <ul>
   *   <li>Pulling new raw records from a table (i.e. records with null _airbyte_loaded_at)</li>
   *   <li>Extracting the JSON fields and casting to the appropriate types</li>
   *   <li>Handling errors in those casts</li>
   *   <li>Merging those typed records into an existing table</li>
   *   <li>Updating the raw records with SET _airbyte_loaded_at = now()</li>
   * </ul>
   *
   * @param finalSuffix the suffix of the final table to write to. If empty string, writes to the final table directly. Useful for full refresh
   *                    overwrite syncs, where we write the entire sync to a temp table and then swap it into the final table at the end.
   */
  // TODO maybe this should be broken into smaller methods, idk
  String updateTable(String finalSuffix, final StreamConfig<DialectType> stream);

  /**
   * Drop the previous final table, and rename the new final table to match the old final table.
   */
  String overwriteFinalTable(String finalSuffix, StreamConfig<DialectType> stream);

}
