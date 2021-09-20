/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.config.persistence.split_secrets;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.config.persistence.split_secrets.test_cases.ArrayTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.NestedObjectTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.OneOfTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.OptionalPasswordTestCase;
import io.airbyte.config.persistence.split_secrets.test_cases.SimpleTestCase;
import java.util.List;
import java.util.UUID;
import java.util.regex.Pattern;
import java.util.stream.Stream;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

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

  private static Stream<Arguments> provideTestCases() {
    return Stream.of(
        new OptionalPasswordTestCase(),
        new SimpleTestCase(),
        new NestedObjectTestCase(),
        new OneOfTestCase(),
        new ArrayTestCase()
    // new ArrayOneOfTestCase() todo: support this test case
    ).map(Arguments::of);
  }

  @ParameterizedTest
  @MethodSource("provideTestCases")
  void testSplit(SecretsTestCase testCase) {
    final var uuidIterator = UUIDS.iterator();
    final var splitConfig = SecretsHelpers.split(
        uuidIterator::next,
        WORKSPACE_ID,
        testCase.getFullConfig(),
        testCase.getSpec());

    assertEquals(testCase.getPartialConfig(), splitConfig.getPartialConfig());
    assertEquals(testCase.getFirstSecretMap(), splitConfig.getCoordinateToPayload());

    // check that keys for Google Secrets Manger fit the requirements:
    // A secret ID is a string with a maximum length of 255 characters and can contain
    // uppercase and lowercase letters, numerals, and the hyphen (-) and underscore (_) characters.
    // https://cloud.google.com/secret-manager/docs/reference/rpc/google.cloud.secretmanager.v1#createsecretrequest
    final var gsmKeyCharacterPattern = Pattern.compile("^[a-zA-Z0-9_-]+$");

    // sanity check pattern with a character that isn't allowed
    assertFalse(gsmKeyCharacterPattern.matcher("/").matches());

    // check every key for the pattern and max length
    splitConfig.getCoordinateToPayload().keySet().forEach(key -> {
      assertTrue(gsmKeyCharacterPattern.matcher(key.toString()).matches(), "Invalid character in key: " + key);
      assertTrue(key.toString().length() <= 255, "Key is too long: " + key.toString().length());
    });
  }

  @ParameterizedTest
  @MethodSource("provideTestCases")
  void testSplitUpdate(SecretsTestCase testCase) {
    final var uuidIterator = UUIDS.iterator();
    final var secretPersistence = new MemorySecretPersistence();
    final var updatedSplit = SecretsHelpers.splitUpdate(
        uuidIterator::next,
        WORKSPACE_ID,
        testCase.getPartialConfig(),
        testCase.getFullConfig(),
        testCase.getSpec(),
        secretPersistence::read);

    assertEquals(testCase.getUpdatedPartialConfig(), updatedSplit.getPartialConfig());
    assertEquals(testCase.getSecondSecretMap(), updatedSplit.getCoordinateToPayload());
  }

  @ParameterizedTest
  @MethodSource("provideTestCases")
  void testCombine(SecretsTestCase testCase) {
    final var secretPersistence = new MemorySecretPersistence();
    testCase.getPersistenceUpdater().accept(secretPersistence);

    final var actualCombinedConfig = SecretsHelpers.combine(testCase.getPartialConfig(), secretPersistence);

    assertEquals(testCase.getFullConfig(), actualCombinedConfig);
  }

  @Test
  void testMissingSecretShouldThrowException() {
    // todo: test case where it can't find secret -> should throw exception
  }

  @Test
  void testUpdatingSecretsOneAtATime() {
    final var uuidIterator = UUIDS.iterator();
    final var secretPersistence = new MemorySecretPersistence();
    final var testCase = new NestedObjectTestCase();

    final var splitConfig = SecretsHelpers.split(
            uuidIterator::next,
            WORKSPACE_ID,
            testCase.getFullConfig(),
            testCase.getSpec());

    assertEquals(testCase.getPartialConfig(), splitConfig.getPartialConfig());
    assertEquals(testCase.getFirstSecretMap(), splitConfig.getCoordinateToPayload());

    final var updatedSplit1 = SecretsHelpers.splitUpdate(
            uuidIterator::next,
            WORKSPACE_ID,
            testCase.getPartialConfig(),
            testCase.getFullConfigUpdate1(),
            testCase.getSpec(),
            secretPersistence::read);

    assertEquals(testCase.getUpdatedPartialConfigAfterUpdate1(), updatedSplit1.getPartialConfig());
    assertEquals(testCase.getSecretMapAfterUpdate1(), updatedSplit1.getCoordinateToPayload());

    final var updatedSplit2 = SecretsHelpers.splitUpdate(
            uuidIterator::next,
            WORKSPACE_ID,
            updatedSplit1.getPartialConfig(),
            testCase.getFullConfigUpdate2(),
            testCase.getSpec(),
            secretPersistence::read);

    assertEquals(testCase.getUpdatedPartialConfigAfterUpdate2(), updatedSplit2.getPartialConfig());
    assertEquals(testCase.getSecretMapAfterUpdate2(), updatedSplit2.getCoordinateToPayload());

  }

}
