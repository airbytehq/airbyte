/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser.StreamConfig;
import java.util.Optional;

public interface SqlGenerator<DialectTableDefinition> {

  /**
   * In general, callers should not directly instantiate this class. Use
   * {@link #buildStreamId(String, String, String)} instead.
   * <p>
   * All names/namespaces are intended to be quoted, but do not explicitly contain quotes. For
   * example, finalName might be "foo bar"; the caller is required to wrap that in quotes before using
   * it in a query.
   *
   * @param finalNamespace the namespace where the final table will be created
   * @param finalName the name of the final table
   * @param rawNamespace the namespace where the raw table will be created (typically "airbyte")
   * @param rawName the name of the raw table (typically namespace_name, but may be different if there
   *        are collisions). There is no rawNamespace because we assume that we're writing raw tables
   *        to the airbyte namespace.
   */
  record StreamId(String finalNamespace, String finalName, String rawNamespace, String rawName, String originalNamespace, String originalName) {

    /**
     * Most databases/warehouses use a `schema.name` syntax to identify tables. This is a convenience
     * method to generate that syntax.
     */
    public String finalTableId(String quote) {
      return quote + finalNamespace + quote + "." + quote + finalName + quote;
    }

    public String finalTableId(String suffix, String quote) {
      return quote + finalNamespace + quote + "." + quote + finalName + suffix + quote;
    }

    public String rawTableId(String quote) {
      return quote + rawNamespace + quote + "." + quote + rawName + quote;
    }

    public String finalName(final String quote) {
      return quote + finalName + quote;
    }

    public String finalNamespace(final String quote) {
      return quote + finalNamespace + quote;
    }

  }

  /**
   * In general, callers should not directly instantiate this class. Use
   * {@link #buildColumnId(String)} instead.
   *
   * @param name the name of the column in the final table. Callers should prefer
   *        {@link #name(String)} when using the column in a query.
   * @param originalName the name of the field in the raw JSON blob
   * @param canonicalName the name of the field according to the destination. Used for deduping.
   *        Useful if a destination warehouse handles columns ignoring case, but preserves case in the
   *        table schema.
   */
  record ColumnId(String name, String originalName, String canonicalName) {

    public String name(final String quote) {
      return quote + name + quote;
    }

  }

  StreamId buildStreamId(String namespace, String name, String rawNamespaceOverride);

  ColumnId buildColumnId(String name);

  /**
   * Generate a SQL statement to create a fresh table to match the given stream.
   * <p>
   * The generated SQL may throw an exception if the table already exists. Callers should use
   * {@link #alterTable(StreamConfig, java.lang.Object)} if the table is known to exist.
   *
   * @param suffix A suffix to add to the stream name. Useful for full refresh overwrite syncs, where
   *        we write the entire sync to a temp table.
   */
  String createTable(final StreamConfig stream, final String suffix);

  /**
   * Generate a SQL statement to alter an existing table to match the given stream.
   * <p>
   * The operations may differ based on the existing table definition (BigQuery does not allow
   * altering a partitioning scheme and requires you to recreate+rename the table; snowflake only
   * allows altering some column types to certain other types, etc.).
   */
  String alterTable(final StreamConfig stream, DialectTableDefinition existingTable);

  /**
   * Generate a SQL statement to copy new data from the raw table into the final table.
   * <p>
   * Supports both incremental and one-shot loading. (maybe.)
   * <p>
   * Responsible for:
   * <ul>
   * <li>Pulling new raw records from a table (i.e. records with null _airbyte_loaded_at)</li>
   * <li>Extracting the JSON fields and casting to the appropriate types</li>
   * <li>Handling errors in those casts</li>
   * <li>Merging those typed records into an existing table</li>
   * <li>Updating the raw records with SET _airbyte_loaded_at = now()</li>
   * </ul>
   * <p>
   * Implementing classes are recommended to break this into smaller methods, which can be tested in
   * isolation. However, this interface only requires a single mega-method.
   *
   * @param finalSuffix the suffix of the final table to write to. If empty string, writes to the
   *        final table directly. Useful for full refresh overwrite syncs, where we write the entire
   *        sync to a temp table and then swap it into the final table at the end.
   */
  String updateTable(String finalSuffix, final StreamConfig stream);

  /**
   * Drop the previous final table, and rename the new final table to match the old final table.
   */
  Optional<String> overwriteFinalTable(String finalSuffix, StreamConfig stream);

}
