/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.typing_deduping;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;

public class JdbcTyperDeduper extends DefaultTyperDeduper<JdbcDatabase> implements TyperDeduper {

  public JdbcTyperDeduper(
                          final SqlGenerator<JdbcDatabase> sqlGenerator,
                          final DestinationHandler<JdbcDatabase> destinationHandler,
                          final ParsedCatalog parsedCatalog) {
    super(sqlGenerator, destinationHandler, parsedCatalog);
  }

  @Override
  public void prepareFinalTables() throws Exception {
    super.prepareFinalTables();
  }

  @Override
  public void typeAndDedupe(final String originalNamespace, final String originalName) throws Exception {
    super.typeAndDedupe(originalNamespace, originalName);
  }

  @Override
  public void commitFinalTables() throws Exception {
    super.commitFinalTables();
  }

}
