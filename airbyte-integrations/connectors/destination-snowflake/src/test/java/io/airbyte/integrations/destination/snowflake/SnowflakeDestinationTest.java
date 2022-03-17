/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.params.provider.Arguments.arguments;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.snowflake.SnowflakeDestination.DestinationType;
import io.airbyte.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.SQLException;
import java.time.Instant;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

public class SnowflakeDestinationTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  @Test
  @DisplayName("When given S3 credentials should use COPY")
  public void useS3CopyStrategyTest() {
    final var stubLoadingMethod = mapper.createObjectNode();
    stubLoadingMethod.put("s3_bucket_name", "fake-bucket");
    stubLoadingMethod.put("access_key_id", "test");
    stubLoadingMethod.put("secret_access_key", "test key");

    final var stubConfig = mapper.createObjectNode();
    stubConfig.set("loading_method", stubLoadingMethod);

    assertTrue(SnowflakeDestinationResolver.isS3Copy(stubConfig));
  }

  @Test
  @DisplayName("When given GCS credentials should use COPY")
  public void useGcsCopyStrategyTest() {
    final var stubLoadingMethod = mapper.createObjectNode();
    stubLoadingMethod.put("project_id", "my-project");
    stubLoadingMethod.put("bucket_name", "my-bucket");
    stubLoadingMethod.put("credentials_json", "hunter2");

    final var stubConfig = mapper.createObjectNode();
    stubConfig.set("loading_method", stubLoadingMethod);

    assertTrue(SnowflakeDestinationResolver.isGcsCopy(stubConfig));
  }

  @Test
  @DisplayName("When not given S3 credentials should use INSERT")
  public void useInsertStrategyTest() {
    final var stubLoadingMethod = mapper.createObjectNode();
    final var stubConfig = mapper.createObjectNode();
    stubConfig.set("loading_method", stubLoadingMethod);
    assertFalse(SnowflakeDestinationResolver.isS3Copy(stubConfig));
  }

  @Test
  public void testCleanupStageOnFailure() throws Exception {

    final JdbcDatabase mockDb = mock(JdbcDatabase.class);
    final SnowflakeInternalStagingSqlOperations sqlOperations = mock(SnowflakeInternalStagingSqlOperations.class);
    when(sqlOperations.getStageName(anyString(), anyString())).thenReturn("stage_name");
    when(sqlOperations.getStagingPath(anyString(), anyString(), anyString(), any())).thenReturn("staging_path");
    final var testMessages = generateTestMessages();
    final JsonNode config = Jsons.deserialize(MoreResources.readResource("insert_config.json"), JsonNode.class);
    final AirbyteMessageConsumer airbyteMessageConsumer = new StagingConsumerFactory()
        .create(Destination::defaultOutputRecordCollector, mockDb,
            sqlOperations, new SnowflakeSQLNameTransformer(), config, getCatalog());
    doThrow(SQLException.class).when(sqlOperations).copyIntoTmpTableFromStage(any(), anyString(), anyString(), anyString());

    airbyteMessageConsumer.start();
    for (final AirbyteMessage m : testMessages) {
      airbyteMessageConsumer.accept(m);
    }
    assertThrows(RuntimeException.class, airbyteMessageConsumer::close);

    verify(sqlOperations, times(1)).cleanUpStage(any(), anyString());
  }

  @ParameterizedTest
  @MethodSource("destinationTypeToConfig")
  public void testS3ConfigType(String configFileName, DestinationType expectedDestinationType) throws Exception {
    final JsonNode config = Jsons.deserialize(MoreResources.readResource(configFileName), JsonNode.class);
    DestinationType typeFromConfig = SnowflakeDestinationResolver.getTypeFromConfig(config);
    assertEquals(expectedDestinationType, typeFromConfig);
  }

  private static Stream<Arguments> destinationTypeToConfig() {
    return Stream.of(
        arguments("copy_gcs_config.json", DestinationType.COPY_GCS),
        arguments("copy_s3_config.json", DestinationType.COPY_S3),
        arguments("insert_config.json", DestinationType.INTERNAL_STAGING));
  }

  private List<AirbyteMessage> generateTestMessages() {
    return IntStream.range(0, 3)
        .boxed()
        .map(i -> new AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream("test")
                .withNamespace("test_staging")
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "human " + i)))))
        .collect(Collectors.toList());
  }

  ConfiguredAirbyteCatalog getCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createConfiguredAirbyteStream(
            "test",
            "test_staging",
            Field.of("id", JsonSchemaType.NUMBER),
            Field.of("name", JsonSchemaType.STRING))
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));
  }

}
