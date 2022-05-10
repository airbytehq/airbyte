/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class RecordSchemaValidatorTest {

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
    final RecordSchemaValidator recordSchemaValidator = new RecordSchemaValidator(WorkerUtils.mapStreamNamesToSchemas(syncInput));
    recordSchemaValidator.validateSchema(VALID_RECORD.getRecord());
  }

  @Test
  void testValidateInvalidSchema() throws Exception {
    final RecordSchemaValidator recordSchemaValidator = new RecordSchemaValidator(WorkerUtils.mapStreamNamesToSchemas(syncInput));
    assertThrows(RecordSchemaValidationException.class, () -> recordSchemaValidator.validateSchema(INVALID_RECORD.getRecord()));
  }

}
