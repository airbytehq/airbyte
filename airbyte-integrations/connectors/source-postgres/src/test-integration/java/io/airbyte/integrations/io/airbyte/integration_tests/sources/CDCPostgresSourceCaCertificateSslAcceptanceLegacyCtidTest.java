/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import io.airbyte.integrations.source.postgres.PostgresTestDatabase.PostgresBaseImage;

public class CDCPostgresSourceCaCertificateSslAcceptanceLegacyCtidTest extends CDCPostgresSourceCaCertificateSslAcceptanceTest {

  @Override
  protected PostgresBaseImage getServerImage() {
    return PostgresBaseImage.POSTGRES_12_BULLSEYE;
  }

}
