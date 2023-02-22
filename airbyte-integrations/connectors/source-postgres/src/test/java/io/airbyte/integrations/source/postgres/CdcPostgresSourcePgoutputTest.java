/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

class CdcPostgresSourcePgoutputTest extends CdcPostgresSourceTest {

  @Override
  protected String getPluginName() {
    return "pgoutput";
  }

}
