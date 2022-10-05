package io.airbyte.integrations.destination.mariadb_columnstore;

import static io.airbyte.integrations.destination.mariadb_columnstore.MariaDbColumnstoreSslUtils.VERIFY_CA;

public class MariaDbDestinationSSLVerifyCaAcceptanceTest extends AbstractMariaDbDestinationSSLAcceptanceTest{

  @Override
  protected String getSslMode() {
    return VERIFY_CA;
  }
}
