/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.google.common.collect.ImmutableMap;

public class PostgresSourceSSLFullCertificateAcceptanceTest extends AbstractPostgresSourceSSLCertificateAcceptanceTest {

  @Override
  public ImmutableMap getCertificateConfiguration() {
    return ImmutableMap.builder()
        .put("mode", "verify-ca")
        .put("ca_certificate", certs.getCaCertificate())
        .put("client_certificate", certs.getClientCertificate())
        .put("client_key", certs.getClientKey())
        .put("client_key_password", PASSWORD)
        .build();
  }

}
