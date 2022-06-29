/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.google.common.collect.ImmutableMap;

class CertificatesPostgresSourceSSLCaTest extends AbstractPostgresSourceSSLCertificatesTest {

  @Override
  public ImmutableMap getSSLCertificateConfig() {
    return ImmutableMap.builder()
        .put("mode", "verify-ca")
        .put("ca_certificate", certs.getLeft())
        .put("client_key_password", PASSWORD)
        .build();
  }

}
