/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.util.List;

public class RedshiftDestinationHandler extends JdbcDestinationHandler {

  public RedshiftDestinationHandler(final String databaseName, final JdbcDatabase jdbcDatabase) {
    super(databaseName, jdbcDatabase);
  }

  @Override
  public boolean isFinalTableEmpty(final StreamId id) throws Exception {
    // Redshift doesn't have an information_schema.tables table, so we have to use SVV_TABLE_INFO.
    // From https://docs.aws.amazon.com/redshift/latest/dg/r_SVV_TABLE_INFO.html:
    // > The SVV_TABLE_INFO view doesn't return any information for empty tables.
    // So we just query for our specific table, and if we get no rows back,
    // then we assume the table is empty.
    // Note that because the column names are reserved words (table, schema, database),
    // we need to enquote them.
    final List<JsonNode> query = jdbcDatabase.queryJsons(
        """
        SELECT 1
        FROM SVV_TABLE_INFO
        WHERE "database" = ?
          AND "schema" = ?
          AND "table" = ?
        """,
        databaseName,
        id.finalNamespace(),
        id.finalName());
    return query.isEmpty();
  }

}
