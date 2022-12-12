/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.alloydb;

import static io.airbyte.integrations.source.relationaldb.state.StateManager.LOGGER;

import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.postgres.PostgresSourceStrictEncrypt;

public class AlloyDbStrictEncryptSource {

  public static void main(String[] args) throws Exception {
    final Source source = new PostgresSourceStrictEncrypt();
    LOGGER.info("starting source: {}", PostgresSourceStrictEncrypt.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSourceStrictEncrypt.class);
  }

}
