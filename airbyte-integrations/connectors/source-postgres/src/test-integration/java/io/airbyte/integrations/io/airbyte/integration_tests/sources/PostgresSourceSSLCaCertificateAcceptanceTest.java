/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.google.common.collect.ImmutableMap;
import java.util.Map;

public class PostgresSourceSSLCaCertificateAcceptanceTest extends AbstractPostgresSourceSSLCertificateAcceptanceTest {

  @Override
  public Map<Object, Object> getCertificateConfiguration() {
    return ImmutableMap.builder()
        .put("mode", "verify-ca")
        .put("ca_certificate", testdb.getCertificates().caCertificate())
        .put("client_key_password", PASSWORD)
        .build();
  }

}
