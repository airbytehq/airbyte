/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public interface SqlGenerator<DialectTableDefinition> {

  String SOFT_RESET_SUFFIX = "_ab_soft_reset";

  StreamId buildStreamId(String namespace, String name, String rawNamespaceOverride);

  ColumnId buildColumnId(String name);

  /**
   * Generate a SQL statement to create a fresh table to match the given stream.
   * <p>
   * The generated SQL should throw an exception if the table already exists and {@code force} is
   * false. Callers should use
   * {@link #existingSchemaMatchesStreamConfig(StreamConfig, java.lang.Object)} if the table is known
   * to exist, and potentially {@link #softReset(StreamConfig)}.
   *
   * @param suffix A suffix to add to the stream name. Useful for full refresh overwrite syncs, where
   *        we write the entire sync to a temp table.
   * @param force If true, will overwrite an existing table. If false, will throw an exception if the
   *        table already exists. If you're passing a non-empty prefix, you likely want to set this to
   *        true.
   */
  String createTable(final StreamConfig stream, final String suffix, boolean force);

  /**
   * Check the final table's schema and compare it to what the stream config would generate.
   *
   * @param stream the stream/stable in question
   * @param existingTable the existing table mapped to the stream
   * @return whether the existing table matches the expected schema
   */
  boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final DialectTableDefinition existingTable);

  /**
   * SQL Statement which will rebuild the final table using the raw table data. Should not cause data
   * downtime. Typically this will resemble "create tmp_table; update raw_table set loaded_at=null;
   * (t+d into tmp table); (overwrite final table from tmp table);"
   *
   * @param stream the stream to rebuild
   */
  String softReset(final StreamConfig stream);

  /**
   * Generate a SQL statement to copy new data from the raw table into the final table.
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
  String updateTable(final StreamConfig stream, String finalSuffix);

  /**
   * Drop the previous final table, and rename the new final table to match the old final table.
   * <p>
   * This method may assume that the stream is an OVERWRITE stream, and that the final suffix is
   * non-empty. Callers are responsible for verifying those are true.
   */
  String overwriteFinalTable(StreamId stream, String finalSuffix);

  /**
   * Creates a sql query which will create a v2 raw table from the v1 raw table, then performs a soft
   * reset.
   *
   * @param streamId the stream to migrate
   * @param namespace
   * @param tableName
   * @return a string containing the necessary sql to migrate
   */
  String migrateFromV1toV2(StreamId streamId, String namespace, String tableName);

}
