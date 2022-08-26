/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.google.common.collect.ImmutableMap;
import io.airbyte.db.MySqlUtils;
import io.airbyte.db.jdbc.JdbcUtils;
import java.io.IOException;

public class MySqlSslCaCertificateSourceAcceptanceTest extends AbstractMySqlSslCertificateSourceAcceptanceTest {

  @Override
  public MySqlUtils.Certificate getCertificates() throws IOException, InterruptedException {
    return MySqlUtils.getCertificate(container, false);
  }

  @Override
  public ImmutableMap getSslConfig() {
    return ImmutableMap.builder()
        .put(JdbcUtils.MODE_KEY, "verify_ca")
        .put("ca_certificate", certs.getCaCertificate())
        .put("client_key_password", PASSWORD)
        .build();
  }

}
