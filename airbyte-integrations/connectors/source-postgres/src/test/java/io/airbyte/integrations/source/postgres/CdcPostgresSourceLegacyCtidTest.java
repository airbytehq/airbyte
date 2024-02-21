/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Order;

@Order(2)
public class CdcPostgresSourceLegacyCtidTest extends CdcPostgresSourceTest {

  @Override
  protected void setBaseImage() {
    this.postgresImage = BaseImage.POSTGRES_12;
  }

  @Override
  @Disabled("https://github.com/airbytehq/airbyte/issues/35267")
  public void newTableSnapshotTest() {

  }

  @Override
  @Disabled("https://github.com/airbytehq/airbyte/issues/35267")
  public void syncShouldIncrementLSN() {

  }

}
