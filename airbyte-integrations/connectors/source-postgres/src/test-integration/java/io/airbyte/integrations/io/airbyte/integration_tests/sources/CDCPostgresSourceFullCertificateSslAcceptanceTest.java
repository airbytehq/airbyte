/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import java.util.Map;

public class CDCPostgresSourceFullCertificateSslAcceptanceTest extends AbstractCdcPostgresSourceSslAcceptanceTest {

  @Override
  public Map<Object, Object> getCertificateConfiguration() {
    final var certs = testdb.getCertificates();
    return ImmutableMap.builder()
        .put("mode", "verify-ca")
        .put("ca_certificate", certs.caCertificate())
        .put("client_certificate", certs.clientCertificate())
        .put("client_key", certs.clientKey())
        .put("client_key_password", PASSWORD)
        .build();
  }

  @Override
  protected BaseImage getServerImage() {
    return BaseImage.POSTGRES_16;
  }

}
