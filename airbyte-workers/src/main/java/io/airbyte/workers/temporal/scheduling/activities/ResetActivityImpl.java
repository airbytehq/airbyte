/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.StreamDescriptor;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.workers.temporal.exception.RetryableException;
import io.airbyte.workers.temporal.scheduling.activities.ResetActivity.GetResetsOutput;
import java.util.List;
import java.util.UUID;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class ResetActivityImpl implements ResetActivity {

  private StreamResetPersistence streamResetPersistence;

  @Override
  public GetResetsOutput getStreamResets(final UUID connectionId) {
    try {
      return new GetResetsOutput(streamResetPersistence.getStreamResets(connectionId));
    } catch (final Exception e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void createStreamResets(final UUID connectionId, final List<StreamDescriptor> streamDescriptorList) {
    try {
      streamResetPersistence.createStreamResets(connectionId, streamDescriptorList);
    } catch (final Exception e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void deleteStreamResets(final UUID connectionId, final List<StreamDescriptor> streamDescriptorList) {
    try {
      streamResetPersistence.deleteStreamResets(connectionId, streamDescriptorList);
    } catch (final Exception e) {
      throw new RetryableException(e);
    }
  }

}
