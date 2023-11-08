/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationV1V2Migrator;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.V2TableMigrator;

public class JdbcTyperDeduper extends DefaultTyperDeduper<JdbcDatabase> implements TyperDeduper {

  public JdbcTyperDeduper(final SqlGenerator<JdbcDatabase> sqlGenerator,
                          final DestinationHandler<JdbcDatabase> destinationHandler,
                          final ParsedCatalog parsedCatalog,
                          final DestinationV1V2Migrator<JdbcDatabase> v1V2Migrator,
                          final V2TableMigrator v2TableMigrator,
                          final int defaultThreadCount) {
    super(sqlGenerator, destinationHandler, parsedCatalog, v1V2Migrator, v2TableMigrator, defaultThreadCount);
  }

  @Override
  public void prepareTables() throws Exception {
    super.prepareTables();
  }

  @Override
  public void typeAndDedupe(final String originalNamespace, final String originalName, final boolean mustRun) throws Exception {
    super.typeAndDedupe(originalNamespace, originalName, mustRun);
  }

  @Override
  public void commitFinalTables() throws Exception {
    super.commitFinalTables();
  }

}
