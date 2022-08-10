/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.google.common.collect.ImmutableMap;
import io.airbyte.db.jdbc.JdbcUtils;

public class MySqlSslFullCertificateSourceAcceptanceTest extends AbstractMySqlSslCertificateSourceAcceptanceTest {

  @Override
  public ImmutableMap getSslConfig() {
    return ImmutableMap.builder()
            .put(JdbcUtils.MODE_KEY, "verify_identity")
            .put("ca_certificate", certs.getCaCertificate())
            .put("client_certificate", certs.getClientCertificate())
            .put("client_key", certs.getClientKey())
            .put("client_key_password", PASSWORD)
            .build();
  }

}
