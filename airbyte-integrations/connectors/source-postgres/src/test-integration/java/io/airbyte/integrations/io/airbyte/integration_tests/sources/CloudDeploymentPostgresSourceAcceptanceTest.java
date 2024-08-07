/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.ContainerModifier;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;

public class CloudDeploymentPostgresSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private static final String SCHEMA_NAME = "public";

  private PostgresTestDatabase testdb;

  protected static final String PASSWORD = "Passw0rd";

  @Override
  protected FeatureFlags featureFlags() {
    return FeatureFlagsWrapper.overridingDeploymentMode(
        super.featureFlags(),
        AdaptiveSourceRunner.CLOUD_MODE);
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    testdb = PostgresTestDatabase.in(BaseImage.POSTGRES_16, ContainerModifier.CERT);
    testdb.query(ctx -> {
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
      ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
      ctx.fetch("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
      return null;
    });
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-postgres:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return SshHelpers.injectSshIntoSpec(
        Jsons.deserialize(MoreResources.readResource("expected_cloud_deployment_spec.json"), ConnectorSpecification.class),
        Optional.of("security"));
  }

  @Override
  protected JsonNode getConfig() {
    final var certs = testdb.getCertificates();
    return testdb.integrationTestConfigBuilder()
        .withStandardReplication()
        .withSsl(ImmutableMap.builder()
            .put("mode", "verify-ca")
            .put("ca_certificate", certs.caCertificate())
            .put("client_certificate", certs.clientCertificate())
            .put("client_key", certs.clientKey())
            .put("client_key_password", PASSWORD)
            .build())
        .build();
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME, SCHEMA_NAME,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2, SCHEMA_NAME,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withSourceDefinedPrimaryKey(List.of(List.of("id"))))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
