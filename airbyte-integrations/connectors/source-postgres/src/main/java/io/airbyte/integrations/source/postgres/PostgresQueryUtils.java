/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

/**
 * Utility class to define constants related to querying postgres
 */
public class PostgresQueryUtils {

  public static final String NULL_CURSOR_VALUE_WITH_SCHEMA_QUERY =
      """
        SELECT
          (EXISTS (SELECT FROM information_schema.columns WHERE table_schema = '%s' AND table_name = '%s' AND is_nullable = 'YES' AND column_name = '%s'))
        AND
          (EXISTS (SELECT from \"%s\".\"%s\" where \"%s\" IS NULL LIMIT 1)) AS %s
      """;
  public static final String NULL_CURSOR_VALUE_NO_SCHEMA_QUERY =
      """
      SELECT
        (EXISTS (SELECT FROM information_schema.columns WHERE table_name = '%s' AND is_nullable = 'YES' AND column_name = '%s'))
      AND
        (EXISTS (SELECT from \"%s\" where \"%s\" IS NULL LIMIT 1)) AS %s
      """;

  public static final String TABLE_ESTIMATE_QUERY =
      """
            SELECT (select reltuples::int8 as count from pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace where nspname='%s' AND relname='%s') AS %s,
            pg_relation_size('%s') AS %s;
      """;

  public static final String ROW_COUNT_RESULT_COL = "rowcount";

  public static final String TOTAL_BYTES_RESULT_COL = "totalbytes";

}
