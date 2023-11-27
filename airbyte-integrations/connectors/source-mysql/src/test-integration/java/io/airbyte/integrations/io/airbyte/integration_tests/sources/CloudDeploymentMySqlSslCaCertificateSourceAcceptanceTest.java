/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.MySqlUtils;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.io.IOException;

public class CloudDeploymentMySqlSslCaCertificateSourceAcceptanceTest extends AbstractCloudDeploymentMySqlSslCertificateSourceAcceptanceTest {

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
