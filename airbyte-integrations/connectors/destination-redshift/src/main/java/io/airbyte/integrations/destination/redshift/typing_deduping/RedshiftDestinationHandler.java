/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class RedshiftDestinationHandler extends JdbcDestinationHandler {

  public RedshiftDestinationHandler(final String databaseName, final JdbcDatabase jdbcDatabase) {
    super(databaseName, jdbcDatabase);
  }

  @Override
  public void execute(final Sql sql) throws Exception {
    final List<List<String>> transactions = sql.transactions();
    final UUID queryId = UUID.randomUUID();
    for (final List<String> transaction : transactions) {
      final UUID transactionId = UUID.randomUUID();
      log.info("Executing sql {}-{}: {}", queryId, transactionId, String.join("\n", transaction));
      final long startTime = System.currentTimeMillis();

      try {
        // Original list is immutable, so copying it into a different list.
        final List<String> modifiedStatements = new ArrayList<>();
        // This is required for Redshift to retrieve Json path query with upper case characters, even after
        // specifying quotes.
        // see https://github.com/airbytehq/airbyte/issues/33900
        modifiedStatements.add("SET enable_case_sensitive_identifier to TRUE;\n");
        modifiedStatements.addAll(transaction);
        jdbcDatabase.executeWithinTransaction(modifiedStatements);
      } catch (final SQLException e) {
        log.error("Sql {}-{} failed", queryId, transactionId, e);
        throw e;
      }

      log.info("Sql {}-{} completed in {} ms", queryId, transactionId, System.currentTimeMillis() - startTime);
    }
  }

  /**
   * Issuing a select 1 limit 1 query can be expensive, so relying on SVV_TABLE_INFO system table.
   * EXPLAIN of the select 1 from table limit 1 query: (seq scan and then limit is applied, read from
   * bottom to top) XN Lim it (co st=0. 0 .0.01 rows=1 width=0) -> XN Seq Scan on _airbyte_raw_ users
   * (cost=0.00..1000.00 rows=100000 width=0)
   *
   * @param id
   * @return
   * @throws Exception
   */
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
