/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import io.airbyte.cdk.testutils.PostgresTestDatabase.PostgresImage;

public class PostgresSourceAcceptanceLegacyCtidTest extends PostgresSourceAcceptanceTest {

  @Override
  protected PostgresImage getServerImage() {
    return PostgresImage.POSTGRES_12_BULLSEYE;
  }

}
