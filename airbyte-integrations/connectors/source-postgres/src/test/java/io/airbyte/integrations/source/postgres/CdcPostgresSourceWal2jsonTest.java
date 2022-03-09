/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

class CdcPostgresSourceWal2jsonTest extends CdcPostgresSourceTest {

  @Override
  protected String getPluginName() {
    return "wal2json";
  }

}
