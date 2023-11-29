/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import org.junit.jupiter.api.Order;

@Order(2)
public class CdcPostgresSourceLegacyCtidTest extends CdcPostgresSourceTest {

  protected static String getServerImageName() {
    return "debezium/postgres:13-bullseye";
  }

}
