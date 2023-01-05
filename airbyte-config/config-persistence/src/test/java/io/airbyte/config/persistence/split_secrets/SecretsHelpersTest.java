/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.persistence.split_secrets.test_cases.ArrayOneOfTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.ArrayTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.NestedObjectTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.NestedOneOfTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.OneOfSecretTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.OneOfTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.OptionalPasswordTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.PostgresSshKeyTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.SimpleTestCase;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.regex.Pattern;
import java.util.stream.Stream;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

@SuppressWarnings({"PMD.JUnit5TestShouldBePackagePrivate", "PMD.UnusedPrivateMethod"})
public class SecretsHelpersTest {

  public static final UUID WORKSPACE_ID = UUID.fromString("e0eb0554-ffe0-4e9c-9dc0-ed7f52023eb2");

  // use a fixed sequence of UUIDs so it's easier to have static files for the test cases
  public static final List<UUID> UUIDS = List.of(
      UUID.fromString("9eba44d8-51e7-48f1-bde2-619af0e42c22"),
      UUID.fromString("2c2ef2b3-259a-4e73-96d1-f56dacee2e5e"),
      UUID.fromString("1206db5b-b968-4df1-9a76-f3fcdae7e307"),
      UUID.fromString("c03ef566-79a7-4e77-b6f3-d23d2528f25a"),
      UUID.fromString("35f08b15-bfd9-44fe-a8c7-5aa9e156c0f5"),
      UUID.fromString("159c0b6f-f9ae-48b4-b7f3-bcac4ba15743"),
      UUID.fromString("71af9b74-4e61-4cff-830e-3bf1ec18fbc0"),
      UUID.fromString("067a62fc-d007-44dd-a8f6-0fd10823713d"),
      UUID.fromString("c4967ac9-0856-4733-a21e-1d51ca8f254d"));

  private static final String PROVIDE_TEST_CASES = "provideTestCases";

  /**
   * This is a bit of a non-standard way of specifying test case paramaterization for Junit, but it's
   * intended to let you treat most of the JSON involved in the tests as static files.
   */
  private static Stream<Arguments> provideTestCases() {
    return Stream.of(
        new OptionalPasswordTestCase(),
        new SimpleTestCase(),
        new NestedObjectTestCase(),
        new OneOfTestCase(),
        new OneOfSecretTestCase(),
        new ArrayTestCase(),
        new ArrayOneOfTestCase(),
        new NestedOneOfTestCase(),
        new PostgresSshKeyTestCase()).map(Arguments::of);
  }

  @ParameterizedTest
  @MethodSource(PROVIDE_TEST_CASES)
  @SuppressWarnings({"PMD.JUnitTestsShouldIncludeAssert"})
  public void validateTestCases(final SecretsTestCase testCase) throws JsonValidationException {
    final var validator = new JsonSchemaValidator();
    final var spec = testCase.getSpec().getConnectionSpecification();
    validator.ensure(spec, testCase.getFullConfig());
    validator.ensure(spec, testCase.getUpdateConfig());
  }

  @ParameterizedTest
  @MethodSource(PROVIDE_TEST_CASES)
  void testSplit(final SecretsTestCase testCase) {
    final var uuidIterator = UUIDS.iterator();
    final var inputConfig = testCase.getFullConfig();
    final var inputConfigCopy = inputConfig.deepCopy();
    final var splitConfig = SecretsHelpers.splitConfig(
        uuidIterator::next,
        WORKSPACE_ID,
        inputConfig,
        testCase.getSpec().getConnectionSpecification());

    assertEquals(testCase.getPartialConfig(), splitConfig.getPartialConfig());
    assertEquals(testCase.getFirstSecretMap(), splitConfig.getCoordinateToPayload());

    // check that we didn't mutate the input configs
    assertEquals(inputConfigCopy, inputConfig);

    // check that keys for Google Secrets Manger fit the requirements:
    // A secret ID is a string with a maximum length of 255 characters and can contain
    // uppercase and lowercase letters, numerals, and the hyphen (-) and underscore (_) characters.
    // https://cloud.google.com/secret-manager/docs/reference/rpc/google.cloud.secretmanager.v1#createsecretrequest
    final var gsmKeyCharacterPattern = Pattern.compile("^[a-zA-Z0-9_-]+$");

    // sanity check pattern with a character that isn't allowed
    assertFalse(gsmKeyCharacterPattern.matcher("/").matches());

    // check every key for the pattern and max length
    splitConfig.getCoordinateToPayload().keySet().forEach(key -> {
      assertTrue(gsmKeyCharacterPattern.matcher(key.getFullCoordinate()).matches(), "Invalid character in key: " + key);
      assertTrue(key.toString().length() <= 255, "Key is too long: " + key.toString().length());
    });
  }

  @ParameterizedTest
  @MethodSource(PROVIDE_TEST_CASES)
  void testSplitUpdate(final SecretsTestCase testCase) {
    final var uuidIterator = UUIDS.iterator();
    final var inputPartialConfig = testCase.getPartialConfig();
    final var inputUpdateConfig = testCase.getUpdateConfig();
    final var inputPartialConfigCopy = inputPartialConfig.deepCopy();
    final var inputUpdateConfigCopy = inputUpdateConfig.deepCopy();
    final var secretPersistence = new MemorySecretPersistence();

    for (final Map.Entry<SecretCoordinate, String> entry : testCase.getFirstSecretMap().entrySet()) {
      secretPersistence.write(entry.getKey(), entry.getValue());
    }

    final var updatedSplit = SecretsHelpers.splitAndUpdateConfig(
        uuidIterator::next,
        WORKSPACE_ID,
        inputPartialConfig,
        inputUpdateConfig,
        testCase.getSpec().getConnectionSpecification(),
        secretPersistence::read);

    assertEquals(testCase.getUpdatedPartialConfig(), updatedSplit.getPartialConfig());
    assertEquals(testCase.getSecondSecretMap(), updatedSplit.getCoordinateToPayload());

    // check that we didn't mutate the input configs
    assertEquals(inputPartialConfigCopy, inputPartialConfig);
    assertEquals(inputUpdateConfigCopy, inputUpdateConfig);
  }

  @ParameterizedTest
  @MethodSource(PROVIDE_TEST_CASES)
  void testCombine(final SecretsTestCase testCase) {
    final var secretPersistence = new MemorySecretPersistence();
    testCase.getPersistenceUpdater().accept(secretPersistence);

    final var inputPartialConfig = testCase.getPartialConfig();
    final var inputPartialConfigCopy = inputPartialConfig.deepCopy();
    final var actualCombinedConfig = SecretsHelpers.combineConfig(testCase.getPartialConfig(), secretPersistence);

    assertEquals(testCase.getFullConfig(), actualCombinedConfig);

    // check that we didn't mutate the input configs
    assertEquals(inputPartialConfigCopy, inputPartialConfig);
  }

  @Test
  void testMissingSecretShouldThrowException() {
    final var testCase = new SimpleTestCase();
    final var secretPersistence = new MemorySecretPersistence();

    // intentionally do not seed the persistence with
    // testCase.getPersistenceUpdater().accept(secretPersistence);

    assertThrows(RuntimeException.class, () -> SecretsHelpers.combineConfig(testCase.getPartialConfig(), secretPersistence));
  }

  @Test
  void testUpdatingSecretsOneAtATime() {
    final var uuidIterator = UUIDS.iterator();
    final var secretPersistence = new MemorySecretPersistence();
    final var testCase = new NestedObjectTestCase();

    final var splitConfig = SecretsHelpers.splitConfig(
        uuidIterator::next,
        WORKSPACE_ID,
        testCase.getFullConfig(),
        testCase.getSpec().getConnectionSpecification());

    assertEquals(testCase.getPartialConfig(), splitConfig.getPartialConfig());
    assertEquals(testCase.getFirstSecretMap(), splitConfig.getCoordinateToPayload());

    for (final Map.Entry<SecretCoordinate, String> entry : splitConfig.getCoordinateToPayload().entrySet()) {
      secretPersistence.write(entry.getKey(), entry.getValue());
    }

    final var updatedSplit1 = SecretsHelpers.splitAndUpdateConfig(
        uuidIterator::next,
        WORKSPACE_ID,
        testCase.getPartialConfig(),
        testCase.getFullConfigUpdate1(),
        testCase.getSpec().getConnectionSpecification(),
        secretPersistence::read);

    assertEquals(testCase.getUpdatedPartialConfigAfterUpdate1(), updatedSplit1.getPartialConfig());
    assertEquals(testCase.getSecretMapAfterUpdate1(), updatedSplit1.getCoordinateToPayload());

    for (final Map.Entry<SecretCoordinate, String> entry : updatedSplit1.getCoordinateToPayload().entrySet()) {
      secretPersistence.write(entry.getKey(), entry.getValue());
    }

    final var updatedSplit2 = SecretsHelpers.splitAndUpdateConfig(
        uuidIterator::next,
        WORKSPACE_ID,
        updatedSplit1.getPartialConfig(),
        testCase.getFullConfigUpdate2(),
        testCase.getSpec().getConnectionSpecification(),
        secretPersistence::read);

    assertEquals(testCase.getUpdatedPartialConfigAfterUpdate2(), updatedSplit2.getPartialConfig());
    assertEquals(testCase.getSecretMapAfterUpdate2(), updatedSplit2.getCoordinateToPayload());
  }

  @ParameterizedTest
  @MethodSource(PROVIDE_TEST_CASES)
  void testSecretPath(final SecretsTestCase testCase) throws IOException {
    final JsonNode spec = testCase.getSpec().getConnectionSpecification();

    final List<String> secretsPaths = SecretsHelpers.getSortedSecretPaths(spec);

    Assertions.assertThat(secretsPaths).containsExactlyElementsOf(testCase.getExpectedSecretsPaths());
  }

}
