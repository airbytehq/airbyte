/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.ContainerModifier;
import org.junit.jupiter.api.Order;

@Order(2)
public class CdcPostgresSourceLegacyCtidTest extends CdcPostgresSourceTest {

  @Override
  protected PostgresTestDatabase createTestDatabase() {
    return PostgresTestDatabase.in(BaseImage.POSTGRES_13, ContainerModifier.CONF).withReplicationSlot();
  }

  @Override
  protected int getPostgresVersion() {
    return 13;
  }

}
