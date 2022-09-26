/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.alloydb;

import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.postgres.PostgresSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AlloyDbSource {

  private static final Logger LOGGER = LoggerFactory.getLogger(AlloyDbSource.class);

  /**
   * AlloyDB for PostgreSQL is a fully managed PostgreSQL-compatible database service. So the
   * source-postgres connector is used under the hood. For more details please check the
   * https://cloud.google.com/alloydb
   */
  public static void main(final String[] args) throws Exception {
    final Source source = PostgresSource.sshWrappedSource();
    LOGGER.info("starting source: AlloyDB for {}", PostgresSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: AlloyDB for {}", PostgresSource.class);
  }

}
