/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

public class CdcPostgresSourceAcceptanceLegacyCtidTest extends CdcPostgresSourceAcceptanceTest {

  @Override
  protected String getServerImageName() {
    return "postgres:12-bullseye";
  }

}
