/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.commons.temporal.exception.RetryableException;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.helper.ConnectionHelper;
import io.airbyte.workers.temporal.scheduling.activities.ConnectionDeletionActivity.ConnectionDeletionInput;
import java.io.IOException;
import java.util.UUID;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ConnectionDeletionActivityTest {

  @Mock
  private ConnectionHelper mConnectionHelper;

  @InjectMocks
  private ConnectionDeletionActivityImpl connectionDeletionActivity;

  private final ConnectionDeletionInput input = new ConnectionDeletionInput(UUID.randomUUID());

  @Test
  @DisplayName("Test that the proper helper method is called")
  void testSuccess() throws JsonValidationException, ConfigNotFoundException, IOException {
    connectionDeletionActivity.deleteConnection(input);

    Mockito.verify(mConnectionHelper).deleteConnection(input.getConnectionId());
  }

  @Test
  @DisplayName("Test that exception are properly wrapped")
  void testWrapException() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.doThrow(new JsonValidationException(""), new ConfigNotFoundException("", ""), new IOException())
        .when(mConnectionHelper).deleteConnection(input.getConnectionId());

    Assertions.assertThatThrownBy(() -> connectionDeletionActivity.deleteConnection(input))
        .isInstanceOf(RetryableException.class)
        .hasCauseInstanceOf(JsonValidationException.class);

    Assertions.assertThatThrownBy(() -> connectionDeletionActivity.deleteConnection(input))
        .isInstanceOf(RetryableException.class)
        .hasCauseInstanceOf(ConfigNotFoundException.class);

    Assertions.assertThatThrownBy(() -> connectionDeletionActivity.deleteConnection(input))
        .isInstanceOf(RetryableException.class)
        .hasCauseInstanceOf(IOException.class);

  }

}
