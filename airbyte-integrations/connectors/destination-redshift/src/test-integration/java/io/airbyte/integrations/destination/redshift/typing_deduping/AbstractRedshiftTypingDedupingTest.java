/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.destination.redshift.RedshiftInsertDestination;
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGeneratorIntegrationTest.RedshiftSourceOperations;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.conf.Settings;
import org.jooq.impl.DSL;

public abstract class AbstractRedshiftTypingDedupingTest extends JdbcTypingDedupingTest {

  @Override
  protected String getImageName() {
    return "airbyte/destination-redshift:dev";
  }

  @Override
  protected DataSource getDataSource(final JsonNode config) {
    return new RedshiftInsertDestination().getDataSource(config);
  }

  @Override
  protected JdbcCompatibleSourceOperations<?> getSourceOperations() {
    return new RedshiftSourceOperations();
  }

  @Override
  protected SqlGenerator<?> getSqlGenerator() {
    return new RedshiftSqlGenerator(new RedshiftSQLNameTransformer()) {

      // Override only for tests to print formatted SQL. The actual implementation should use unformatted
      // to save bytes.
      @Override
      protected DSLContext getDslContext() {
        return DSL.using(getDialect(), new Settings().withRenderFormatted(true));
      }

    };
  }

}
