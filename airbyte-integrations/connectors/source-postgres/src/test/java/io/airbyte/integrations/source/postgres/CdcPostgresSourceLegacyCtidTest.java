/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

public class CdcPostgresSourceLegacyCtidTest extends CdcPostgresSourceTest {

  protected static String getServerImageName() {
    return "debezium/postgres:13-bullseye";
  }

}
