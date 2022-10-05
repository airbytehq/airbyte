package io.airbyte.integrations.destination.mariadb_columnstore;

import static io.airbyte.integrations.destination.mariadb_columnstore.MariaDbColumnstoreSslUtils.VERIFY_FULL;

public class MariaDbDestinationSSLVerifyFullAcceptanceTest extends AbstractMariaDbDestinationSSLAcceptanceTest {

  @Override
  protected String getSslMode() {
    return VERIFY_FULL;
  }
}
