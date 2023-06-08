package io.airbyte.integrations.destination.bigquery.typing_deduping;

import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;
import java.util.UUID;

public interface SqlGenerator<DialectTableDefinition, DialectType> {

  /**
   * In general, callers should not directly instantiate this class. Use {@link #quoteStreamId(String, String)} instead.
   *
   * @param namespace         the namespace where the final table will be created
   * @param name              the name of the final table
   * @param rawName           the name of the raw table (typically namespace_name, but may be different if there are collisions). There is no
   *                          rawNamespace because we assume that we're writing raw tables to the airbyte namespace.
   * @param originalNamespace the namespace of the stream according to the Airbyte catalog
   * @param originalName      the name of the stream according to the Airbyte catalog
   */
  record QuotedStreamId(String namespace, String name, String rawName, String originalNamespace, String originalName) {

    /**
     * Most databases/warehouses use a `schema.name` syntax to identify tables. This is a convenience method to generate that syntax.
     */
    public String finalTableId() {
      return namespace + "." + name;
    }
  }

  /**
   * In general, callers should not directly instantiate this class. Use {@link #quoteColumnId(String)} instead.
   *
   * @param name         the name of the column in the final table
   * @param originalName the name of the field in the raw JSON blob
   */
  record QuotedColumnId(String name, String originalName) {

  }

  QuotedStreamId quoteStreamId(String namespace, String name);

  QuotedColumnId quoteColumnId(String name);

  DialectType toDialectType(AirbyteType type);

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
   * </ul>
   */
  // TODO maybe this should be broken into smaller methods, idk
  // TODO this probably needs source+target table names
  String updateTable(final StreamConfig<DialectType> stream);

  /**
   * Delete records from the final table with a non-null _ab_cdc_deleted_at column.
   */
  String executeCdcDeletions(final StreamConfig<DialectType> stream);

  /**
   * Generate a SQL statement to delete records from the final table that were not emitted in the current sync.
   * <p>
   * Useful for the full-refresh case, where we need to delete records that from the previous sync and which weren't re-emitted in the current sync.
   */
  String deletePreviousSyncRecords(StreamConfig<DialectType> stream, UUID syncId);

}
