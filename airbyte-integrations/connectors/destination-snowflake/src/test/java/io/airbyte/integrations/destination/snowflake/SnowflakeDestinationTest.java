/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.params.provider.Arguments.arguments;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.integrations.destination.snowflake.SnowflakeDestination.DestinationType;
import io.airbyte.integrations.destination_async.AsyncStreamConsumer;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;

import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.junit.jupiter.params.provider.MethodSource;

public class SnowflakeDestinationTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  private static Stream<Arguments> urlsDataProvider() {
    return Stream.of(
        // See https://docs.snowflake.com/en/user-guide/admin-account-identifier for specific requirements
        // "Account name in organization" style
        arguments("https://acme-marketing-test-account.snowflakecomputing.com", true),
        arguments("https://acme-marketing_test_account.snowflakecomputing.com", true),
        arguments("https://acme-marketing.test-account.snowflakecomputing.com", true),

        // Legacy style (account locator in a region)
        // Some examples taken from
        // https://docs.snowflake.com/en/user-guide/admin-account-identifier#non-vps-account-locator-formats-by-cloud-platform-and-region
        arguments("xy12345.snowflakecomputing.com", true),
        arguments("xy12345.us-gov-west-1.aws.snowflakecomputing.com", true),
        arguments("xy12345.us-east-1.aws.snowflakecomputing.com", true),
        // And some other formats which are, de facto, valid
        arguments("xy12345.foo.us-west-2.aws.snowflakecomputing.com", true),
        arguments("https://xy12345.snowflakecomputing.com", true),
        arguments("https://xy12345.us-east-1.snowflakecomputing.com", true),
        arguments("https://xy12345.us-east-1.aws.snowflakecomputing.com", true),
        arguments("https://xy12345.foo.us-west-2.aws.snowflakecomputing.com", true),

        // Invalid formats
        arguments("example.snowflakecomputing.com/path/to/resource", false),
        arguments("example.snowflakecomputing.com:8080", false),
        arguments("example.snowflakecomputing.com:12345", false),
        arguments("example.snowflakecomputing.com//path/to/resource", false),
        arguments("example.snowflakecomputing.com/path?query=string", false),
        arguments("example.snowflakecomputing.com/#fragment", false),
        arguments("ab12345.us-east-2.aws.snowflakecomputing. com", false),
        arguments("ab12345.us-east-2.aws.snowflakecomputing..com", false));
  }

  @ParameterizedTest
  @MethodSource({"urlsDataProvider"})
  void testUrlPattern(final String url, final boolean isMatch) throws Exception {
    final ConnectorSpecification spec = new SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS).spec();
    final Pattern pattern = Pattern.compile(spec.getConnectionSpecification().get("properties").get("host").get("pattern").asText());

    final Matcher matcher = pattern.matcher(url);
    assertEquals(isMatch, matcher.find());
  }

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

  @ParameterizedTest
  @MethodSource("destinationTypeToConfig")
  public void testS3ConfigType(final String configFileName, final DestinationType expectedDestinationType) throws Exception {
    final JsonNode config = Jsons.deserialize(MoreResources.readResource(configFileName), JsonNode.class);
    final DestinationType typeFromConfig = SnowflakeDestinationResolver.getTypeFromConfig(config);
    assertEquals(expectedDestinationType, typeFromConfig);
  }

  private static Stream<Arguments> destinationTypeToConfig() {
    return Stream.of(
        arguments("copy_gcs_config.json", DestinationType.COPY_GCS),
        arguments("copy_s3_config.json", DestinationType.COPY_S3),
        arguments("insert_config.json", DestinationType.INTERNAL_STAGING));
  }

  @Test
  void testWriteSnowflakeInternal() throws Exception {
    final JsonNode config = Jsons.deserialize(MoreResources.readResource("internal_staging_config.json"), JsonNode.class);
    final SerializedAirbyteMessageConsumer consumer = new SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS)
        .getSerializedMessageConsumer(config, new ConfiguredAirbyteCatalog(), null);
    assertEquals(AsyncStreamConsumer.class, consumer.getClass());
  }

  static class TestEnableAsyncArgumentsProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(ExtensionContext context) throws Exception {
      final var mapper = new ObjectMapper();
      final var standard = mapper.createObjectNode();
      final var internalStagingSpace = mapper.createObjectNode();
      final var internalStagingSpaceCapital = mapper.createObjectNode();
      final var internalStagingDash = mapper.createObjectNode();
      final var internalStagingUnderscore = mapper.createObjectNode();
      final var noLoadingMethod = mapper.createObjectNode();
      standard.put("loading_method", mapper.createObjectNode().put("method", "standard"));
      internalStagingSpace.put("loading_method", mapper.createObjectNode().put("method", "internal staging"));
      internalStagingSpaceCapital.put("loading_method", mapper.createObjectNode().put("method", "INTERNAL STAGING"));
      internalStagingDash.put("loading_method", mapper.createObjectNode().put("method", "internal-staging"));
      internalStagingUnderscore.put("loading_method", mapper.createObjectNode().put("method", "internal_staging"));
      noLoadingMethod.put("loading_method", "standard");

      return Stream.of(
              Arguments.of(standard, true),
              Arguments.of(internalStagingSpace, true),
              Arguments.of(internalStagingSpaceCapital, true),
              Arguments.of(internalStagingDash, true),
              Arguments.of(internalStagingUnderscore, true),
              Arguments.of(mapper.createObjectNode(), false),
              Arguments.of(noLoadingMethod, false)
      );
    }
  }


  @ParameterizedTest
  @ArgumentsSource(TestEnableAsyncArgumentsProvider.class)
  public void testEnableAsync(final JsonNode config, boolean expected) {
    final var actual = SnowflakeDestination.useAsyncSnowflake(config);
    Assertions.assertEquals(expected, actual);
  }


}
