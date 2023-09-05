/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.google.common.collect.ImmutableMap;
import io.airbyte.db.MySqlUtils;
import io.airbyte.db.jdbc.JdbcUtils;
import java.io.IOException;
import java.nio.file.Path;

public class MySqlSslCaCertificateSourceAcceptanceTest extends MySqlSourceAcceptanceTest {

  public Path getConfigFilePath() {
    return Path.of("secrets/mysql-ssl-ca-certificate-source-acceptance-test-config.json");
  }
}
