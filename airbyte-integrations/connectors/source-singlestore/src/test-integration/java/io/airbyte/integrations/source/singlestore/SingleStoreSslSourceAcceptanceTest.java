/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.singlestore.SingleStoreTestDatabase.BaseImage;
import io.airbyte.integrations.source.singlestore.SingleStoreTestDatabase.ContainerModifier;
import org.junit.jupiter.api.Order;

@Order(3)
public class SingleStoreSslSourceAcceptanceTest extends SingleStoreSourceAcceptanceTest {

  @Override
  protected SingleStoreTestDatabase createDatabase() {
    return SingleStoreTestDatabase.in(BaseImage.SINGLESTORE_DEV, ContainerModifier.CERT);
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder().withStandardReplication()
        .with(JdbcUtils.SSL_MODE_KEY, Jsons.jsonNode(
            ImmutableMap.of(JdbcUtils.MODE_KEY, "verify-ca", "ca_certificate",
                testdb.getCertificates().caCertificate())))
        .build();
  }

}
