/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import static org.junit.Assert.assertEquals;

import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import io.airbyte.workers.test_utils.TestConfigHelpers;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
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
  private ConcurrentHashMap<AirbyteStreamNameNamespacePair, ImmutablePair<Set<String>, Integer>> validationErrors;

  @BeforeEach
  void setup() throws Exception {
    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    syncInput = syncPair.getValue();
    validationErrors = new ConcurrentHashMap<>();
  }

  @Test
  void testValidateValidSchema() {
    final var recordSchemaValidator = new RecordSchemaValidator(WorkerUtils.mapStreamNamesToSchemas(syncInput), false);
    for (var i = 0; i < 10; i++) {
      recordSchemaValidator.validateSchema(
          VALID_RECORD.getRecord(), AirbyteStreamNameNamespacePair.fromRecordMessage(VALID_RECORD.getRecord()),
          validationErrors);
    }
    assertEquals(0, validationErrors.size());
  }

  @Test
  void testValidateInvalidSchema() {
    final var recordSchemaValidator = new RecordSchemaValidator(WorkerUtils.mapStreamNamesToSchemas(syncInput), false);
    recordSchemaValidator.validateSchema(
        INVALID_RECORD.getRecord(),
        AirbyteStreamNameNamespacePair.fromRecordMessage(INVALID_RECORD.getRecord()),
        validationErrors);
    assertEquals(1, validationErrors.size());
  }

  @Test
  void testValidateValidSchemaWithBackgroundValidation() {
    final var recordSchemaValidator = new RecordSchemaValidator(WorkerUtils.mapStreamNamesToSchemas(syncInput), true);
    for (var i = 0; i < 10; i++) {
      recordSchemaValidator.validateSchema(VALID_RECORD.getRecord(), AirbyteStreamNameNamespacePair.fromRecordMessage(VALID_RECORD.getRecord()),
          validationErrors);
    }
    assertEquals(0, validationErrors.size());
  }

  @Test
  void testValidateInvalidSchemaWithBackgroundValidation() throws InterruptedException {
    final var executorService = Executors.newFixedThreadPool(1);
    final var recordSchemaValidator = new RecordSchemaValidator(WorkerUtils.mapStreamNamesToSchemas(syncInput), true, executorService);

    recordSchemaValidator.validateSchema(
        INVALID_RECORD.getRecord(),
        AirbyteStreamNameNamespacePair.fromRecordMessage(INVALID_RECORD.getRecord()),
        validationErrors);
    executorService.awaitTermination(3, TimeUnit.SECONDS);
    assertEquals(1, validationErrors.size());
  }

}
