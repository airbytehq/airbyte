/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

/**
 * In general, callers should not directly instantiate this class. Use
 * {@link SqlGenerator#buildStreamId(String, String, String)} instead.
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
public record StreamId(String finalNamespace,
                       String finalName,
                       String rawNamespace,
                       String rawName,
                       String originalNamespace,
                       String originalName) {

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

  /**
   * Build the raw table name as namespace + (delimiter) + name. For example, given a stream with
   * namespace "public__ab" and name "abab_users", we will end up with raw table name
   * "public__ab_ab___ab_abab_users".
   * <p>
   * This logic is intended to solve two problems:
   * <ul>
   * <li>The raw table name should be unambiguously parsable into the namespace/name.</li>
   * <li>It must be impossible for two different streams to generate the same raw table name.</li>
   * </ul>
   * The generated delimiter is guaranteed to not be present in the namespace or name, so it
   * accomplishes both of these goals.
   */
  public static String concatenateRawTableName(String namespace, String name) {
    String plainConcat = namespace + name;
    int longestUnderscoreRun = 0;
    for (int i = 0; i < plainConcat.length(); i++) {
      // If we've found an underscore, count the number of consecutive underscores
      int underscoreRun = 0;
      while (i < plainConcat.length() && plainConcat.charAt(i) == '_') {
        underscoreRun++;
        i++;
      }
      longestUnderscoreRun = Math.max(longestUnderscoreRun, underscoreRun);
    }

    return namespace + "_ab" + "_".repeat(longestUnderscoreRun + 1) + "ab_" + name;
  }

}
