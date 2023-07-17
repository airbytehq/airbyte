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
 * @param finalName      the name of the final table
 * @param rawNamespace   the namespace where the raw table will be created (typically "airbyte")
 * @param rawName        the name of the raw table (typically namespace_name, but may be different if there
 *                       are collisions). There is no rawNamespace because we assume that we're writing raw tables
 *                       to the airbyte namespace.
 */
public record StreamId(String finalNamespace, String finalName, String rawNamespace, String rawName,
                       String originalNamespace, String originalName) {

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
