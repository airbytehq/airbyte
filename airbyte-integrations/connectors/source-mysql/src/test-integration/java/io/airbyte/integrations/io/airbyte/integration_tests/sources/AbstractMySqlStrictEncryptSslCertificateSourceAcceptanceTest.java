/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.MySqlUtils;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.MySQLContainer;

public abstract class AbstractMySqlStrictEncryptSslCertificateSourceAcceptanceTest extends AbstractMySqlSslCertificateSourceAcceptanceTest {

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    super.setupEnvironment(environment);
    environmentVariables.set(EnvVariableFeatureFlags.DEPLOYMENT_MODE, "CLOUD");
  }


}
