/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.featureflag.TestClient;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.workers.exception.RecordSchemaValidationException;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import io.airbyte.workers.test_utils.TestConfigHelpers;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class RecordSchemaValidatorTest {

  private StandardSyncInput syncInput;
  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";
  private static final AirbyteMessage VALID_RECORD = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue");
  private static final AirbyteMessage INVALID_RECORD = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, 3);

  @BeforeEach
  void setup() throws Exception {
    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    syncInput = syncPair.getValue();
  }

  @Test
  void testValidateValidSchema() throws Exception {
    final var featureFlagClient = new TestClient();
    final var recordSchemaValidator = new RecordSchemaValidator(featureFlagClient, syncInput.getWorkspaceId(),
        WorkerUtils.mapStreamNamesToSchemas(syncInput));
    recordSchemaValidator.validateSchema(VALID_RECORD.getRecord(), AirbyteStreamNameNamespacePair.fromRecordMessage(VALID_RECORD.getRecord()));
  }

  @Test
  void testValidateInvalidSchema() throws Exception {
    final var featureFlagClient = new TestClient();
    final RecordSchemaValidator recordSchemaValidator = new RecordSchemaValidator(featureFlagClient, syncInput.getWorkspaceId(),
        WorkerUtils.mapStreamNamesToSchemas(syncInput));
    assertThrows(RecordSchemaValidationException.class, () -> recordSchemaValidator.validateSchema(INVALID_RECORD.getRecord(),
        AirbyteStreamNameNamespacePair.fromRecordMessage(INVALID_RECORD.getRecord())));
  }

}
